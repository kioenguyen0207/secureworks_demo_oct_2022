from calendar import week
from flask import Flask, jsonify, request, Response
from flask_restful import Api, Resource, reqparse
from flask_apscheduler import APScheduler

from alert_api import refresh_alert
import json

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
api = Api(app)
scheduler = APScheduler()
scheduler.init_app(app)
app.config.from_object(Config())

@scheduler.task('interval', id='refresh_alert_data', seconds=3600, misfire_grace_time=900)
def refresh_alert_data():
    print('Refresh progress is running...')
    refresh_alert()
    print('Refreshed!!!')

scheduler.start()

class AlertLineChart(Resource):
    def get(self):
        f = open('alert_result.json', 'r')
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
            print(record)
            for key, value in record['result'].items():
                if (value is not None):
                    counter[key] += value
        return counter


class RenewData(Resource):
    def get(self):
        refresh_alert()
        return {
            'status': 'OK'
        }

# api.add_resource(column_chart, "/daily")
api.add_resource(AlertLineChart, "/linechart")
api.add_resource(RenewData, "/refresh")
api.add_resource(SummaryCell, "/summary")

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)