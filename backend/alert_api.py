from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import json
import csv
from helper import last_two_weeks_time

from dotenv import load_dotenv
load_dotenv()

def refresh_alert():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    client = BackendApplicationClient(client_id=client_id)
    oauth_client = OAuth2Session(client=client)
    token = oauth_client.fetch_token(token_url='https://api.ctpx.secureworks.com/auth/api/v2/auth/token', client_id=client_id,
                                     client_secret=client_secret)
    
    dateRange = last_two_weeks_time()
    returnValue = []
    severityRules = {
        'informational': [0, 0.2],
        'low': [0.2, 0.4],
        'medium': [0.4, 0.6],
        'high': [0.6, 0.8],
        'critical': [0.8, 1]
    }
    for date in dateRange:
        recordValue = {
            'date': date['date'],
            'date_sorter': date['date_sorter'],
            'result': 0
        }
        counter = {
            'informational': 0,
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        for category, range in severityRules.items():
            query = """query {
            alertsServiceSearch(
                in: {
                cql_query: "from alert """ + f"severity >= {range[0]} AND severity < {range[1]} AND EARLIEST='{date.get('after')}' AND LATEST='{date.get('before')}'" + """"
                }
            ) {
                status
                reason
                alerts {
                list {
                    id
                    tenant_id
                    status
                    suppressed
                    suppression_rules {
                    id
                    version
                    }
                    resolution_reason
                    attack_technique_ids
                    entities{
                    entities
                    relationships{
                        from_entity
                        relationship
                        to_entity
                    }
                    }
                    metadata {
                    creator {
                        detector {
                            detector_id
                            detector_name
                        }
                    }
                    engine {
                        name
                    }
                    creator {
                        detector {
                        version
                        detector_id
                        }
                        rule {
                        rule_id
                        version
                        }
                    }
                    title
                    description
                    confidence
                    severity
                    created_at {
                        seconds
                    }
                    }
                    investigation_ids {
                    id
                    }
                    sensor_types
                }
                total_results
                }
            }
            }"""

            r = oauth_client.post('https://api.ctpx.secureworks.com/graphql', json={"query": query})
            data = json.loads(r.content)
            with open(f"alert_raw_{category}.json", "w") as outfile:
                json.dump(data, outfile)
            if data["data"]["alertsServiceSearch"]["alerts"]["total_results"] is not None:
                counter[category] = data["data"]["alertsServiceSearch"]["alerts"]["total_results"]
        recordValue['result'] = counter
        returnValue.append(recordValue)
    result_in_json = {
        'status': 'OK',
        'result': returnValue
    }
    json_dump = json.dumps(result_in_json)
    json_load = json.loads(json_dump)
    with open("alert_result.json", "w") as outfile:
        json.dump(json_load, outfile)

def refresh_alert_by_detector():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    client = BackendApplicationClient(client_id=client_id)
    oauth_client = OAuth2Session(client=client)
    token = oauth_client.fetch_token(token_url='https://api.ctpx.secureworks.com/auth/api/v2/auth/token', client_id=client_id,
                                     client_secret=client_secret)
    dateRange = last_two_weeks_time()
    query = """query {
            alertsServiceSearch(
                in: {
                cql_query: "from alert status='OPEN'""" + f"severity >= 0 AND EARLIEST='{dateRange[0].get('after')}' AND LATEST='{dateRange[13].get('before')}'" + """",
                limit: 9999
                }
            ) {
                status
                reason
                alerts {
                list {
                    id
                    tenant_id
                    status
                    suppressed
                    suppression_rules {
                    id
                    version
                    }
                    resolution_reason
                    attack_technique_ids
                    entities{
                    entities
                    relationships{
                        from_entity
                        relationship
                        to_entity
                    }
                    }
                    metadata {
                    creator {
                        detector {
                            detector_id
                            detector_name
                        }
                    }
                    engine {
                        name
                    }
                    creator {
                        detector {
                        version
                        detector_id
                        detector_name
                        }
                        rule {
                        rule_id
                        version
                        }
                    }
                    title
                    description
                    confidence
                    severity
                    created_at {
                        seconds
                    }
                    }
                    investigation_ids {
                    id
                    }
                    sensor_types
                }
                total_results
                }
            }
            }"""

    r = oauth_client.post('https://api.ctpx.secureworks.com/graphql', json={"query": query})
    data = json.loads(r.content)
    with open("alert_raw.json", "w") as outfile:
        json.dump(data, outfile)
    temp_result = {}
    for record in data["data"]["alertsServiceSearch"]["alerts"]["list"]:
        detector = record["metadata"]["creator"]["detector"]["detector_name"]
        if detector in temp_result.keys():
            temp_result[detector] += 1
        else:
            temp_result[detector] = 1
    result = []
    for key, value in temp_result.items():
        result.append({
        'key': key,
        'value': value
        })
    json_load = json.loads(json.dumps({
        'data': result
    }))
    with open("detector_result.json", "w") as outfile:
        json.dump(json_load, outfile)


if __name__ == "__main__":
    refresh_alert()
