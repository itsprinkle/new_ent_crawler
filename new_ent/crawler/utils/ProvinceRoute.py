# -*- coding: utf-8 -*-

"""
@Time : 18-1-5 下午3:44
@Author : courage
@File : utils.py
@Software: PyCharm
"""

class ProvinceRoute(object):

    urls = {
        "1": "http://ah.gsxt.gov.cn",
        "2": "http://bj.gsxt.gov.cn",
        "3": "http://fj.gsxt.gov.cn",
        "4": "http://gs.gsxt.gov.cn",
        "5": "http://gx.gsxt.gov.cn",
        "6": "http://hi.gsxt.gov.cn",
        "7": "http://he.gsxt.gov.cn",
        "8": "http://hl.gsxt.gov.cn",
        "9": "http://ha.gsxt.gov.cn",
        "10": "http://hb.gsxt.gov.cn",
        "11": "http://hn.gsxt.gov.cn",
        # "12": "http://js.gsxt.gov.cn",
        "12": "http://www.jsgsj.gov.cn:58888",
        "13": "http://jl.gsxt.gov.cn",
        "14": "http://ln.gsxt.gov.cn",
        "15": "http://nx.gsxt.gov.cn",
        "16": "http://qh.gsxt.gov.cn",
        "17": "http://sd.gsxt.gov.cn",
        "18": "http://sh.gsxt.gov.cn",
        "19": "http://sx.gsxt.gov.cn",
        "20": "http://tj.gsxt.gov.cn",
        "21": "http://xj.gsxt.gov.cn",
        "22": "http://xz.gsxt.gov.cn",
        "23": "http://yn.gsxt.gov.cn",
        "24": "http://www.gsxt.gov.cn",
        "25": "http://gd.gsxt.gov.cn",
        "26": "http://cq.gsxt.gov.cn",
        "27": "http://zj.gsxt.gov.cn",
        "28": "http://sc.gsxt.gov.cn",
        "29": "http://gz.gsxt.gov.cn",
        "30": "http://nm.gsxt.gov.cn",
        "31": "http://sn.gsxt.gov.cn",
        "32": "http://jx.gsxt.gov.cn"
    }

    @staticmethod
    def route(provinceId):
        if provinceId is not None :
            return ProvinceRoute.urls.get(str(provinceId))
        else:
            return ""