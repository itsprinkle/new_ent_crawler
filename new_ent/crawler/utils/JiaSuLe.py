# -*- coding: utf-8 -*-

"""
@Time : 18-1-5 下午3:44
@Author : courage
@File : utils.py
@Software: PyCharm
"""

import execjs
import time
from crawler.utils.ProvinceRoute import ProvinceRoute
import crawler.utils.Config as Config
import requests
import logging


class JiaSuLe(object):
    jiaSuLe = {}

    @staticmethod
    def getJiaSuLe(province,isNew=False):
        if isNew :
            JiaSuLe.jiaSuLe.pop(str(province))
        elif len(JiaSuLe.jiaSuLe) > 0:
            temp_list = []
            for k, v in JiaSuLe.jiaSuLe.items():
                if time.time() - v["time"] > 300:#3600
                    temp_list.append(k)
            for i in temp_list:
                JiaSuLe.jiaSuLe.pop(i)
        if JiaSuLe.jiaSuLe.get(str(province)) is not None:
            return JiaSuLe.jiaSuLe.get(str(province))
        else:
            url1 = ProvinceRoute.route(province)
            url2 = url1 +"/index.html"

            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "max-age=0",
                "Proxy-Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
            }

            r = None
            try:
                r = requests.get(url2, headers=headers, timeout=Config.timeout)
            except Exception as e:
                logging.exception(e)

            if r is not None and r.status_code ==521 :
                jsl = {}
                jsl["__jsluid"] = r.cookies.get("__jsluid")
                jsl["time"] = time.time()
                __jsl_clearance = JiaSuLe.exe(str(r.text),url1)
                if __jsl_clearance is None:
                    return None
                jsl["__jsl_clearance"] = __jsl_clearance
                JiaSuLe.jiaSuLe[str(province)] = jsl
                return JiaSuLe.jiaSuLe.get(str(province))
        return None

    @classmethod
    def exe(cls,script,url="'http://www.gsxt.gov.cn'"):
        if type(script) is str and len(script)>0:
            temp2 = None
            try:
                script = script.replace("\0","")
                script = script.replace("<script>", "function methodA(){")
                script = script.replace("</script>", "}")
                script = script.replace("eval(", "return (")
                script = script.replace("\n", "")

                ctx = execjs.compile(script)
                temp = ctx.call("methodA")

                temp = temp.replace("while(window._phantom||window.__phantomas){};", "")
                temp = temp.replace(
                    "document.createElement('div');h.innerHTML='<a href=\\'/\\'>x</a>';h=h.firstChild.href",
                    "'"+url+"/'")
                temp = temp.replace(
                    "setTimeout('location.href=location.href.replace(/[\\?|&]captcha-challenge/,\\'\\')',1500);", "")
                temp = temp.replace(r"document.cookie=", "return ")
                temp = temp.replace(
                    r"if((function(){try{return !!window.addEventListener;}catch(e){return false;}})()){document.addEventListener('DOMContentLoaded',l,false);}else{document.attachEvent('onreadystatechange',l);}",
                    "")
                ctx = execjs.compile(str(temp))
                temp2 = str(ctx.call("l"))
                if "__jsl_clearance=" in temp2 :
                    return temp2[temp2.index("=")+1:temp2.index(";")]
                else:
                    return None
            except Exception as e:
                logging.exception(e)
                print ("jia su le err js run err!")
                return None
        else:
            return None

    @classmethod
    def remove(cls,province):
        JiaSuLe.jiaSuLe.clear()