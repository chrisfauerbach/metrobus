# metrobus
![Metrobus - Elastic]
(elasticsearch_head.png)

Proof of concept and example for smart routing on a dumb bus.

This is a small project focused on my blog posts around routing on a message bus that's dumb.  Like Kafka. 

Stateless and dumb:  https://medium.com/capital-one-developers/stateless-and-dumb-microservices-on-a-message-bus-be78bca93ccb

Fast Cache:    https://medium.com/capital-one-developers/blazing-fast-data-lookup-in-a-microservices-world-dd3ae548ca45

I use some of the cacheing ideas in here for a few of my data lookups.

#Setup

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



docker-compose.yml information:

  # Web Status
  Web application, in order to see some super basic stats from redis.   

  http://localhost:5000/
   
  Flask app in web.py

  # Pusher
  Cool name, eh? Pusher?

  This is the example 'source' of data

  Raw JSON messages going into Kafka...

  pusher.py

  # Bus Driver

  This is the first major step of the process.

  Bus driver is my smart router dude.  In a real

  application, bus driver could/would inspect

  the state of the data coming in. THen, it would

  dynamically build a route

  https://medium.com/capital-one-developers/stateless-and-dumb-microservices-on-a-message-bus-be78bca93ccb

  #Contact Point - Add Email (Stage one)

  This application uses the fake account ID

  generated in the pusher.  Adds an email

  address based on the cps.dat file you

  previously generated. Drops message if can't find

  # Whitelist (stage two)

  Example of a whitelist.  I blogged about black list.

  Same dealio?  If record (email in this case) isn't

  in the list, then we can drop the messsage (return)

  # Log Stop (stage three)

  This is an example 'sink' stop on the metrobus

  All this bad boy does is logs the message..

  in the real world, this could shove into elasticsearch

  or something less cool than ES.




## NOTE
This is a personal project and has nothing to do with my employer or any contracts/clients I have.     

I will build this project out to be MIT licensed though, for anyone to use and abuse.

