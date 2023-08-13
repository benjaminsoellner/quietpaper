import asyncio
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from quietpaper import logger

class MerossConnection:

    def __init__(self, meross_email, meross_password):
        self.manager = None
        self.meross_email = meross_email
        self.meross_password = meross_password
        self.event_loop = asyncio.get_event_loop()
        self.http_api_client = None
        self.manager = None
    
    async def _async_disconnect(self):
        try:
            self.manager.close()
            await self.http_api_client.async_logout()
        except Exception as ee:
            logger.warning("Error terminating Meross Connection: " + (ee.message if hasattr(ee, 'message') else type(ee).__name__))
        self.manager = None
        self.http_api_client = None
    
    async def _async_connect(self):
        try:
            self.http_api_client = await MerossHttpClient.async_from_user_password(email=self.meross_email, password=self.meross_password)
            self.manager = MerossManager(http_client=self.http_api_client)
            await self.manager.async_init()
            await self.manager.async_device_discovery()    
        except Exception as ee:
            logger.warning("Error initializing Meross Connection: " + (ee.message if hasattr(ee, 'message') else type(ee).__name__))
            self.http_api_client = None
            self.manager = None
    
    async def _async_get_power_of_plug(self, plug_name):
        if self.manager is None or self.http_api_client is None:
            await self._async_disconnect()
            await self._async_connect()
        try:
            plugs = self.manager.find_devices(device_name=plug_name)
            await plugs[0].async_update()
            return (await plugs[0].async_get_instant_metrics()).power
        except Exception as ee:
            logger.warning("Error querying power of plug '" + plug_name + "'. Resetting connection to Meross. " + (ee.message if hasattr(ee, 'message') else type(ee).__name__))
            plugs = []
            await self._async_disconnect()
            await self._async_connect()
    
    def connect(self):
        self.event_loop.run_until_complete(self._async_connect())

    def disconnect(self):
        self.event_loop.run_until_complete(self._async_disconnect())
    
    def get_power_of_plug(self, plug_name):
        return self.event_loop.run_until_complete(self._async_get_power_of_plug(plug_name))
