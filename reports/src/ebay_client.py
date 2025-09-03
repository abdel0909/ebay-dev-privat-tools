
import base64
import os
import requests

EBAY_TOKEN_URLS = {
    "PROD": "https://api.ebay.com/identity/v1/oauth2/token",
    "SANDBOX": "https://api.sandbox.ebay.com/identity/v1/oauth2/token",
}
EBAY_API_BASE = {
    "PROD": "https://api.ebay.com",
    "SANDBOX": "https://api.sandbox.ebay.com",
}

BROWSE_SCOPE = "https://api.ebay.com/oauth/api_scope"

class EbayClient:
    def __init__(self, env="PROD", client_id=None, client_secret=None):
        self.env = env.upper()
        self.client_id = client_id or os.getenv("EBAY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("EBAY_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError("EBAY_CLIENT_ID/EBAY_CLIENT_SECRET fehlen.")
        self._token = None

    def _get_token(self):
        if self._token:
            return self._token
        token_url = EBAY_TOKEN_URLS[self.env]
        basic = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic}",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": BROWSE_SCOPE,
        }
        r = requests.post(token_url, headers=headers, data=data, timeout=30)
        r.raise_for_status()
        self._token = r.json()["access_token"]
        return self._token

    def search_items(self, q, limit=20, filter_str=None):
        token = self._get_token()
        url = f"{EBAY_API_BASE[self.env]}/buy/browse/v1/item_summary/search"
        params = {"q": q, "limit": str(limit)}
        if filter_str:
            params["filter"] = filter_str
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        r = requests.get(url, headers=headers, params=params, timeout=40)
        r.raise_for_status()
        return r.json()
