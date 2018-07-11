import time
import json
from metrobus import metrobus
import sys
import random


# To consume latest messages and auto-commit offsets

def cb(message):
    print("Received in CB: ", message)
    real_message = message.value
    print("Final value: ", json.dumps(real_message))
    return 

if __name__ == "__main__":
    print("Trying to start app.")
    topic_in = "Log"
    topic_out = None
    metrostop = metrobus.MetroStop(cb, in_topic=topic_in, out_topic=topic_out)
    metrostop.start()
