#!/home/mitche50/dpow-mqtt/venv/bin/python3

import simplejson as json
import redis
import modules.db as db

from datetime import datetime

r = redis.Redis('localhost')

def init():
    # Initialize the last hours / minutes that were updated
    # We will reference these to prevent any unnecessary updates
    if r.get("bpow_last_day") is None:
        r.set("bpow_last_day", datetime.utcnow().day)
    if r.get("bpow_last_hour") is None:
        r.set("bpow_last_hour", datetime.utcnow().hour)
    if r.get("bpow_last_minute") is None:
        r.set("bpow_last_minute", datetime.utcnow().minute)

    # Check to make sure that the lists have been populated
    if r.llen("minute_data") < 60:
        print("minute list too short, initializing")
        min_data = db.get_minute_list()
        populate_chart(min_data, "minute")
    if r.llen("day_data") < 30:
        print("day list too short, initializing")
        day_data = db.get_day_list()
        populate_chart(day_data, "day")
    if r.llen("hour_data") < 24:
        print("hour list too short, initializing")
        hour_data = db.get_hour_list()
        populate_chart(hour_data, "hour")
    if r.llen("avg_data") < 24:
        print("avg list too short, initializing")
        avg_data = db.get_avg()
        populate_chart(avg_data, "avg")

def populate_chart(data_dict, chart_name):
    print("populating {} data".format(chart_name))
    r.delete("bpow_{}_data".format(chart_name))
    r.delete("bpow_{}_precache".format(chart_name))
    r.delete("bpow_{}_ondemand".format(chart_name))
    for data in data_dict:
        r.lpush("bpow_{}_data".format(chart_name), json.dumps({"x": data[0], "y": data[1]}))
        if data[2] is not None:
            r.lpush("bpow_{}_precache".format(chart_name), json.dumps({"x": data[0], "y": data[2]}))
        else:
            r.lpush("bpow_{}_precache".format(chart_name), json.dumps({"x": data[0], "y": 0}))
        if data[3] is not None:
            r.lpush("bpow_{}_ondemand".format(chart_name), json.dumps({"x": data[0], "y": data[3]}))
        else:
            r.lpush("bpow_{}_ondemand".format(chart_name), json.dumps({"x": data[0], "y": 0}))
        

if __name__ == "__main__":
    init()

    hour_difference = int(r.get("bpow_last_hour")) - datetime.utcnow().hour
    if hour_difference >= 1:
        print("Hour difference greater than 1, setting data")
        hour_data = db.get_hour_list()
        populate_chart(hour_data, "hour")
        avg_data = db.get_avg()
        populate_chart(avg_data, "avg")
    day_difference = int(r.get("bpow_last_day")) - datetime.utcnow().day
    if day_difference >= 1:
        print("Day difference greater than 1, setting data")
        day_data = db.get_day_list()
        populate_chart(day_data, "day")
    minute_difference = int(r.get("bpow_last_minute")) - datetime.utcnow().minute
    if minute_difference >= 1:
        print("Minute difference greater than 1, setting data")
        minute_data = db.get_minute_list()
        populate_chart(minute_data, "minute")
