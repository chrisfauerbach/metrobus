import time
import json
import traceback
import sys
import os
import redis
import kafka
import kafka.errors
from kafka import KafkaConsumer, KafkaProducer


HEADER_FIELD = 'header'
ROUTE_FIELD = 'route'
ORIGINAL_ROUTE_FIELD = 'original_route'
HISTORICAL_ROUTE_FIELD = 'historical_route'
BODY_FIELD = 'body'

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
        print("Input topic: ", self.topic_name)
        self.error_topic = 'Error'
        self.callback = callback
        self.consumer = None
        print("Looking for consumer in bg thread.")
        print(f"Config:\nKafka: {KAFKA_HOST}:{KAFKA_PORT}\nRedis: {REDIS_HOST}:{REDIS_PORT}")
        self.consumer = self.get_consumer()
        print("Started background thread with consumer: ", self.consumer)
        self.producer = self.get_producer()
        print("Starting background thread with producer: ", self.producer)

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
                print("Consumer: ", "-"*60)
                traceback.print_exc(file=sys.stdout)
                print("//Consumer: ", "-"*60)
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
            while True:
                for message in consumer:
                    print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition, message.offset, message.key, message.value))
                    self.add_count(message.topic)
                    if self.callback:
                        message_body = message.value
                        message_header = message_body.get(HEADER_FIELD)
                        downstream_message = message_body.get(BODY_FIELD, message_body)
                        retval = self.callback(downstream_message)
                        next_stop = None
                        if retval: # and (local_out_topic):
                            if not message_header:
                                message_body = retval
                                message_header = message_body.get(HEADER_FIELD)
                            if message_header:
                                routes = message_header.get(ROUTE_FIELD)
                                if routes:
                                    next_stop = routes.pop()
                                    message_header.get(HISTORICAL_ROUTE_FIELD).insert(0, next_stop)
                            else:
                                print("NO MESSAGE HEADER, I think this is where I add one.?????")

                            if next_stop:
                                print(f"Downstream, now sending to {next_stop} {message_body}")
                                self.producer.send(next_stop, message_body)
                            else:
                                print("NO NEXT STOP 1: ", message.value)
                                print("NO NEXT STOP 2: ", message_body)
                                sys.exit(1)
                        else: #No retval!
                            print("Nothing returned, therefore, assume filtered.")
                print("No message detected yet.")
        else:
            print("SOMETHING IS BROKEN. NO CONSUMER")
            sys.exit(1)
        print("Uh Oh. I am exiting for some reason.")
    def add_count(self, topic):
        return CACHE.hincrby(COUNTER_KEY, topic, 1)


if __name__ == "__main__":
    print("Trying to start app.")
    METRO_STOP = MetroStop()
    METRO_STOP.start()
