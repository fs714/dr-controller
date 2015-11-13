import logging
import json
from ansible.runner import Runner
from taskflow import engines
from taskflow.patterns import linear_flow, unordered_flow
from taskflow.task import Task


class AnsibleTask(Task):
    def __init__(self, name, host_list, module_name, module_args,
                 pattern='*', inject=None):
        super(AnsibleTask, self).__init__(name, inject=inject, provides=name)
        self.name = name
        self.host_list = host_list
        self.logger = logging.getLogger("AnsibleTask")
        self.runner = Runner(host_list=host_list,
                             pattern=pattern,
                             module_name=module_name,
                             module_args=module_args)

    def execute(self):
        self.logger.info('Executing Task ' + self.name + ':')
        self.logger.debug('\tHosts: ' + ','.join(self.host_list))
        self.logger.debug('\tModule_name: ' + self.runner.module_name)
        self.logger.debug('\tModule_args: ' + self.runner.module_args)
        self.logger.debug('\tPattern: ' + self.runner.pattern)
        result = self.runner.run()
        self.logger.debug('Result of Task ' + self.name + ':')
        self.logger.debug(json.dumps(result, indent=4, sort_keys=True))
        return result


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Main")

    hosts = ['10.175.150.16']
    module_name = 'shell'
    module_args = 'echo "Hello World"'
    pattern = '*'

    linearflow = linear_flow.Flow('Liner_Flow')
    unorderedflow = unordered_flow.Flow('Unordered_Flow')

    for i in range(0, 5):
        linear_task_name = 'Linear_task_' + str(i)
        linear_task = AnsibleTask(linear_task_name, hosts, module_name, module_args, pattern)
        unordered_task_name = 'Unordered_task_' + str(i)
        unordered_task = AnsibleTask(unordered_task_name, hosts, module_name, module_args, pattern)
        linearflow.add(linear_task)
        unorderedflow.add(unordered_task)

    flow = linear_flow.Flow('Final_Flow')
    flow.add(linearflow, unorderedflow)

    eng = engines.load(flow)
    eng.run()
