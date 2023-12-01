from bot import building_status_monitor
from log_utils import logger
from setup import setup


async def main():
    await setup()
    logger.info("开始监控建筑状态")
    await building_status_monitor()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
