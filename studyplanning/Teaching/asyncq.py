import asyncio

async def producer(q: asyncio.Queue[int]):
    for i in range(3):
        await q.put(i)
    await q.put(-1)  # 用哨兵表示结束

async def consumer(q: asyncio.Queue[int]):
    while True:
        x = await q.get()
        if x == -1:
            break
        print("consume", x)

async def main():
    q = asyncio.Queue()
    await asyncio.gather(producer(q), consumer(q))

asyncio.run(main())