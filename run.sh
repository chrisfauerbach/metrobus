docker-compose  kill
docker-compose  rm -f
docker build --tag "webtest:example1" --file ./DockerfileWeb . 
docker build  --tag "webtest:pusher" --file ./DockerfilePusher . 
docker build  --tag "webtest:contactPoint" --file ./DockerfileContactPoint . 
docker build  --tag "webtest:whiteList" --file ./DockerfileWhiteList . 
docker build  --tag "webtest:logstop" --file ./DockerfileLogstop . 
docker build  --tag "webtest:busdriver" --file ./DockerfileBusdriver . 
docker-compose up
