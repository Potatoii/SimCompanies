from bot import building_status_monitor
from log_utils import logger


async def main():
    logger.info("开始监控建筑状态")
    await building_status_monitor()


if __name__ == "__main__":
    import asyncio
    import sys

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("退出监控")
        sys.exit(0)
