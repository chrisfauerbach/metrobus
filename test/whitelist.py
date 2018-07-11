import time
import json
from metrobus import metrobus
import sys
import random


# To consume latest messages and auto-commit offsets
WHITE_LIST = set()

def callback(message):
    print("Received in CB: ", message)
    real_message = message
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
            line = line.strip()
            WHITE_LIST.add(line)
            counter+=1 
            if counter % 100000 == 0:
                print('added another 100k, up to ', counter)

            
    topic_in = "WhiteList"
    metrostop = metrobus.MetroStop(callback, in_topic=topic_in)
    metrostop.start()
