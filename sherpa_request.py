import requests
from enum import Enum
import time
import uuid 
from hashlib import sha1
import hmac
import base64
import json
from IPython.display import clear_output

base_url = "https://recom.sherpa.ai"
sherpa_api_key = ""
sherpa_private_key = ""

class SherpaRequest:
    
    class Verb(Enum):
        GET = 1
        POST = 2
        PUT = 3
        DELETE = 4
        PATCH = 5
    
    def __init__(self, verb=Verb.GET, path="", extra_headers={}, data={}):
        self.verb = verb
        self.url = base_url + path
        self.data = data                
        
        nonce = str(uuid.uuid1())
        timestamp = str(int(round(time.time() * 1000)))
        hmac = self.__sign_request(sherpa_private_key, ":".join([path.split("?")[0], timestamp, nonce]))

        self.headers = {
            'Content-Type': 'application/json',
            'X-Sherpa-apikey': sherpa_api_key,
            'X-Sherpa-timestamp': timestamp,
            'X-Sherpa-nonce': nonce,
            'X-Sherpa-hmac': hmac
        }
        for key, value in extra_headers.items():
            self.headers[key] = value
        # print(self.verb)
        # print(self.url)
        # print(self.headers)
        # print(self.data)
        
    def perform_request(self, pretty_print=True):
        if self.verb == SherpaRequest.Verb.GET:
            result = requests.get(self.url, headers=self.headers)
        elif self.verb == SherpaRequest.Verb.POST:
            result = requests.post(self.url, headers=self.headers, data=self.data)
        elif self.verb == SherpaRequest.Verb.PUT:
            result = requests.put(self.url, headers=self.headers, data=self.data)
        elif self.verb == SherpaRequest.Verb.DELETE:
            result = requests.delete(self.url, headers=self.headers)
        elif self.verb == SherpaRequest.Verb.PATCH:
            result = requests.patch(self.url, headers=self.headers, data=self.data)
        if pretty_print:
            self.pretty_print_response(result)
        return result
    
    def __sign_request(self, key: str, raw: str):
        a = bytearray()
        a.extend(map(ord, key))

        b = bytearray()
        b.extend(map(ord, raw))

        hashed = hmac.new(a, b, sha1)

        return base64.b64encode(hashed.digest())
    
    @staticmethod
    def pretty_print_response(response):
        prettyStr = "Response status code: " + str(response.status_code)
        if response.text:
            prettyStr += "\nResponse content:\n"
            try:
                parsed = json.loads(response.text)
                prettyStr += json.dumps(parsed, indent=4, sort_keys=True)
            except:
                prettyStr += response.text
        print(prettyStr)