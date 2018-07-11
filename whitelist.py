import time
import json
from metrobus import metrobus
import sys
import random


# To consume latest messages and auto-commit offsets
WHITE_LIST = set()

def cb(message):
    print("Received in CB: ", message)
    real_message = message.value
    if real_message['email'] in WHITE_LIST:
        real_message['whitelist'] = True
        return real_message 
    print("DROPPING due to missing white list.")
    return 

if __name__ == "__main__":
    print("Trying to start app.")
    print("Loading whitelist")
    counter = 0
    with open('./data/whitelist.dat', 'r') as input_file:
        for line in input_file:
            WHITE_LIST.add(line)
            counter+=1 
            if counter % 10000 == 0:
                print('added another 10k, up to ', counter)

            
    topic_in = "WhiteList"
    topic_out = "Log"
    metrostop = metrobus.MetroStop(cb, in_topic=topic_in, out_topic=topic_out)
    metrostop.start()
