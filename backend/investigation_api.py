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

def refresh_investigation():
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
    allInvestigations {
      id
      tenant_id
      tags
      alerts {
        id
      }
      auth_credentials
      key_findings
      description
      created_at
      updated_at
      notified_at
      archived_at
      service_desk_id
      service_desk_type
      assignee_id
      status
      created_by
      contributors
      created_by_scwx
      created_by_partner
      type
      priority
    }
  }
  ''')


  print(result)
  data = json.loads(result)
  with open("investigation_sample_data.json", "w") as outfile:
    json.dump(data, outfile)


if __name__ == '__main__':
  refresh_investigation()