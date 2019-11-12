from quietpaper import logger
import requests
import datetime
import json

class TadoConnection:
    def __init__(self, client_secrets_file, username, password):
        with open(client_secrets_file, "r") as fd:
            self.client_secret = json.load(fd)["secret"]
        self.username = username
        self.password = password
        self.bearer_token = None
        self.bearer_token_expires = None
        self.home_id = None
        self.zones = None
    
    def acquire_bearer_token(self):
        data = {
            "client_id": "tado-web-app",
            "grant_type": "password",
            "scope": "home.user",
            "username": self.username,
            "password": self.password,
            "client_secret": self.client_secret
        }
        response = requests.post(url="https://auth.tado.com/oauth/token", data=data)
        self.bearer_token = json.loads(response.text)
        self.bearer_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=self.bearer_token["expires_in"])

    def get_bearer_token(self):
        if self.bearer_token is None or datetime.datetime.now() > self.bearer_token_expires:
            self.acquire_bearer_token()
        return self.bearer_token
    
    def get_access_token(self):
        return self.get_bearer_token()["access_token"]
    
    def query(self, url):
        try:
            headers = { "Authorization": "Bearer %s" % self.get_access_token() }
            response = requests.get(url=url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            logger.warning("Cannot query Tado: " + (e.message if hasattr(e, 'message') else type(e).__name__))
            return None
    
    def init_home(self):
        details = self.query("https://my.tado.com/api/v1/me")
        if details is not None:
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
