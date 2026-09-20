# !/usr/bin/env python
# coding=utf-8
import multiprocessing
import time


def task(iIndex):
    # Obtain the name of current process
    name = multiprocessing.current_process().name
    print(name, ' ..................')
    print('worker ', iIndex)
    time.sleep(1)
    return


if __name__ == '__main__':
    numList = []
    for iIndex in range(5):
        p = multiprocessing.Process(target = task, args = (iIndex,))

        p.start()
        p.join()
        print('Process end.')
