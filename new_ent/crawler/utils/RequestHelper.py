# -*- coding: utf-8 -*-
"""
@Time : 18-1-5 下午7:02
@Author : courage
@Site : 
@File : RequestHelper.py
@Software: PyCharm
"""

import requests
import logging
import traceback
import crawler.utils.Config as Config

# request 通用功能
#
# 1请求功能
# 2cookie 缓存功能
# 3请求转码功能
# 4返回字符串功能
# 5返回json(字典)功能
# 6请求头的配置


headers = {
    "common":{
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    "common1":{
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "X - Requested - With": "XMLHttpRequest"
    },
    "get":{
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Connection":"keep-alive",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With":"XMLHttpRequest"
    },
    "post":{
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Connection":"keep-alive",
        "X-Requested-With":"XMLHttpRequest"
    }
}


class RequestHeler(object):

    @staticmethod
    def get(url,params=None,retry=Config.retry_count,**kwargs):
        response = None
        for i in range(retry):
            try:
                response = requests.get(url,params=params,**kwargs)
                break
            except TimeoutError as e:
                print("request get time out :",url)
                continue
            except Exception as e:
                logging.error(e)
                # logging.exception(e)
                # traceback.print_exc()
                continue
        return response

    @staticmethod
    def post(url,data=None,json=None,retry=Config.retry_count,**kwargs):
        response = None
        for i in range(retry):
            try:
                response = requests.post(url,data=data,json=json,**kwargs)
                break
            except TimeoutError as e:
                print("request post time out :", url)
                continue
            except Exception as e:
                logging.error(e)
                # logging.exception(e)
                # traceback.print_exc()
                continue
        return response