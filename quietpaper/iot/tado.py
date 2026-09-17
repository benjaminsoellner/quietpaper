from quietpaper import logger
import requests
import datetime
import json

class TadoConnection:
    def __init__(self, refresh_token_file, api_ratelimit_minutes=15):
        self.refresh_token_file = refresh_token_file
        self.access_token = None
        self.access_token_expires = None
        self.refresh_token = None
        self.home_id = None
        self.zones_updated_every = api_ratelimit_minutes
        self.zones_last_updated = None
        self.zones_cache = None
    
    def acquire_new_tokens(self):
        with open(self.refresh_token_file, "r") as fd:
            self.refresh_token = json.load(fd)["refresh_token"]
        token = requests.post(
            "https://login.tado.com/oauth2/token",
            params=dict(
                client_id="1bb50063-6b0c-4d11-bd99-387f4a91cc46",
                grant_type="refresh_token",
                refresh_token=self.refresh_token,
            ),
        ).json()
        self.refresh_token = token["refresh_token"]
        self.access_token = token["access_token"]
        self.access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=token["expires_in"])
        with open(self.refresh_token_file, "w") as fd:
            json.dump(token, fd)

    def get_bearer_token(self):
        if self.access_token is None or datetime.datetime.now() > self.access_token_expires:
            self.acquire_new_tokens()
        return self.access_token
    
    def query(self, url):
        try:
            headers = { "Authorization": "Bearer %s" % self.get_bearer_token() }
            response = requests.get(url=url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            logger.warning("Cannot query Tado: " + (e.message if hasattr(e, 'message') else type(e).__name__))
            return None
    
    def init_home(self):
        details = self.query("https://my.tado.com/api/v2/me")
        if details is not None and "homes" in details and len(details["homes"]) > 0:
            self.home_id = details["homes"][0]["id"]
            return True
        else:
            return False
    
    def query_home(self, force_reinit=False):
        if self.home_id is None or force_reinit:
            return self.init_home()
        else:
            return True
    
    def query_zones(self, force_update=False):
        if self.home_id is None:
            self.init_home()
        if self.home_id is not None:
            if force_update or self.zones_cache is None or self.zones_last_updated is None or (datetime.datetime.now() - self.zones_last_updated).total_seconds() > self.zones_updated_every * 60:
                self.zones_cache = self.query("https://my.tado.com/api/v2/homes/%s/zoneStates" % self.home_id)
                self.zones_last_updated = datetime.datetime.now()
            if self.zones_cache is None:
                self.zones_cache = {}
        else:
            self.zones_cache = {}
        return self.zones_cache

