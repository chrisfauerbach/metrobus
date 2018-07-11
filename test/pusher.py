import time
from flask import Flask
from kafka import KafkaProducer
from threading import Thread
import sys
from random import randint, choice
import json
import string


def get_producer():
    producer = None
    for _ in range(4):
        try: 
            producer = KafkaProducer( bootstrap_servers=['kafka:9092']
            , value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        except Exception as e: 
            print("Issue getting producer..  We'll try again later.")
            print(e) 
        time.sleep(3)
    if not producer:   
        raise Exception("Missing producer.")
    print("Returning producer: ", producer)
    return producer


if __name__ == "__main__":
    producer = get_producer()
    for x in range(1000):
        # header = {}
        # header['route'] = ['Source','AddEmail', 'Whitelist','Log']
        # header['body'] = msg
        msg ={}
        msg['x'] = x
        msg['message_type_code'] = 'ALTABC'
        msg['account_number'] = randint(1000000,1999999)
        future = producer.send('Source', msg)
        try:
            record_metadata = future.get(timeout=10)
            print(record_metadata.topic)
            print(record_metadata.partition)
            print(record_metadata.offset)
        except KafkaError:
            # Decide what to do if produce request failed...
            log.exception()
            pass


        time.sleep(.1)
        

