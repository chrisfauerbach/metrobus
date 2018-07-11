import time
import redis
from kafka import KafkaConsumer, KafkaProducer
import json
import traceback

from threading import Thread
import sys
import _thread

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

# To consume latest messages and auto-commit offsets
#
# in = "Source"
# out = "WhiteList"
# metrostop = metrobus.MetroStop(cb, in_topic=in, out_topic=out)

class MetroStop(object):
    def __init__(self, cb=None, in_topic=None, out_topic=None):
        super().__init__()
        self.consumer = None
        self.producer = None
        self.topic_name = in_topic # "Source"
        self.out_topic = out_topic # "WhiteList"
        print("Input topic: ", self.topic_name)
        print("Output topic: ", self.out_topic)
        self.error_topic = 'Error'
        self.cb = cb
        self.consumer = None 
        print("Looking for consumer in bg thread.") 
        self.consumer = self.get_consumer()
        print("Started background thread with consumer: ", self.consumer)
        self.producer = self.get_producer()
        print("Starting background thread with producer: ", self.producer)

    def get_consumer(self):
        if self.consumer:  return self.consumer
        for _ in range(4):
            try: 
                self.consumer = KafkaConsumer(self.topic_name,
                             group_id='my-group',consumer_timeout_ms=10000,
                             bootstrap_servers=['kafka:9092']
                             , value_deserializer=lambda v: json.loads(v))
            except: 
                print("Consumer: ", "-"*60)
                traceback.print_exc(file=sys.stdout)
                print("//Consumer: ", "-"*60)
            time.sleep(3)
        if not self.consumer:   
            raise Exception("Missing consumer.")

        return self.consumer

    def get_producer(self):
        if self.producer:  return self.producer

        for _ in range(4):
            try:
                self.producer = KafkaProducer(bootstrap_servers=['kafka:9092'] 
              , value_serializer=lambda v: json.dumps(v).encode('utf-8') )
            except: 
                print("Producer: ", "-"*60)
                traceback.print_exc(file=sys.stdout)
                print("//Producer: ", "-"*60)
                time.sleep(3)
        if not self.producer:   
            raise Exception("Missing producer.")
        return self.producer

    def start(self):
        print("Starting thread. listening to: ", self.topic_name)
        consumer = self.get_consumer()

        if consumer:    
            while(True):
                for message in consumer:
                    print ("%s:%d:%d: key=%s value=%s" % (message.topic, 
                        message.partition,
                        message.offset, message.key,
                        message.value))
                    self.add_count(message.topic)
                    if self.cb:
                        retval = self.cb(message)
                        if retval and self.out_topic:
                            self.producer.send(self.out_topic, retval)

                print("No message detected yet.")
        else:
            print("SOMETHING IS BROKEN. NO CONSUMER")
            sys.exit(1)
        print("UH OH. I am exiting for some reason.")
    
    def add_count(self, topic):
        COUNTER_KEY = "counter"
        return cache.hincrby(COUNTER_KEY, topic, 1)
   

if __name__ == "__main__":
    print("Trying to start app.")
    bg_thread = MetroStop(cb)
    # bg_thread.daemon = True
    bg_thread.start()
