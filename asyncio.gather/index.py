import asyncio
from pprint import pprint

import random


async def coro(tag):
    print(">", tag)
    await asyncio.sleep(random.uniform(1, 3))
    print("<", tag)
    return tag


loop = asyncio.get_event_loop()

group1 = asyncio.gather(*[coro("group A.{}".format(i)) for i in range(1, 6)])
group2 = asyncio.gather(*[coro("group B.{}".format(i)) for i in range(1, 4)])
group3 = asyncio.gather(*[coro("group C.{}".format(i)) for i in range(1, 10)])

all_groups = asyncio.gather(group1, group2, group3)

results = loop.run_until_complete(all_groups)

loop.close()

