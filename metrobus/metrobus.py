import time
import json
import traceback
import sys
import logging

import os
import redis
import kafka
import kafka.errors
from kafka import KafkaConsumer, KafkaProducer


HEADER_FIELD = 'header'
ROUTE_FIELD = 'route'
ORIGINAL_ROUTE_FIELD = 'original_route'
HISTORICAL_ROUTE_FIELD = 'historical_route'
PAYLOAD_FIELD = 'payload'

COUNTER_KEY = "counter"

KAFKA_HOST = os.environ.get('KAFKA_HOST', 'localhost')
KAFKA_PORT = os.environ.get('KAFKA_PORT', 9092)
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)


CACHE = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class BadStateRecordError(Exception):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        topic -- which topic was being listened to
        value -- String / JSON of the message
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, topic, value, message):
        super().__init__(message)
        self.topic = topic
        self.value = value
        self.message = message

    def __str__(self):
        return f"ErrorConditionRecord: {self.topic} {self.message} {self.value}"


# To consume latest messages and auto-commit offsets
#
# in = "Source"
# out = "WhiteList"
# metrostop = metrobus.MetroStop(callback, in_topic=in, out_topic=out)

class MetroStop(object):
    def __init__(self, callback=None, in_topic=None):
        super().__init__()
        self.consumer = None
        self.producer = None
        self.topic_name = in_topic # "Source"
        logging.info("Input topic: %s", self.topic_name)
        self.error_topic = 'Error'
        self.callback = callback
        self.consumer = None
        logging.info("Looking for consumer in bg thread.")
        logging.info(f"Config:\nKafka: {KAFKA_HOST}:{KAFKA_PORT}\nRedis: {REDIS_HOST}:{REDIS_PORT}")
        #self.consumer = self.get_consumer()
        #logging.info("Started background thread with consumer: %s", self.consumer)
        #self.producer = self.get_producer()
        #logging.info("Starting background thread with producer: %s", self.producer)
        self.setLastMessage(None)

    def setLastMessage(self, message):
        self.last_message = message

    def push_stop(self, stop):
        routes = []
        message_header = None

        if self.last_message:
            message_header = self.last_message.get(HEADER_FIELD)
            if message_header:
                routes = message_header.get(ROUTE_FIELD)
        if routes:
            routes.insert(0, stop)

    def pop_stop(self):
        routes = []
        message_header = None

        if self.last_message:
            message_header = self.last_message.get(HEADER_FIELD)
            if message_header:
                routes = message_header.get(ROUTE_FIELD)
        if routes:
            return routes.pop()
        return 

    def get_consumer(self):
        if self.consumer:
            return self.consumer
        for _ in range(4):
            try:
                self.consumer = KafkaConsumer(self.topic_name,
                                              group_id='my-group',
                                              consumer_timeout_ms=30000,
                                              bootstrap_servers=[f"{KAFKA_HOST}:{KAFKA_PORT}"],
                                              value_deserializer=lambda v: json.loads(v))
            except kafka.errors.NoBrokersAvailable:
                pass
            except: 
                logging.exception("Error in consumer") 
            time.sleep(3)
        if not self.consumer:
            raise Exception("Missing consumer.")

        return self.consumer

    def get_producer(self):
        if self.producer:
            return self.producer

        for _ in range(4):
            try:
                self.producer = KafkaProducer(bootstrap_servers=['kafka:9092'],
                                              value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            except kafka.errors.NoBrokersAvailable:
                pass
            except:
                logging.exception("Error in producer") 
                time.sleep(3)
        if not self.producer:
            raise Exception("Missing producer.")
        return self.producer

    def start(self):
        try:
            self._start()
        except:
            logging.exception("There was an uncaught exception during processing.")

    def _start(self):
        logging.info("Starting thread. listening to: ", self.topic_name)
        consumer = self.get_consumer() 
        producer = self.get_producer()
        if consumer:
            while True:
                for kafka_message in consumer:
                    logging.debug("%s:%s:%s: key=%s value=%s",kafka_message.topic, kafka_message.partition, kafka_message.offset, kafka_message.key, kafka_message.value)
                    self.add_count(kafka_message.topic)
                    message = kafka_message.value 
                    message_payload = message.get(PAYLOAD_FIELD, message)
                    
                    if self.callback:   
                        # retval means the callback returned something
                        returned_body = self.callback(message_payload)  
                        if returned_body: # and (local_out_topic):
                            #This may happen if its a new message (since above has no head/body)
                            #but the retval may have is, inserted by busdriver.   
                            # @TODO  change how this works.
                            if HEADER_FIELD in returned_body:
                                message = retval
                                message_header = message.get(HEADER_FIELD)
                            else:
                                #logging.error("NO MESSAGE HEADER, I think this is where I add one.?????")
                                message[PAYLOAD_FIELD] = retval

                            self.setLastMessage( message  )
                            next_stop = self.pop_stop()
                            if next_stop:
                                message_header.get(HISTORICAL_ROUTE_FIELD).append(next_stop)
                                logging.info(f"Downstream, now sending to %s %s", next_stop, message)
                                producer.send(next_stop, message)
                            else:
                                logging.error("NO NEXT STOP 1: %s", message.value)
                                logging.error("NO NEXT STOP 2: %s", message)
                                logging.error("NO NEXT STOP 2.5:%s", message_payload)
                                logging.error("NO NEXT STOP 3: %s", message)
                                sys.exit(1)
                        else: #No retval!
                            logging.info("Nothing returned, therefore, assume filtered.")
                    self.setLastMessage( None  )
                logging.info("No message detected yet.")
        else:
            logging.error("SOMETHING IS BROKEN. NO CONSUMER")
            sys.exit(1)
        logging.error("Uh Oh. I am exiting for some reason.")

    def add_count(self, topic):
        return CACHE.hincrby(COUNTER_KEY, topic, 1)


if __name__ == "__main__":
    logging.info("Trying to start app.")
    metro = MetroStop()
    metro.setLastMessage({
        HEADER_FIELD: {
            ROUTE_FIELD:[1,2,3,4]
        },
        PAYLOAD_FIELD: {"one":"two", "three":3 }
    })
    print(metro.pop_stop())
    print(metro.pop_stop())
    print(metro.pop_stop())
    






