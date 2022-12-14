from calendar import week
from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource, reqparse
from flask_apscheduler import APScheduler
from flask_cors import CORS

from alert_api import refresh_alert, refresh_alert_by_detector
from assets_api import refresh_assets
from scorecard import refresh_scorecard
import json
import time
from datetime import datetime
from backup import backupData

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
api = Api(app)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
app.config.from_object(Config())

@scheduler.task('interval', id='refresh_alert_data', seconds=3600, misfire_grace_time=900)
def refresh_alert_data():
    now = datetime.now()
    try:
        refresh_alert()
    except Exception as ex:
        print(f"Refresh alert failed at {now}, error: " + str(ex))

    try:
        refresh_assets()
    except Exception as ex:
        print(f"Refresh asset failed at {now}, error: " + str(ex))

    try:
        refresh_scorecard()
    except Exception as ex:
        print(f"Refresh scorecard failed at {now}, error: " + str(ex))

    try:
        refresh_alert_by_detector()
    except Exception as ex:
        print(f"Refresh detector failed at {now}, error: " + str(ex))

    try:
        backupData()
    except Exception as ex:
        print(f"Backup data failed at {now}, error: " + str(ex))
    print('Refreshed')
scheduler.start()

class AlertLineChart(Resource):
    def get(self):
        f = open('alert_result.json', 'r')
        data = json.load(f)
        f.close()
        return data

class AssetsPieChart(Resource):
    def get(self):
        f = open('assets_result.json', 'r')
        data = json.load(f)
        f.close()
        return data

class DetectorPieChart(Resource):
    def get(self):
        f = open('detector_result.json', 'r')
        data = json.load(f)
        f.close()
        return data

class ScoreCardDoughnut(Resource):
    def get(self):
        f = open('scorecard_result.json', 'r')
        data = json.load(f)
        f.close()
        return data

class SummaryCell(Resource):
    def get(self):
        counter = {
            'informational': 0,
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        f = open('alert_result.json', 'r')
        data = json.load(f)
        for record in data['result']:
            for key, value in record['result'].items():
                if (value is not None):
                    counter[key] += value
        result = []
        for key, value in counter.items():
            result.append({
                'key': key,
                'value': value
            })
        return {
            'data': result
        }


class RenewData(Resource):
    def get(self):
        start = time.time()
        refresh_alert()
        refresh_assets()
        refresh_scorecard()
        refresh_alert_by_detector()
        end = time.time()
        return {
            'status': 'OK',
            'time': end - start
        }

api.add_resource(AlertLineChart, "/linechart")
api.add_resource(RenewData, "/refresh")
api.add_resource(SummaryCell, "/summary")
api.add_resource(AssetsPieChart, "/piechart")
api.add_resource(ScoreCardDoughnut, "/doughnutchart")
api.add_resource(DetectorPieChart, "/piechart2")

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)