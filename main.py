from decorators import sim_client
from log_utils import logger
from monitor import building_status_monitor
from sim_request import SimClient
from utils.api_utils import get_my_company


@sim_client
async def main(simclient: SimClient = None):
    my_company = await get_my_company(simclient=simclient)
    await building_status_monitor(my_company, simclient=simclient)


if __name__ == "__main__":
    import asyncio
    import sys

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("退出监控")
        sys.exit(0)
