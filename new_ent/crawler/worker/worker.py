# -*- coding: UTF-8 -*-

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
import queue
import threading

from crawler.utils.JiaSuLe import JiaSuLe
from crawler.utils.Geetest import Geetest
from crawler.utils.ADSL import ADSL
from crawler.utils.ProvinceRoute import ProvinceRoute
from crawler.utils.UserAgentRoute import UserAgentRoute
from crawler.parser.ListParser import ListParser
from crawler.parser.DetaiParser import DetailParser
from crawler.parser.DetailParser1 import DetailParser as DetailParser1
import crawler.utils.Config as Config
from crawler.utils.RequestHelper import RequestHeler
import logging


class TResult(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.exit = False
        self.queue = queue
        self.DBHerlper = Mysql()

    def run(self):
        while True :
            try:
                if self.exit:
                    for i in range(self.queue.qsize()):
                        tq = None
                        try:
                            tq = self.queue.get_nowait()
                        except:
                            continue
                        # 更新数据库的关键词状态、统计数据将统计结果保存到数据库
                        self.DBHerlper#???????
                    break
                length_ = self.queue.qsize()
                if length_ >= 1:
                    for i in range(length_):
                        tq = None
                        try:
                            tq = self.queue.get_nowait()
                        except:
                            continue

                        status = tq.get("status")
                        infov2s = tq.get("infov2s")
                        keyword = tq.get("keyword")
                        province = keyword.get("province")
                        if status ==3:
                            # 更新数据库的关键词状态、统计数据将统计结果保存到数据库
                            self.DBHerlper.insertBusinessInfo(infov2s, province)
                            self.DBHerlper.insertEnterpriseInfo(infov2s, province)
                            self.DBHerlper.insertReportInfo(infov2s, province)
                            self.DBHerlper.insertMainUrls(infov2s, province)
                            self.DBHerlper.updateKeywordState(keyword)
                            self.DBHerlper.insertCrawlerLog([{"project_name":"gsxt","machine_name":Config.MCNAME,"option":"crawler by keyword"}])
                        else:
                            self.DBHerlper.updateKeywordState(keyword)
                time.sleep(5)
            except Exception as e:
                logging.exception(e)


class TTask(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.exit = False
        self.redis = Redis(Config.RWQNAME,Config.RQUEUE)

    def run(self):
        while True:
            try:
                if self.exit:
                    for i in range(self.queue.qsize()):
                        pass
                    break
                length_ = self.queue.qsize()
                if length_ <= 3:
                    for i in range(6):
                        keyword = self.redis.get_nowait()
                        if keyword is not None:
                            try:
                                tk = json.loads(keyword)
                                tk["province"] = tk.get("province_id")
                                self.queue.put_nowait(tk)
                            except:
                                continue
                time.sleep(5)
            except Exception as e:
                logging.exception(e)


class Crawler(threading.Thread):

    def __init__(self, rQueue,tQueue):
        threading.Thread.__init__(self)
        self.resultQueue = rQueue
        self.taskQueue = tQueue

    def run(self):
        while True:
            try:
                keyword = None
                try:
                    keyword = self.taskQueue.get_nowait()
                    print("Crawler tQueue", self.taskQueue.qsize())
                    print("Crawler rQueue", self.resultQueue.qsize())
                except:
                    time.sleep(5)
                    continue
                if keyword is not None:
                    for i in range(3):
                        province = keyword.get("province")

                        # jsl = None
                        # for i in range(5):
                        #     jsl = JiaSuLe.getJiaSuLe(province)  # >>>>>>>>>>>>设计换ip
                        #     if jsl is not None:
                        #         break
                        # if jsl is None:
                        #     print("get jiaSuLe 5 time None")
                        #     ADSL.exe(province)  # 打印提示已经换IP
                        #     continue

                        geetest = None
                        for i in range(5):
                            # geetest = Geetest.getGeeTest(province, jsl)  # >>>>>>>>>>>>设计换ip
                            geetest = Geetest.getGeeTest(province)
                            if geetest is not None:
                                break
                        if geetest is None:
                            print("get geetest 5 time None")
                            ADSL.exe(province)  # 打印提示已经换IP
                            continue

                        if type(geetest) is str and geetest == 'IP Error':
                            print("IP Error!")
                            ADSL.exe(province)  # 打印提示已经换IP
                            continue

                        domain_url = ProvinceRoute.route(province)
                        userAgent = UserAgentRoute.ruote()

                        headers = {
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9",
                            "Cache-Control": "max-age=0",
                            "Connection": "keep-alive",
                            "X - Requested - With": "XMLHttpRequest"
                        }
                        cookies = {}
                        # if jsl is not None:
                        #     headers["Cookie"] = "__jsluid=" + jsl.get("__jsluid") + ";__jsl_clearance=" + jsl.get(
                        #         "__jsl_clearance")
                        #     cookies["__jsluid"] = jsl.get("__jsluid")
                        #     cookies["__jsl_clearance"] = jsl.get("__jsl_clearance")

                        if userAgent is not None:
                            headers["User-Agent"] = userAgent

                        searUrl = ""
                        if domain_url is not None and geetest is not None:
                            skeyword = keyword.get("keyword")
                            schallenge = geetest.get("challenge")
                            svalidate = geetest.get("validate")

                            # http://www.jsgsj.gov.cn:58888/province/jiangsu.jsp?typeName=36B3A1898D8C053C69E8521F161C6837&searchType=qyxx
                            searUrl = domain_url + "/corp-query-search-advancetest.html?tab=ent_tab&token=&province=&searchword=" + \
                                      skeyword + "&geetest_challenge=" + schallenge + "&geetest_validate=" + svalidate + "&geetest_seccode=" + svalidate + "|jordan&page=1"
                        print("province", province, "searUrl", searUrl)

                        r = RequestHeler.get(searUrl, headers=headers, timeout=Config.timeout)

                        if r is None:
                            continue

                        #<script>window.location.href='/index/invalidLink'</script>
                        if r.status_code == 502 or "由于您操作过于频繁" in r.text or r.text is None or "invalidLink" in r.text:
                            print("由于您操作过于频繁 invalidLink")
                            ADSL.exe(province,True)  # 打印提示已经换IP
                            continue
                        else:
                            # 提取cookie
                            for it in r.cookies.keys():
                                cookies[it] = r.cookies.get(it)

                            urls = ListParser.parser(r.text)
                            # 0未查找、1 查找失败、2 正在查找、3 查找找到、4 查找未找到
                            if urls is None:
                                keyword["success"] = 1  # program err
                                ru = {"keyword":keyword,"status":1,"infov2s":None}
                                self.resultQueue.put(ru)
                                print("program get list url error:",keyword.get("keyword"),keyword.get("id"))
                                ADSL.exe(province,True)  # 打印提示已经换IP
                                continue
                            elif type(urls) == str and urls == "not_found":
                                keyword["success"] = 4  # not found
                                ru = {"keyword": keyword, "status": 4, "infov2s": None}
                                self.resultQueue.put(ru)
                                print(keyword.get("keyword") + " not found")
                                break
                            else:
                                keyword["urls"] = urls
                                keyword["cookies"] = cookies
                                keyword["headers"] = headers
                                keyword["domain_url"] = domain_url
                                results = DetailParser.parser(keyword)
                                # results = DetailParser1.parser(keyword)
                                if results is None:
                                    keyword["success"] = 1  # program err
                                    ru = {"keyword": keyword, "status": 1, "infov2s": None}
                                    self.resultQueue.put(ru)
                                    print("DetailParser Error :",keyword.get("keyword"),keyword.get("id"))
                                elif isinstance(results, str) and results == "IP Error":
                                    print("IP Error  2")
                                    ADSL.exe(province,True)  # 打印提示已经换IP
                                    continue
                                else:
                                    kname = keyword.get("keyword")
                                    cname = results[0].get("business").get("base").get("name")
                                    if cname == kname:
                                        keyword["success"] = 5  # success
                                    else:
                                        keyword["success"] = 3  # success
                                    ru = {"keyword": keyword, "status": 3, "infov2s": results}
                                    self.resultQueue.put(ru)
                                    break
            except Exception as e:
                logging.exception(e)
                print("run Time Error!")

                # http://bj.gsxt.gov.cn/corp-query-search-advancetest.html?tab=ent_tab&searchword=%E5%86%9C%E4%B8%9A%E9%93%B6%E8%A1%8C&nowNum=&token=&page=1&geetest_seccode=973e80e76954c1596b8e1815c03d6708%7Cjordan&province=110000&geetest_validate=973e80e76954c1596b8e1815c03d6708&geetest_challenge=dda86bb4533420e70930e74715f9f972h3
                # 查询列表判断IP  statecode 502   ||  由于您操作过于频繁
                # 查找程序问题：1抛出异常2suceess3nontFound
                # parser :关键词相关信息，url,cookiejar

    #@1 fetch keyword<
    #@2 main url<
    #@3 jia shu le <
    #@4 gt&challenge<
    #@5 parser
    #@6 insert mysql<
    #@7 statistic(task queue)<
    #@8 adsl() <

if __name__ == "__main__":
    tqueue = queue.Queue()
    rqueue = queue.Queue()

    TTask = TTask(tqueue)
    TResult = TResult(rqueue)
    TTask.start()
    TResult.start()

    for i in  range(Config.thread):
        crawler = Crawler(rqueue, tqueue)
        crawler.start()