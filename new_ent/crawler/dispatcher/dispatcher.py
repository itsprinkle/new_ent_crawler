# -*- Coding: UTF-8 -*-

"""
@Time : 18-1-5 下午3:44
@Author : courage
@File : utils.py
@Software: PyCharm
"""

from crawler.utils.RedisDBHelper import Redis
from crawler.utils.MysqlDBHelper import Mysql
import time
import json
import crawler.utils.Config as Config
from threading import Thread


def push(priority):
    redis = Redis(Config.RDQNAME,Config.RQUEUE)
    mysql = Mysql()
    while True :
        length = redis.qsize()
        if length < 100:
            ids = []
            keywords = mysql.queryKeyword(priority)
            if keywords:
                keywords = list(keywords)
                for i in range(len(keywords)):
                    keywords[i]["success"]= 2
                    keywords[i]["crawler_count"] = int(keywords[i]["crawler_count"]) + 1
                mysql.updateKeywordState(keywords)
                for i in range(len(keywords)):
                    redis.put(json.dumps(keywords[i]))
        print("**************11")
        time.sleep(120)


def priorityPush(priority):
    redis = Redis(Config.RDQNAME1,Config.RQUEUE)
    mysql = Mysql()
    while True :
        length = redis.qsize()
        if length < 100:
            ids = []
            keywords = mysql.queryKeyword(priority)
            if keywords:
                keywords = list(keywords)
                for i in range(len(keywords)):
                    keywords[i]["success"]= 2
                    keywords[i]["crawler_count"] = int(keywords[i]["crawler_count"]) + 1
                mysql.updateKeywordState(keywords)
                for i in range(len(keywords)):
                    redis.put(json.dumps(keywords[i]))
        print("**************22")
        time.sleep(120)


if __name__ == "__main__":
    t1 = Thread(target=push, args=(0,))
    t2 = Thread(target=priorityPush, args=(1,))
    t1.start()
    t2.start()
    pass