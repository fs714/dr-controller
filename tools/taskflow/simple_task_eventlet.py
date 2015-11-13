import logging
from taskflow import engines
from taskflow.patterns import linear_flow, unordered_flow
from simple_task import AnsibleTask
import eventlet


eventlet.patcher.monkey_patch(all=True)


def func():
    hosts = ['10.175.150.16']
    module_name = 'shell'
    module_args = 'echo "Hello World"'
    pattern = '*'

    linearflow = linear_flow.Flow('Liner_Flow')
    unorderedflow = unordered_flow.Flow('Unordered_Flow')

    for i in range(0, 5):
        linear_task_name = 'Linear_task_' + str(i)
        linear_task = AnsibleTask(linear_task_name, hosts, module_name,
                                  module_args, pattern)
        unordered_task_name = 'Unordered_task_' + str(i)
        unordered_task = AnsibleTask(unordered_task_name, hosts, module_name,
                                     module_args, pattern)
        linearflow.add(linear_task)
        unorderedflow.add(unordered_task)

    flow = linear_flow.Flow('Final_Flow')
    flow.add(linearflow, unorderedflow)

    eng = engines.load(flow)
    eng.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Main")
    pool = eventlet.GreenPool(200)
    for i in xrange(2):
        pool.spawn(func)
    pool.waitall()
