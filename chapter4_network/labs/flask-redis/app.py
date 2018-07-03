# 1、运行一个redis实例
# docker run -d --name redis redis

# 2、创建flask-redis镜像
# docker build -t flask-redis .

# 3、通过link到redis容器来访问redis
# docker run -d -p 5000:5000 --link redis --name flask-redis -e REDIS_HOST=redis flask-redis

from flask import Flask
from redis import Redis
import os
import socket

app = Flask(__name__)
redis = Redis(host=os.environ.get('REDIS_HOST', '127.0.0.1'), port=6379)

@app.route('/')
def hello():
    redis.incr('hits')
    return 'Hello Container World! I have been seen %s times and my hostname is %s.\n' % (redis.get('hits'),socket.gethostname())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
