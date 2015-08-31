#!/usr/bin/env python2.7
import sys
sys.path.append('../recovery')
from recovery_handler import RecoveryHandler
from taskflow import engines

if __name__ == '__main__':
    #t = GlanceHandler()
    #flow = t.prepare()
    #eng = engines.load(flow)
    #eng.run()
    recovery = RecoveryHandler()
    recovery.start()
