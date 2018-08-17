# -*- coding: utf-8 -*-
"""
@Time : 18-1-5 下午5:11
@Author : courage
@Site : 
@File : Geetest.py
@Software: PyCharm
"""

# 1 极验验证字典
# 2 判断验证是否有效
# 3 定时清理获取验证
# 4 统计验证规律

import time
import requests
import re
import json
from crawler.utils.ProvinceRoute import ProvinceRoute
from crawler.utils.UserAgentRoute import UserAgentRoute
import crawler.utils.Config as Config
import logging


class Geetest(object):

    geeDict={}

    @staticmethod
    def getGeeTest(province,jsl):
        # print("Geetest",Geetest.geeDict)
        # ru = {"gt": "62756445cd524543f5a16418cd920ffd", "challenge": "5d8e70ed5584260e689fc27607412846",
        #       "validate": "ec30bb23040eb9496a15c1afc058b160", "time": time.time()}
        # return ru

        if len(Geetest.geeDict)>0 :
            temp_list = []
            for k,v in Geetest.geeDict.items():
                if time.time()-v["time"]>7200:#300 半个小时
                    temp_list.append(k)
            for i in temp_list:
                Geetest.geeDict.pop(i)
        if Geetest.geeDict.get(str(province)) is not None :
            return Geetest.geeDict.get(str(province))
        else:
            # get gt@challenge

            # request Geetest API

            # put msg to geeDist

            #设计调用接口的统计方式

            for i in range(1):
                cookie = "__jsluid="+jsl.get("__jsluid")+"; __jsl_clearance="+jsl.get("__jsl_clearance")+";"
                uagent = UserAgentRoute.ruote()
                domain_url = ProvinceRoute.route(province)
                url = domain_url+'/SearchItemCaptcha?t='+str(int(time.time()+1000))
                resp = None
                try:
                    resp = http.get(url, headers={'Cookie': cookie, "User-Agent": uagent}, timeout=Config.timeout)
                except Exception as  e:
                    logging.exception(e)

                if resp is None or resp.text is None or resp.status_code != 200:
                    return "IP Error"
                jsonResult = resp.json()
                gt = jsonResult['gt']
                challenge = jsonResult['challenge']
                validate = None
                try:
                    validate = GetValidate(gt, challenge, domain_url)
                except Exception as e:
                    logging.exception(e)
                    validate = None
                    print("&&&&&&接口调用异常 time:",time.strftime('%Y-%m-%d',time.localtime(time.time())))
                if validate is not None and len(validate)>20:
                    #该打印方式是设计为统计接口成功调用次数,需要定期抽查返回的validate是否好使
                    print("@@@@@@","province:",province,"gt:",gt,"challenge:",challenge,"validate:",validate,"time:",time.strftime('%Y-%m-%d',time.localtime(time.time())))
                    ru = {"gt":gt,"challenge":challenge,"validate":validate,"time":time.time()}
                    Geetest.geeDict[str(province)] = ru
                    return ru
                else:
                    continue
            return None


user = 'b0df930d-57d6-42ea-981c-8aa52c4260da'

apiHttp = requests.Session()
http = requests.Session()
http.headers = {
    'User-Agent': None
}

# del http.headers['Accept-Encoding']
if http.headers.get("Accept-Encoding") is not None:
    http.headers.pop("Accept-Encoding")
    print(http.headers)

def GetParams(gt, challenge):
    apiResult = apiHttp.get('http://private.ashx.cn/geetest/getparams?gt=%s&challenge=%s' % (gt, challenge))
    return apiResult.json()


def GetFull(s, gt, challenge, key):
    headers = {'Content-Type': 'application/json'}
    apiResult = apiHttp.post('http://private.ashx.cn/geetest/fullInfo', headers=headers,
                             data=json.dumps({'s': s, 'gt': gt, 'challenge': challenge, 'key': key}))
    return apiResult.text


def GetClickData(picurl, s, gt, challenge, key):
    apiResult = apiHttp.post('http://api.ashx.cn/geetest/getclickdata',
                             data={'picurl': picurl, 's': s, 'challenge': challenge, 'gt': gt, 'key': key,
                                   'user': user})
    return apiResult.json()


