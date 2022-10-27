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

def refresh_assets():
  client_id = os.getenv('CLIENT_ID')
  client_secret = os.getenv('CLIENT_SECRET')
  client = BackendApplicationClient(client_id=client_id)
  oauth_client = OAuth2Session(client=client)
  token = oauth_client.fetch_token(token_url='https://api.ctpx.secureworks.com/auth/api/v2/auth/token', client_id=client_id,
                                client_secret=client_secret)

  gql_client = GraphQLClient('https://api.ctpx.secureworks.com/graphql')
  gql_client.inject_token("Bearer " + token['access_token'], "Authorization")
  result = gql_client.execute('''
  {
    allAssets(
      offset: 0,
      limit: 99999,
      order_by: hostname,
      filter_asset_state: All,
      only_most_recent: true
    )
    {
      assets {
        hostnames {
          hostname
        }
        tags {
          tag
        }
      }
    }
  }
  ''')

  data = json.loads(result)

  result_hostnames = {}
  for record in data['data']['allAssets']['assets']:
    if record['hostnames'][0]['hostname'] in result_hostnames.keys():
      result_hostnames[record['hostnames'][0]['hostname']] += 1
    else:
      result_hostnames[record['hostnames'][0]['hostname']] = 1

  result_tags = {}
  for tags in data['data']['allAssets']['assets']:
    for tag in tags['tags']:
      if tag['tag'] in result_tags.keys():
        result_tags[tag['tag']] += 1
      elif tag['tag'] is not None:
        result_tags[tag['tag']] = 1

  result = {}
  result['total_hostnames'] = len(result_hostnames.keys())
  result['total_tags'] = len(result_tags.keys())
  formatted_result_tags = []
  for key, value in result_tags.items():
    formatted_result_tags.append({
      'key': key,
      'value': value
    })
  result['data'] = formatted_result_tags

  json_load = json.loads(json.dumps(result))
  with open("assets_result.json", "w") as outfile:
      json.dump(json_load, outfile)

if __name__ == '__main__':
  refresh_assets()