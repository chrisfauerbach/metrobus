import json
import os
import time
import sys
import random
import traceback

import requests
from metrobus import wait_open
from metrobus import metrobus
from datetime import datetime
from elasticsearch import Elasticsearch

ELASTIC_HOST = os.environ.get('ELASTIC_HOST', 'localhost')
ELASTIC_PORT = os.environ.get('ELASTIC_PORT', '9200')

es = Elasticsearch([f"{ELASTIC_HOST}:{ELASTIC_PORT}"]) 

# To consume latest messages and auto-commit offsets

def callback(message):
    print("Received in CB: ", message)
    real_message = message
    now_ms = int(time.time() * 1000.0)
    real_message['metrobus_inserted_timestamp'] = now_ms
    idx =  "metro-bus-{}".format(time.strftime("%Y-%m-%d", time.gmtime()))
    print("Final value: ", json.dumps(real_message))
    print("Going to index: ", idx)
    try: 
        res = es.index(index=idx, doc_type='metrobus_doc', body=real_message)
        print(res['result']) 
    except:
        print("Consumer: ", "-"*60)
        traceback.print_exc(file=sys.stdout)
        print("//Consumer: ", "-"*60)


    return 

if __name__ == "__main__":
    print("Trying to start app.")
    topic_in = "Log"
    topic_out = None
    mapping = None

    wait_open(ELASTIC_HOST,ELASTIC_PORT, timeout=120, sleep_time=5)

    with open('./reference/log.mapping', 'r') as f:
        mapping = f.read()
        print(mapping)
        mapping = json.loads(mapping)
    resp = requests.put(f"http://{ELASTIC_HOST}:{ELASTIC_PORT}/_template/template_1", json=mapping)
    print(resp.text)
    metrostop = metrobus.MetroStop(callback, in_topic=topic_in)
    metrostop.start()
