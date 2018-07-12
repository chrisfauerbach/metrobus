# metrobus
Proof of concept and example for smart routing on a dumb bus.

This is a small project focused on my blog posts around routing on a message bus that's dumb.  Like Kafka. 

Stateless and dumb:  https://medium.com/capital-one-developers/stateless-and-dumb-microservices-on-a-message-bus-be78bca93ccb

Fast Cache:    https://medium.com/capital-one-developers/blazing-fast-data-lookup-in-a-microservices-world-dd3ae548ca45

I use some of the cacheing ideas in here for a few of my data lookups.

The concept for the 'test' example application is fairly simple.  The 'pusher' generates records, as if from a client or application.  These records are simple JSON structures.  For our example, we get cool things like an account number (FAKE!).  The 'pusher' sends the message to the 'Source' topic on Kafka.  Consider this your public entry point for upstream clients.

Next, the 'busdriver' takes over.  The 'busdriver' then pulls data from the Source, and formats it to something that downstream can use.  In our case, we add a 'header' object.  This 'header' contains a 'route' (and an initial route, and a historical route for tracking purposes).  Once this is created based on some intelligence (if the message is in a certain state, or of a certain type, etc), then the 'busdriver' configures it to be so.    This is where the 'metrobus' framework comes into play.  Once the callback to the 'busdriver' returns the 'wrapped' object, the framework pulls (pops) the "next" stop (Kafka Topic) from the routes stack, and sends the message downstream.

In this case, our first stop after the 'busdriver' is the microservice that uses external data to get the email address associated with the account..  This is our 'contactpoint' micro service.  You know, the point at which we should contact the customer?   Email address?    Come on. Generic!  The 'contactpoint' microservice pulls from an external cache, and loads the email address.  If the cache doesn't contain the email address, the callback function returns None, indicating that the message is 'dropped' appropriately.   I may change this to a specific 'Exception'.  Soon?

Next is the 'whitelist' service.  Long story short, same pattern.  If the email address is in the whitelist cache, we can send to it.  If not, the message gets dropped.

Next is the 'LogStop' service.  If we were really building an email service, this is where we would send the message out through an SMTP server or something cool like mailgun or mailchimp.  IN this case, we just drop it.. cause you know... example code.

Questions?   hit me up:    chris [ @    ] [at] (obfuscation)   fauie.com


OH, The entire reason I wrote this framework is to make each of my stops 'dumb', and focus on only one thing... processing the message.  Doesn't care where it came from.  Doesn't care where it's going.  Just do your job.  KISS.

```python
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
```

The unique bit of code for this 'stop' is the "topic_in" (configuration file, seriously folks), loading of the cache (whitelist.dat), and then processing each message.  Seriously, it's like 12 lines of code.. This is what I mean, when I say "are you kidding? That's like 10 lines of code!"
 

# Setup

Once you download the clone/download this repo, let's setup some stuff in the test path:
- git clone git@github.com:chrisfauerbach/metrobus.git
- cd metrobus
- cd test
- pip install --upgrade pipenv
- pipenv shell
- mkdir data
- python make_whitelist.py > data/whitelist.dat
- python make_account_email.py  > data/emails.dat
- ./run.sh

You'll then see a lot of docker compose stuff happening.   The environment variables are in metrobus.env

They're set to:
- Kafka:  kafka:9092
- Redis:  redis:6379

Those host names are set in the docker-compose file.


# docker-compose.yml

  ## Web Status
  Web application, in order to see some super basic stats from redis.   

  http://localhost:5000/
   
  Flask app in web.py

  ## Pusher
  Cool name, eh? Pusher?

  This is the example 'source' of data

  Raw JSON messages going into Kafka...

  pusher.py

  ## Bus Driver

  This is the first major step of the process.

  Bus driver is my smart router dude.  In a real

  application, bus driver could/would inspect

  the state of the data coming in. THen, it would

  dynamically build a route

  https://medium.com/capital-one-developers/stateless-and-dumb-microservices-on-a-message-bus-be78bca93ccb

  ## Contact Point - Add Email (Stage one)

  This application uses the fake account ID

  generated in the pusher.  Adds an email

  address based on the cps.dat file you

  previously generated. Drops message if can't find

  ## Whitelist (stage two)

  Example of a whitelist.  I blogged about black list.

  Same dealio?  If record (email in this case) isn't

  in the list, then we can drop the messsage (return)

  ## Log Stop (stage three)

  This is an example 'sink' stop on the metrobus

  All this bad boy does is logs the message..

  in the real world, this could shove into elasticsearch

  or something less cool than ES.




## NOTE
This is a personal project and has nothing to do with my employer or any contracts/clients I have.     

I will build this project out to be MIT licensed though, for anyone to use and abuse.

