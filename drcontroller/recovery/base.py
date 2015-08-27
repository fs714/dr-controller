import logging

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

logger = logging.getLogger("RecoveryHandler:start")

class AnsibleTask(Task):
    def __init__(self, name, host_list, module_name, module_args, pattern='*', inject=None):
        super(AnsibleTask, self).__init__(name, inject=inject, provides=name) #provides send out the results to engine.storage
        self.name = name
        self.runner = Runner(
                      host_list = host_list,
                      pattern = pattern,
                      module_name = module_name,
                      module_args = module_args)

    def add_result_handler(self, result_handler):
        self.result_handler = result_handler

    def execute(self):
	print 'Executing Task "%s"' % self.name
	logger.info('Executing Task "%s"' % self.name)
        result = self.runner.run()
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
