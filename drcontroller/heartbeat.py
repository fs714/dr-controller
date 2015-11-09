import os
import time


def heartbeat():
    hostname = '10.175.150.15'
    times_to_check = 3
    previous_cnt = times_to_check
    while(1):
        current_cnt = 0
        for i in range(0, times_to_check):
            response = os.system("ping -c 1 -w2 " + hostname
                                 + " > /dev/null 2>&1")
            # response 0 mean ping successfully
            if response == 0:
                current_cnt = current_cnt + 1
            time.sleep(1)

        if current_cnt == 0:
            if previous_cnt > 0:
                print('Primary site is down')
            # else:
            #     print('Primary site is still down')
        if current_cnt == times_to_check:
            if previous_cnt < times_to_check:
                print('Primary site is restored')
            # else:
            #     print('Primary site is OK')

        previous_cnt = current_cnt