def GetSlide3Data(fullbg, bg, ypos, s, gt, challenge):
    apiResult = apiHttp.post('http://api.ashx.cn/geetest/GetSlide3Data',
                             data={'fullbg': fullbg, 'ypos': ypos, 's': s, 'challenge': challenge, 'gt': gt, 'bg': bg,
                                   'user': user})
    return apiResult.json()


def ReportError(key):
    apiResult = apiHttp.post('http://api.ashx.cn/User/ReportError', data={'key': key, 'user': user})


def click(gt, challenge, key):
    resp = http.get(
        'http://api.geetest.com/get.php?is_next=true&type=click&gt=%s&challenge=%s&lang=zh-cn&https=false&protocol=http://&offline=false&product=popup&api_server=api.geetest.com' % (
        gt, challenge))
    text = resp.text[1:len(resp.text) - 1]
    jsonobj = json.loads(text)
    pic = jsonobj['data']['pic']
    s = jsonobj['data']['s']
    for i in range(5):
        apiResult = GetClickData(pic, s, gt, challenge, key)
        if (apiResult['Code'] == 0):
            resp = http.get('http://api.geetest.com/ajax.php?gt=%s&challenge=%s&w=%s&callback=geetest_' % (
            gt, challenge, apiResult['Data']))
            if (resp.text.find('validate') != -1):
                return re.findall(r"validate\x22\s*:\s*\x22(.+?)\x22", resp.text)[0]
            else:
                ReportError(apiResult['Key'])
        resp = http.get('http://api.geetest.com/refresh.php?gt=%s&challenge=%s&lang=zh-cn&type=click' % (gt, challenge))
        text = resp.text[1:len(resp.text) - 1]
        jsonobj = json.loads(text)
        pic = jsonobj['data']['pic']
    return ''


def slide3(gt, challenge, referer):
    resp = http.get(
        'http://api.geetest.com/get.php?is_next=true&type=slide3&gt=%s&challenge=%s&lang=zh-cn&https=false&offline=false&product=embed&api_server=api.geetest.com&callback=1' % (
        gt, challenge))
    text = resp.text[2:len(resp.text) - 1]
    jsonobj = json.loads(text)
    s = jsonobj['s']

    for i in range(4):
        challenge = jsonobj['challenge']
        apiResult = GetSlide3Data(jsonobj['fullbg'], jsonobj['bg'], jsonobj['ypos'], s, gt, challenge)
        if (apiResult['Code'] == 0):
            time.sleep(apiResult['PassTime'] / 1000)
            resp = http.get('http://api.geetest.com/ajax.php', headers={'Referrer': referer},
                            params={'gt': gt, 'challenge': challenge, 'w': apiResult['Data'], 'callback': 'geetest_1'})
            print(resp.text)
            if (resp.text.find('validate') != -1):
                return re.findall(r"validate\x22\s*:\s*\x22(.+?)\x22", resp.text)[0]
            else:
                ReportError(apiResult['Key'])
        if (i < 3):
            resp = http.get("http://api.geetest.com/refresh.php?gt=%s&challenge=%s&callback=1" % (gt, challenge))
            text = resp.text[2:len(resp.text) - 1]
            jsonobj = json.loads(text)
    return ''


def GetValidate(gt, challenge, referer):
    jsonResult = GetParams(gt, challenge)
    w = jsonResult['w']
    key = jsonResult['key']
    resp = http.get('http://api.geetest.com/get.php?gt=%s&challenge=%s&w=%s&callback=geetest_' % (gt, challenge, w))
    text = resp.text[9:len(resp.text) - 1]
    jsonobj = json.loads(text)
    s = jsonobj['data']['s']
    w = GetFull(s, gt, challenge, key)
    resp = http.get('http://api.geetest.com/ajax.php?gt=%s&challenge=%s&w=%s&callback=geetest_' % (gt, challenge, w))
    text = resp.text
    if (text.find('click') != -1):
        return click(gt, challenge, key)
    elif text.find('slide') != -1:
        return slide3(gt, challenge, referer)
    elif text.find('validate') != -1:
        return re.findall(r"validate\x22\s*:\s*\x22(.+?)\x22", text)[0]
