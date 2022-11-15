import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

def refresh_scorecard():
  portfolio_id = os.getenv('SCORECARD_PORTFOLIO_ID')
  token = os.getenv('SCORECARD_TOKEN')
  url = f"https://api.securityscorecard.io/portfolios/{portfolio_id}/companies"
  headers = {
      "accept": "application/json; charset=utf-8",
      "Authorization": f"Token {token}"
  }
  response = requests.get(url, headers=headers)
  json_load = json.loads(response.content)
  with open("scorecard_raw.json", "w") as outfile:
      json.dump(json_load, outfile)
  data = []
  for domain in json_load['entries']:
    data.append({
      "domain": domain['domain'],
      "grade": domain['grade']
    })
  result = {
    'data': data
  }
  with open("scorecard_result.json", "w") as outfile:
      json.dump(json.loads(json.dumps(result)), outfile)
      
if __name__ == "__main__":
  refresh_scorecard()