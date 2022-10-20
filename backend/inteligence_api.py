from distutils.command.config import config
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from graphqlclient import GraphQLClient

import os
import json
import csv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from dotenv import load_dotenv
load_dotenv()

def refresh_inteligence():
  client_id = os.getenv('CLIENT_ID')
  client_secret = os.getenv('CLIENT_SECRET')
  client = BackendApplicationClient(client_id=client_id)
  oauth_client = OAuth2Session(client=client)
  token = oauth_client.fetch_token(token_url='https://api.ctpx.secureworks.com/auth/api/v2/auth/token', client_id=client_id,
                                client_secret=client_secret)

  query = """query domains($type: ThreatParentType!) {
  threatWatchlist(type: $type) {
    source_ref
    target_ref
    source_internal
    confidence
    description
    }
  }"""

  r = oauth_client.post('https://api.ctpx.secureworks.com/graphql', json={"query": query, "variables": { "type": "DOMAIN" } })
  data = json.loads(r.content)
  for dom in data['data']['threatWatchlist']:
      print(dom)
  with open("inteligence_sample_data.json", "w") as outfile:
    json.dump(data, outfile)


if __name__ == '__main__':
  refresh_inteligence()