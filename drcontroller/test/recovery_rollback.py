import logging
import os
import hashlib
from functools import wraps
from taskflow import engines

import sys
sys.path.append('../recovery')
from base import AnsibleTask, ShellTask, LinearFlowCreator, UnorderedFlowCreator

sys.path.append("../db")
from db_Dao import DRGlanceDao, DRNovaDao

def task_list(fn):
    @wraps(fn)
    def wrapper(self, tasks, *args, **kwargs):
        task = fn(self, *args, **kwargs)
        task.add_result_handler(self.result_handler)
        tasks.append(task)
    return wrapper

class RollbackHandler(object):
    def __init__(self):
        self.logger = logging.getLogger("RecoveryHandler")
        self.logger.info('Init RecoveryHandler')
        result_handler = ResultHandler()
        self.glance_handler = GlanceHandler(result_handler)
        self.nova_handler = NovaHandler(result_handler)

    def start(self, *req, **kwargs):
        self.logger = logging.getLogger("RecoveryHandler:start")

        self.logger.info("--- Hello Recovery ---")
        flow = self.prepare()
        eng = engines.load(flow)
        eng.run()
        results = eng.storage.fetch_all()
        print results
        return ['Hello Recovery']

    def prepare(self):
        flows = [self.glance_handler.prepare(), self.nova_handler.prepare()]
        flow = UnorderedFlowCreator().create('restore', flows)
        return LinearFlowCreator().create('DR_restore', [self.nova_handler.stop_vm_task[0], flow] + self.glance_handler.drbd_tasks)

class RecoveryError(Exception):
    pass

class ResultHandler(object):
    def __init__(self):
        pass

    def analyze(self, name, result):
        for host in result['dark']:
            print 'Error in Task "%s": %s' % (name, result['dark'][host]['msg'])
            raise RecoveryError('Error in Task "%s": %s' % (name, result['dark'][host]['msg']))
        for host in result['contacted']:
            self.analyze_result_for_host(name, result['contacted'][host])

    def analyze_result_for_host(self, name, result):
        if 'msg' in result and result['msg'] != '':
            print 'Error in Task "%s": %s' % (name, result['msg'])
            if 'service-start' in name:
                raise RecoveryError('Error in Task "%s": %s' % (name, result['msg']))
        if 'stderr' in result and result['stderr'] != '':
            print 'Error in Task "%s": %s' % (name, result['stderr'])
            if 'role_change' in name and 'State change failed' in result['stderr']:
                raise RecoveryError('Error in Task "%s": %s' % (name, result['stderr']))
        if 'stdout' in result and result['stdout'] != '':
            print 'Output in Task "%s": %s' % (name, result['stdout'])

class ComponentHandler(object):
    def __init__(self, component, hosts, disc, result_handler):
        self.component = component
        self.hosts = hosts
        self.disc = disc
        self.config = None
        self.disc_tasks = []
        self.result_handler = result_handler
        self.restore_tasks =[]

    @task_list
    def create_role_change_task(self):
        drbd = 'openstack' #config
        return ShellTask('%s_role_change' % drbd, self.hosts, 'drbdadm secondary %s' % drbd)

    @task_list
    def create_disconnect_task(self):
        drbd = 'openstack' #config
        return ShellTask('%s_disconnect' % drbd, self.hosts, 'drbdadm disconnect %s' % drbd)

    @task_list
    def create_network_up_task(self):
        return ShellTask('network_neo4_up', self.hosts, 'ifconfig eno4 up')

    @task_list
    def create_connect_task(self):
        drbd = 'openstack' #config
        return ShellTask('%s_connect' % drbd, self.hosts, 'drbdadm -- --discard-my-data connect %s' % drbd)

    @task_list
    def create_restore_backup_task(self):
        return ShellTask('%s_fs_restore' % self.component, self.hosts, 'chdir=/var/lib mv %sbak %s' % (self.component, self.component))

    @task_list
    def create_umount_task(self):
        return AnsibleTask('%s_fs_umount' % self.component, self.hosts, 'mount', 'src=/dev/%s name=/var/lib/%s fstype=xfs state=unmounted' % (self.disc, self.component))

    @task_list
    def create_remove_task(self):
        return ShellTask('%s_fs_remove' % self.component, self.hosts, 'chdir=/var/lib rm -rf %s' % self.component)

    def prepare(self):
        self.create_tasks()
        return self.create_flow()

    def create_tasks(self):
        raise NotImplementedError()

    def create_flow(self):
        raise NotImplementedError()

    def analyze(self):
        raise NotImplementedError()

class GlanceHandler(ComponentHandler):
    def __init__(self, result_handler):
        controllers = ['10.175.150.16'] #config
        super(GlanceHandler, self).__init__('glance', controllers, 'drbd0', result_handler)
        self.db = DRGlanceDao()
        self.drbd_tasks = []

    def create_tasks(self):
        self.create_umount_task(self.disc_tasks)
        self.create_remove_task(self.disc_tasks)
        self.create_restore_backup_task(self.disc_tasks)
        self.create_disconnect_task(self.drbd_tasks)
        self.create_role_change_task(self.drbd_tasks)
        self.create_network_up_task(self.drbd_tasks)
        self.create_connect_task(self.drbd_tasks)

    def create_flow(self):
        return LinearFlowCreator().create('glance_op', self.disc_tasks + self.restore_tasks)

class NovaHandler(ComponentHandler):
    def __init__(self, result_handler):
        nodes = ['10.175.150.16'] #config
        super(NovaHandler, self).__init__('nova', nodes, 'drbd1', result_handler)
        self.db = DRNovaDao()
        self.instance_tasks = {}
        self.base_tasks = {}
        self.stop_vm_task = []
        self.instance_ids = []

    @task_list
    def create_rebase_task(self, host, instance_uuid_local, base_uuid_local):
        return ShellTask('rebase', host, 'chdir=/var/lib/nova/instances/%s qemu-img -u -b /var/lib/nova/instances/_base/%s disk' % (instance_uuid_local, base_uuid_local))

    @task_list
    def create_vm_stop_task(self):
        controllers = ['10.175.150.16'] #config
        return ShellTask('vm_stop', [controllers[0]], 'python /home/eshufan/scripts/nova_stop_vm.py --instance_ids %s' % ','.join(self.instance_ids))

    def create_tasks(self):
        for (instance_uuid_primary, instance_uuid_local, image_uuid_primary, image_uuid_local, host_primary, host_local) in self.db.get_all_uuids_node():#[('', 'f6158ecb-18ca-4295-b3dd-3d7e0f7394d2', '10.175.150.16')]:
            print (instance_uuid_primary, instance_uuid_local, image_uuid_local)
            self.instance_ids.append(instance_uuid_local)
        self.create_vm_stop_task(self.stop_vm_task)
        self.create_umount_task(self.disc_tasks)
        self.create_remove_task(self.disc_tasks)
        self.create_restore_backup_task(self.disc_tasks)

    def create_flow(self):
        return LinearFlowCreator().create('nova_op', self.disc_tasks + self.restore_tasks)

if __name__ == '__main__':
    rollback = RollbackHandler()
    rollback.start()
