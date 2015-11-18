import logging
import json
from ansible.runner import Runner
from taskflow.patterns import linear_flow, unordered_flow
from taskflow.task import Task

shell_task = Runner(
            host_list=['eselnlx1453'],
            pattern= '*',
            module_name = 'shell',
            module_args='echo "Hello World"')

copy_task = Runner(
            host_list=['eselnlx1277'],
            pattern='*',
            module_name='copy',
            module_args='src=/home/ejjacci/ansible/example.py dest=/home/ejjacci/tmp/example.py')


class AnsibleTask(Task):
    def __init__(self, name, host_list, module_name, module_args, pattern='*', inject=None):
        super(AnsibleTask, self).__init__(name, inject=inject, provides=name) #provides send out the results to engine.storage
        self.name = name
        self.host_list = host_list
        self.logger = logging.getLogger("RecoveryHandler:Base")
        self.runner = Runner(
                      host_list = host_list,
                      pattern = pattern,
                      module_name = module_name,
                      module_args = module_args)

    def add_result_handler(self, result_handler):
        self.result_handler = result_handler

    def execute(self):
        self.logger.info('Executing Task ' +  self.name + ':')
        self.logger.info('\tHosts: ' +  ','.join(self.host_list))
        self.logger.info('\tModule_name: ' + self.runner.module_name)
        self.logger.info('\tModule_args: ' + self.runner.module_args)
        self.logger.info('\tPattern: ' + self.runner.pattern)
        result = self.runner.run()
        # fake_task = Runner(
        #     host_list=['10.175.150.16'],
        #     pattern= '*',
        #     module_name = 'shell',
        #     module_args='echo "Hello World"')
        # result = fake_task.run()
        self.logger.debug('Result of Task ' + self.name + ':')
        self.logger.debug(json.dumps(result, indent=4, sort_keys=True))
        self.result_handler.analyze(self.name, result)
        return result

class ShellTask(AnsibleTask):
    def __init__(self, name, host_list, module_args, pattern='*', inject=None):
        super(ShellTask, self).__init__(name, host_list, 'shell', module_args, pattern, inject)

class FlowCreator(object):
    def create_flow(self, name):
        raise NotImplementedError()

    def create(self, name, tasks):
        ul_flow = self.create_flow(name)
        for task in tasks:
            ul_flow.add(task)
        return ul_flow

class UnorderedFlowCreator(FlowCreator):
    def create_flow(self, name):
        return unordered_flow.Flow(name)

class LinearFlowCreator(FlowCreator):
    def create_flow(self, name):
        return linear_flow.Flow(name)

