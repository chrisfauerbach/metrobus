import time
import redis
from kafka import KafkaConsumer, KafkaProducer
import json
from metrobus import email_generator, metrobus
from threading import Thread
import sys
import _thread


cache = redis.Redis(host='redis', port=6379, decode_responses=True)

# To consume latest messages and auto-commit offsets

def cb(message):
    print("Received in CB: ", message)
    real_message = message.value
    real_message['email'] = email_generator()
    return real_message

if __name__ == "__main__":
    print("Trying to start app.")
    topic_in = "Source"
    topic_out = "WhiteList"
    metrostop = metrobus.MetroStop(cb, in_topic=topic_in, out_topic=topic_out)
    metrostop.start()
