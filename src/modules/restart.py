from _kisb import KISB
import logging, asyncio
from modules.dataManager._manager import DataManager as DM

async def restart(bot:KISB):
    await bot.unload_extension("bot")
    logging.debug("All Services Stopped - Waiting 5 seconds and cleaning up any locks...")
    DM.lock(False)
    await asyncio.sleep(5)
    logging.debug("Starting Services...")
    await bot.load_extension("bot")