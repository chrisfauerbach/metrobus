import time
import json
from metrobus import metrobus
import sys
import random

def callback(message):
    real_message = message

    # This is the first stop.. no headers, wrappers, etc.
    # Time to add them.   This is going to get a little weird.
    outbound_message = {}
    header = {}

    # For now, everything will go through AddEmail, WhiteList, Log
    routes = []
    routes.insert(0, 'AddEmail')
    routes.insert(0, 'WhiteList')
    routes.insert(0, 'Log')
    header[metrobus.ROUTE_FIELD]          = routes
    header[metrobus.ORIGINAL_ROUTE_FIELD] = routes.copy()
    header[metrobus.HISTORICAL_ROUTE_FIELD] = []
    outbound_message[metrobus.HEADER_FIELD] = header
    outbound_message[metrobus.BODY_FIELD] = real_message
    return outbound_message 

if __name__ == "__main__":
    print("Trying to start app.")
    topic_in = "Source"
    metrostop = metrobus.MetroStop(callback, in_topic=topic_in)
    metrostop.start()
