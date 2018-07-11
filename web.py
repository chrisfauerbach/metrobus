import time
import redis
from flask import Flask, jsonify
import sys
from logging.config import dictConfig

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'stderr': {
        'class': 'logging.StreamHandler',
        # 'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['stderr']
    }
})

app = Flask(__name__)

COUNTER_KEY = "counter"
def get_stats():
    temp_stats = cache.hgetall(COUNTER_KEY)
    app.logger.info("TEMP STATS: %s", temp_stats)
    return temp_stats
 
@app.route('/')
def hello():
    app.logger.info("About to stats.")
    try:
        stats = get_stats()
        app.logger.info("STATS1: %s", stats)
        stats['hit_count'] = get_hit_count()
        app.logger.info("STATS2: %s", stats)
    except Exception as e:
        app.logger.info("ERROR WHILE GETTING STATS: ", e)
    return jsonify(stats)

def flaskThread():
    port = 5000
    app.logger.info("Starting up on port: %s", port)
    app.run(host="0.0.0.0", debug=True, port=port)

if __name__ == "__main__":
    app.logger.info("Trying to start web.")
    flaskThread()
