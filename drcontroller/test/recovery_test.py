#!/usr/bin/env python2.7
import os
import sys
from taskflow import engines

root_path = os.path.abspath(os.path.dirname(sys.argv[0]))
project_root = root_path.replace('/test', '')
sys.path.append(project_root)
from recovery.recovery_handler import RecoveryHandler

if __name__ == '__main__':
    #t = GlanceHandler()
    #flow = t.prepare()
    #eng = engines.load(flow)
    #eng.run()
    recovery = RecoveryHandler()
    recovery.start()
