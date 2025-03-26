from quietpaper import logger
import requests
import datetime
import json

class TadoConnection:
    def __init__(self, refresh_token_file):
        self.refresh_token_file = refresh_token_file
        self.access_token = None
        self.access_token_expires = None
        self.refresh_token = None
        self.home_id = None
        self.zones = None
    
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
        details = self.query("https://my.tado.com/api/v1/me")
        if details is not None and "homeId" in details:
            self.home_id = details["homeId"]
            return True
        else:
            return False
    
    def query_home(self, url_suffix):
        if self.home_id is None:
            self.init_home()
        if self.home_id is not None:
            return self.query("https://my.tado.com/api/v2/homes/%s/%s" % (self.home_id, url_suffix))
        else:
            return None
