import time
import asyncio

now = lambda : time.time()

async def do_some_work(x):
    # 1. 执行 coroutine
    print(now(), ' 1. Waiting: ', x)

    # 2. coroutine 的 return 交给 下一个 callback, 这里跟 JS 不同, js 的 callbabak 没有 return
    return str(now()) + ' Done after {}s'.format(x)

def cCallback(future):
    # 3. 执行 callback
    print(now(), ' 3. Callback: ', future.result())

start = now()

coroutine = do_some_work(100)
loop = asyncio.get_event_loop()

task = asyncio.ensure_future(coroutine)
task.add_done_callback(cCallback)

loop.run_until_complete(task)

print(now(),'TIME: ')