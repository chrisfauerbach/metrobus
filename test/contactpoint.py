import time
import redis
from kafka import KafkaConsumer, KafkaProducer
import json
from metrobus import email_generator, metrobus
from threading import Thread
import sys
import _thread


cache = redis.Redis(host='redis', port=6379, decode_responses=True)
ACCT_EMAILS = {}
# To consume latest messages and auto-commit offsets

def callback(message):
    print("Received in CB: ", message)
    real_message = message
    real_message['email'] = ACCT_EMAILS.get(str(real_message.get('account_number')))
    if not real_message.get('email'):
        return 
    return real_message

if __name__ == "__main__":
    print("Trying to start app.")
    counter = 0
    with open('./data/cps.dat', 'r') as input_file:
        for line in input_file:
            line = line.strip()
            acct_id, email = line.split(",", 1)
            ACCT_EMAILS[acct_id] = email
            counter+=1
            if counter % 50000 == 0:
                print('Contact Points 50k, up to ', counter)




    topic_in = "AddEmail"
    metrostop = metrobus.MetroStop(callback, in_topic=topic_in)
    metrostop.start()
