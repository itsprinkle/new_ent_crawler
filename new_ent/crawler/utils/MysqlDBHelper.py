# -*- coding: UTF-8 -*-

"""
@Time : 18-1-5 下午3:44
@Author : courage
@File : utils.py
@Software: PyCharm
"""

from crawler.utils.MySqlConn import MysqlCn
import crawler.utils.Config as Config
import json
import time

class Mysql(object):

    def __init__(self):
        pass

    def insertBusinessInfo(self,msgs,province):
        self._mysqlCn = MysqlCn()
        sql = "REPLACE INTO "+Config.bus+"(province,create_time,name,md5,type,regno,base,investors,changes,members,branchs,licenses,mortgages,pledges,punishs,abnormals,spot_checks) " \
              "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        for ttemp in msgs:
            temp = ttemp.get("business")
            province = province
            create_time = time.strftime("%Y-%m-%d", time.localtime())
            name = temp.get("base").get("name")
            #1 if 5>3 else 0  python 三目运算符
            md5 = self.md5(temp.get("base").get("credit_code")) if temp.get("base").get("credit_code") is not None else self.md5(temp.get("base").get("reg_no"))
            type = temp.get("base").get("type")
            regno = temp.get("base").get("reg_no")
            base = json.dumps(temp.get("base"))
            investors = json.dumps(temp.get("investors"))
            changes = json.dumps(temp.get("changes"))
            members = json.dumps(temp.get("members"))
            branchs = json.dumps(temp.get("branchs"))
            licenses = json.dumps(temp.get("licenses"))
            mortgages = json.dumps(temp.get("mortgages"))
            pledges = json.dumps(temp.get("pledges"))
            punishs = json.dumps(temp.get("punishs"))
            abnormals = json.dumps(temp.get("abnormals"))
            spot_checks = json.dumps(temp.get("spot_checks"))
            self._mysqlCn.insertOne(sql, (province,create_time,name,md5,type,regno,base,investors,changes,members,branchs,licenses,mortgages,pledges,punishs,abnormals,spot_checks))
        self._mysqlCn.dispose()

    def insertEnterpriseInfo(self,msgs, province):
        self._mysqlCn = MysqlCn()
        sql = "REPLACE INTO "+Config.ent+"(province,create_time,md5,investors,changes,stock_changes,licenses,intells,punishs) " \
              "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for ttemp in msgs:
            temp = ttemp.get("enterprise")
            province = province
            create_time = time.strftime("%Y-%m-%d", time.localtime())
            md5 = self.md5(ttemp.get("business").get("base").get("credit_code")) if ttemp.get("business").get("base").get("credit_code") is not None else self.md5(ttemp.get("business").get("base").get("reg_no"))
            investors = json.dumps(temp.get("investors"))
            changes = json.dumps(temp.get("changes"))
            stock_changes = json.dumps(temp.get("stock_changes"))
            licenses = json.dumps(temp.get("licenses"))
            intells = json.dumps(temp.get("intells"))
            punishs = json.dumps(temp.get("punishs"))
            self._mysqlCn.insertOne(sql, (province,create_time,md5,investors,changes,stock_changes,licenses,intells,punishs))
        self._mysqlCn.dispose()

    def insertReportInfo(self,msgs, province):
        self._mysqlCn = MysqlCn()
        sql1 = "REPLACE INTO "+Config.reprot+"(province,create_time,year,md5,date,`from`,general,operation,websites,licenses,branchs,invents,guarantees,investors,stockchanges,changes) " \
               "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for tttemp in msgs:
            ttemp = tttemp.get("enterprise").get("reports")
            if ttemp is not None:
                for temp in ttemp:
                    province=province
                    create_time = time.strftime("%Y-%m-%d", time.localtime())
                    year = temp.get("year")
                    md5 = self.md5(tttemp.get("business").get("base").get("credit_code")) if tttemp.get("business").get("base").get("credit_code") is not None else self.md5(tttemp.get("business").get("base").get("reg_no"))
                    date = temp.get("date")
                    tfrom = temp.get("from")
                    general = json.dumps(temp.get("general"))
                    operation = json.dumps(temp.get("operation"))
                    websites = json.dumps(temp.get("websites"))
                    licenses = json.dumps(temp.get("licenses"))
                    branchs = json.dumps(temp.get("branchs"))
                    invents = json.dumps(temp.get("invents"))
                    guarantees = json.dumps(temp.get("guarantees"))
                    investors = json.dumps(temp.get("investors"))
                    stockchanges = json.dumps(temp.get("stockchanges"))
                    changes = json.dumps(temp.get("changes"))
                    self._mysqlCn.insertOne(sql1, (province,create_time,year,md5,date,tfrom,general,operation,websites,licenses,branchs,invents,guarantees,investors,stockchanges,changes))
        self._mysqlCn.dispose()

    def insertMainUrls(self,msgs, province):
        self._mysqlCn = MysqlCn()
        sql = "REPLACE INTO "+Config.mainUrl+"(md5,company_name,main_url,province,create_time) " \
               "VALUES(%s,%s,%s,%s,%s)"
        for ttemp in msgs:
            temp = ttemp.get("business")
            province = province
            create_time = time.strftime("%Y-%m-%d", time.localtime())
            name = temp.get("base").get("name")
            #1 if 5>3 else 0  python 三目运算符
            md5 = self.md5(temp.get("base").get("credit_code")) if temp.get("base").get("credit_code") is not None else self.md5(temp.get("base").get("reg_no"))
            mainUrl = ttemp.get("main_url")
            self._mysqlCn.insertOne(sql, (md5,name,mainUrl,province,create_time))
        self._mysqlCn.dispose()

    def insertCrawlerLog(self,msgs):
        self._mysqlCn = MysqlCn()
        sql = "INSERT INTO crawler_log(project_name,machine_name,create_time,`option`,state) " \
               "VALUES(%s,%s,%s,%s,%s)"
        for ttemp in msgs:
            project_name = ttemp.get("project_name")
            machine_name = ttemp.get("machine_name")
            create_time = time.strftime("%Y-%m-%d", time.localtime())
            option = ttemp.get("option")
            state = 1
            self._mysqlCn.insertOne(sql, (project_name,machine_name,create_time,option,state))
        self._mysqlCn.dispose()

    # 查询关键字
    def queryKeyword(self,priority):
        self._mysqlCn = MysqlCn()
        sql = "SELECT keyword,province_id,crawler_count,id FROM "+Config.keyword+" WHERE `status`<2 AND priority = "+str(priority)+" AND province_id IS NOT NULL LIMIT 100;"
        # sql = "SELECT keyword,province_id,crawler_count,id FROM `go_keyword_info` WHERE province_id >0 and `status`<2 LIMIT 1000;"
        result = self._mysqlCn .getAll(sql)
        self._mysqlCn.dispose()
        return result




    def updateKeywordState(self,msgs):
        self._mysqlCn = MysqlCn()
        sql = "UPDATE "+Config.keyword+" SET `status`= %s,crawler_count =%s WHERE id = %s"
        # (2, int(keywords[i]["crawler_count"]), keywords[i]["id"])
        result = None
        if msgs is not None and isinstance(msgs, (list)):# type(msgs) is list
            lists = []
            for temp in msgs:
                lists.append((temp.get("success"),temp.get("crawler_count"),temp.get("id")))
            result = self._mysqlCn.updateMany(sql, lists)
        elif msgs is not None and isinstance(msgs, (dict)):#type(msgs) is dict
            result = self._mysqlCn.update(sql,(msgs.get("success"),msgs.get("crawler_count"),msgs.get("id")))
        self._mysqlCn.dispose()
        return result

    def md5(self,strs):
        import hashlib
        m = hashlib.md5()
        m.update(str(strs).encode("utf8"))
        return m.hexdigest()