# -*- coding: utf-8 -*-
"""
@Time : 18-1-9 下午2:14
@Author : courage
@Site : 
@File : DetaiParser.py
@Software: PyCharm
"""

import json
from lxml import html
from crawler.parser import Entity
import re
import time
import crawler.utils.Config as Config
from crawler.utils.UserAgentRoute import UserAgentRoute
import logging

from crawler.utils.RequestHelper import headers as Headers
from crawler.utils.RequestHelper import RequestHeler

from threading import Thread


class DetailParser(object):

    @classmethod
    def parser(cls, keyword):
        list_urls = keyword.get("urls")
        headers = keyword.get("headers")
        cookies = keyword.get("cookies")
        domain_url = keyword.get("domain_url")

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }

        for i in range(4):
            # JSESSIONID=1AAC7947400C34708519E55C965907ED-n1:8
            # 为了正常获取年报信息 在这通过该请求获取jsessionId http://sh.gsxt.gov.cn/SearchItemCaptcha?t=1516101418799
            geetestUrl = domain_url + "/SearchItemCaptcha?t=" + str(int(round(time.time() * 1000)))
            # cookies 处理
            headers["Cookie"] = fromCookiesToStr(cookies)
            r = RequestHeler.get(geetestUrl, headers=headers, timeout=Config.timeout)
            if r is not None and r.cookies.get("JSESSIONID") is not None:
                cookies["JSESSIONID"] = r.cookies.get("JSESSIONID")

        keyword["cookies"] = cookies
        # cookies 处理
        headers["Cookie"] = fromCookiesToStr(cookies)

        infov2s = []

        for url in list_urls:
            """
                    // 工商局信息
                    type BusinessInfo struct {
                        Base       BaseInfo        `json:"base"`
                        Investors  []InvestorInfo  `json:"investors"`
                        Changes    []ChangeInfo    `json:"changes"`
                        Members    []MemberInfo    `json:"members"`
                        Branchs    []BranchInfo    `json:"branchs"`
                        Licenses   []LicenseInfo   `json:"licenses"`
                        Mortgages  []MortgageInfo  `json:"mortgages"`
                        Pledges    []PledgeInfo    `json:"pledges"`
                        Punishs    []PunishInfo    `json:"punishs"`
                        Abnormals  []AbnormalInfo  `json:"abnormals"`
                        SpotChecks []SpotCheckInfo `json:"spot_checks"`
                    }
            """

            business = {}
            enterprise = {}

            # 营业执照信息             从主页面html解析获取
            response = RequestHeler.get(domain_url + url, retry=6, headers=headers, timeout=Config.timeout)

            if response is None or response.status_code != 200:
                if response is None:
                    print("公司主页面获取失败,请求异常 :", keyword.get("keyword"))
                else:
                    print("公司主页面获取失败,状态码异常 :", keyword.get("keyword"), response.status_code)
                continue

            if response.status_code == 200 and len(response.text) == 0 or "invalidLink" in response.text:
                return "IP Error"

            base = getBusBaseInfo(response.text)
            business["base"] = EntityTimeFormat(base, "busBase")
            urls = getUrls(response.text)
            if urls is None or len(urls) < 10:
                print("从公司主页面源码获取各个详情url失败!")
                continue

            # 营业执照信息 第二次请求，猜想和是否可完整请求数据有关联----测试中
            response = RequestHeler.get(domain_url + url, retry=1, headers=headers, timeout=Config.timeout)

            # 变更信息                从主页面html解析获取url进行再请求提取
            busChange = MainThread("busChange",urls,keyword)
            # 列入经营异常名录信息         从主页面html解析获取url进行再请求提取
            busAbnormal = MainThread("busAbnormal", urls, keyword)
            # 行政处罚信息                 从主页面html解析获取url进行再请求提取
            entPunish = MainThread("entPunish", urls, keyword)
            # 企业年报信息                 从主页面html解析获取url进行再请求提取
            entAnCheYearInfo = MainThread("entAnCheYearInfo", urls, keyword)
            # 股东及出资信息            从主页面html解析获取url进行再请求提取
            busShareholder = MainThread("busShareholder", urls, keyword)
            # 主要人员信息             从主页面html解析获取url进行再请求提取
            busMemberInfo = MainThread("busMemberInfo", urls, keyword)
            # 分支机构信息             从主页面html解析获取url进行再请求提取
            busBranchInfo = MainThread("busBranchInfo", urls, keyword)
            # 动产抵押登记信息          从主页面html解析获取url进行再请求提取
            busMortgageInfo = MainThread("busMortgageInfo", urls, keyword)
            # 股权出质登记信息          从主页面html解析获取url进行再请求提取
            busSockPlegeInfo = MainThread("busSockPlegeInfo", urls, keyword)
            # 抽查检查结果信息           从主页面html解析获取url进行再请求提取
            busSpotCheck = MainThread("busSpotCheck", urls, keyword)
            # 行政处罚信息                从主页面html解析获取url进行再请求提取
            busPunish = MainThread("busPunish", urls, keyword)
            # 行政许可信息                从主页面html解析获取url进行再请求提取
            busLicence = MainThread("busLicence", urls, keyword)

            busChange.start()
            busAbnormal.start()
            entPunish.start()
            entAnCheYearInfo.start()
            busShareholder.start()
            busMemberInfo.start()
            busBranchInfo.start()
            busMortgageInfo.start()
            busSockPlegeInfo.start()
            busSpotCheck.start()
            busPunish.start()
            busLicence.start()

            busChange.join()
            busAbnormal.join()
            entPunish.join()
            entAnCheYearInfo.join()
            busShareholder.join()
            busMemberInfo.join()
            busBranchInfo.join()
            busMortgageInfo.join()
            busSockPlegeInfo.join()
            busSpotCheck.join()
            busPunish.join()
            busLicence.join()

            business["changes"] = busChange.get_result()
            business["abnormals"] = busAbnormal.get_result()
            enterprise["punishs"] = entPunish.get_result()
            enterprise["reports"] = entAnCheYearInfo.get_result()
            business["investors"] = busShareholder.get_result()
            business["members"] = busMemberInfo.get_result()
            business["branchs"] = busBranchInfo.get_result()
            business["mortgages"] = busMortgageInfo.get_result()
            business["pledges"] = busSockPlegeInfo.get_result()
            business["spot_checks"] = busSpotCheck.get_result()
            business["punishs"] = busPunish.get_result()
            business["licenses"] = busLicence.get_result()

            """
            // 企业公示信息
            type EnterpriseInfo struct {
                Reports      []ReportInfo      `json:"reports"`
                Investors    []InvestorInfo    `json:"investors"`
                Changes      []ChangeInfo      `json:"changes"`
                StockChanges []StockChangeInfo `json:"stock_changes"`
                Licenses     []LicenseInfo     `json:"licenses"`
                Intells      []IntellInfo      `json:"intells"`
                Punishs      []PunishInfo      `json:"punishs"`
            }
            """
            # 股东及出资信息                从主页面html解析获取url进行再请求提取
            entInsInvinfo = MainThread("entInsInvinfo",urls,keyword)
            # 股权变更信息                 从主页面html解析获取url进行再请求提取
            entStockChange = MainThread("entStockChange", urls, keyword)
            # 行政许可信息                 从主页面html解析获取url进行再请求提取
            entLicence = MainThread("entLicence", urls, keyword)
            # 知识产权出质登记信息            从主页面html解析获取url进行再请求提取
            entItelPlege = MainThread("entItelPlege", urls, keyword)

            entInsInvinfo.start()
            entStockChange.start()
            entLicence.start()
            entItelPlege.start()

            entInsInvinfo.join()
            entStockChange.join()
            entLicence.join()
            entItelPlege.join()

            enterprise["investors"] = entInsInvinfo.get_result()
            enterprise["stock_changes"] = entStockChange.get_result()
            enterprise["licenses"] = entLicence.get_result()
            enterprise["intells"] = entItelPlege.get_result()

            """
            type InfoV2 struct {
                Business   BusinessInfo   `json:"business"`
                Enterprise EnterpriseInfo `json:"enterprise"`
            }
            """
            infov2 = {}
            infov2["business"] = business
            infov2["enterprise"] = enterprise
            infov2["main_url"] = url

            if base.get("name") is not None:
                infov2s.append(infov2)

        if len(infov2s) > 0:
            return infov2s
        else:
            return None


class MainThread(Thread):

    def __init__(self, type, urls, keyword):
        Thread.__init__(self)
        self.type = type
        self.urls = urls
        self.keyword = keyword

    def run(self):
        if "busChange" == self.type:
            # 变更信息                从主页面html解析获取url进行再请求提取
            alterInfoUrl = self.urls.get("alterInfoUrl")
            changes = extract(Entity.busChange, alterInfoUrl, self.keyword, "post", "bus变更信息")
            changes = formatChange(changes)
            changes = EntityTimeFormat(changes)
            self.result = changes
        elif "busAbnormal" == self.type:
            # 列入经营异常名录信息         从主页面html解析获取url进行再请求提取
            entBusExcepUrl = self.urls.get("entBusExcepUrl")
            abnormals = extract(Entity.busAbnormal, entBusExcepUrl, self.keyword, "post", "bus列入经营异常名录信息")
            abnormals = EntityTimeFormat(abnormals)
            self.result = abnormals
        elif "busShareholder" == self.type:
            # 股东及出资信息            从主页面html解析获取url进行再请求提取
            shareholderUrl = self.urls.get("shareholderUrl")
            investors = getInvester("bus", shareholderUrl, self.keyword, "bus股东及出资信息")
            investors = EntityTimeFormat(investors, "invester")
            investors = formatInvester(investors)
            self.result = investors
        elif "busMemberInfo" == self.type:
            # 主要人员信息             从主页面html解析获取url进行再请求提取
            keyPersonUrl = self.urls.get("keyPersonUrl")
            members = graphExtract(Entity.busMemberInfo, keyPersonUrl, self.keyword, "get", "bus主要人员信息")
            members = formatMembers(members)
            members = EntityTimeFormat(members)
            self.result = members
        elif "busBranchInfo" == self.type:
            # 分支机构信息             从主页面html解析获取url进行再请求提取
            branchUrl = self.urls.get("branchUrl")
            branchs = graphExtract(Entity.busBranchInfo, branchUrl, self.keyword, "get", "bus分支机构信息")
            branchs = EntityTimeFormat(branchs)
            self.result = branchs
        elif "busMortgageInfo" == self.type:
            # 动产抵押登记信息          从主页面html解析获取url进行再请求提取
            mortRegInfoUrl = self.urls.get("mortRegInfoUrl")
            mortgages = getMortgageInfo(Entity.busMortgageInfo, mortRegInfoUrl, self.keyword, "bus动产抵押登记信息")
            mortgages = EntityStataFormat(mortgages)
            mortgages = EntityTimeFormat(mortgages, "busMort")
            self.result = mortgages
        elif "busSockPlegeInfo" == self.type:
            # 股权出质登记信息          从主页面html解析获取url进行再请求提取
            stakQualitInfoUrl = self.urls.get("stakQualitInfoUrl")
            pledges = extract(Entity.busSockPlegeInfo, stakQualitInfoUrl, self.keyword, "post", "bus股权出质登记信息")
            pledges = EntityStataFormat(pledges)
            pledges = EntityTimeFormat(pledges)
            self.result = pledges
        elif "busSpotCheck" == self.type:
            # 抽查检查结果信息           从主页面html解析获取url进行再请求提取
            spotCheckInfoUrl = self.urls.get("spotCheckInfoUrl")
            spot_checks = extract(Entity.busSpotCheck, spotCheckInfoUrl, self.keyword, "post", "bus抽查检查结果信息")
            spot_checks = EntityStataFormat(spot_checks, "spotcheck")
            spot_checks = EntityTimeFormat(spot_checks)
            self.result = spot_checks
        elif "busPunish" == self.type:
            # 行政处罚信息                从主页面html解析获取url进行再请求提取
            punishmentDetailInfoUrl = self.urls.get("punishmentDetailInfoUrl")
            punishs = extract(Entity.busPunish, punishmentDetailInfoUrl, self.keyword, "get", "bus行政处罚信息")
            punishs = EntityTimeFormat(punishs)
            self.result = punishs
        elif "busLicence" == self.type:
            # 行政许可信息                从主页面html解析获取url进行再请求提取
            otherLicenceDetailInfoUrl = self.urls.get("otherLicenceDetailInfoUrl")
            licenses = extract(Entity.busLicence, otherLicenceDetailInfoUrl, self.keyword, "post", "bus行政许可信息")
            licenses = EntityStataFormat(licenses)
            licenses = EntityTimeFormat(licenses)
            self.result = licenses

        elif "entPunish" == self.type:
            # 行政处罚信息                 从主页面html解析获取url进行再请求提取
            insPunishmentinfoUrl = self.urls.get("insPunishmentinfoUrl")
            punishs = extract(Entity.entPunish, insPunishmentinfoUrl, self.keyword, "post", "ent行政处罚信息")
            punishs = EntityTimeFormat(punishs)
            self.result = punishs
        elif "entAnCheYearInfo" == self.type:
            # 企业年报信息                 从主页面html解析获取url进行再请求提取
            anCheYearInfo = self.urls.get("anCheYearInfo")
            reports = getReports(anCheYearInfo, self.keyword, "ent企业年报信息")
            reports = EntityTimeFormat(reports)
            self.result = reports
        elif "entInsInvinfo" == self.type:
            # 股东及出资信息                从主页面html解析获取url进行再请求提取
            insInvinfoUrl = self.urls.get("insInvinfoUrl")
            investors = getInvester("ent", insInvinfoUrl, self.keyword, "ent股东及出资信息")
            investors = EntityTimeFormat(investors, "invester")
            self.result = investors
        elif "entStockChange" == self.type:
            # 股权变更信息                 从主页面html解析获取url进行再请求提取
            insAlterstockinfoUrl = self.urls.get("insAlterstockinfoUrl")
            stock_changes = extract(Entity.entStockChange, insAlterstockinfoUrl, self.keyword, "post", "ent股权变更信息")
            stock_changes = EntityTimeFormat(stock_changes)
            self.result = stock_changes
        elif "entLicence" == self.type:
            # 行政许可信息                 从主页面html解析获取url进行再请求提取
            insLicenceinfoUrl = self.urls.get("insLicenceinfoUrl")
            licenses = extract(Entity.entLicence, insLicenceinfoUrl, self.keyword, "post", "ent行政许可信息")
            licenses = EntityStataFormat(licenses)
            licenses = EntityTimeFormat(licenses)
            self.result = licenses
        elif "entItelPlege" == self.type:
            # 知识产权出质登记信息            从主页面html解析获取url进行再请求提取
            insProPledgeRegInfoUrl = self.urls.get("insProPledgeRegInfoUrl")
            intells = extract(Entity.entItelPlege, insProPledgeRegInfoUrl, self.keyword, "post", "ent知识产权出质登记信息")
            intells = EntityStataFormat(intells)
            intells = EntityTimeFormat(intells)
            self.result = intells

    def get_result(self):
        return self.result


def getReports(url, keyword, modelname):
    """
    // 年报信息
    type ReportInfo struct {
        Year         string            `json:"year" key:"年度" sd:"ancheyear"`
        Date         string            `json:"date" key:"日期" sd:"firstpubtime"`
        From         string            `json:"from" key:"纸质年报"`
        General      GeneralInfo       `json:"general"`
        Operation    OperationInfo     `json:"operation"`
        Websites     []WebsiteInfo     `json:"websites"`
        Licenses     []LicenseInfo     `json:"licenses"`
        Branchs      []BranchInfo      `json:"branchs"`
        InvEnts      []InvEntInfo      `json:"inv_ents"`
        Guarantees   []GuaranteeInfo   `json:"guarantees"`
        Investors    []InvestorInfo    `json:"investors"`
        StockChanges []StockChangeInfo `json:"stock_changes"`
        Changes      []ChangeInfo      `json:"changes"`
    }
    """
    reports = []

    headers = keyword.get("headers")
    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # cookies 处理
    headers["Cookie"] = fromCookiesToStr(cookies)

    # 解决年报404
    response = None
    for i in range(50):
        response = RequestHeler.get(domain_url + url, headers=headers, timeout=Config.timeout)
        if response is None or response.status_code != 200:
            continue
        elif response.status_code == 200:
            break
        elif i >= 50:
            print("年报50请求没有结果!")
            return None

    if response is None or response.status_code != 200:
        return None

    try:
        message = json.loads(response.text)
    except Exception as e:
        logging.exception(e)
        return None
    if isinstance(message, list) == False:
        return None

    # 获取年报基本信息
    for tmsg in message:
        report = {}
        report["year"] = tmsg.get("anCheYear")
        report["date"] = tmsg.get("anCheDate")
        report["from"] = tmsg.get("annRepFrom")

        # 基本信息 #企业资产状况
        annBase = repThread("reGeneral", tmsg, keyword)
        # 股东及出资信息
        sponsor = repThread("reInvestors", tmsg, keyword)
        # 对外提供保证担保信息
        forGuaranteeinfo = repThread("reGuarteen", tmsg, keyword)
        # 修改信息
        alter = repThread("reChange", tmsg, keyword)
        # 网站或网店信息
        webSiteInfo = repThread("reWebsite", tmsg, keyword)
        # 对外投资信息
        forInvestmen = repThread("reInvestEnt", tmsg, keyword)
        # 股权变更信息
        alterStockInfo = repThread("reStockChange", tmsg, keyword)
        # 分支机构信息
        vAnnualReportSfcBranch = repThread("reBranch", tmsg, keyword)
        # 行政许可信息
        annulLicence = repThread("reLicence", tmsg, keyword)

        annBase.start()
        sponsor.start()
        forGuaranteeinfo.start()
        alter.start()
        webSiteInfo.start()
        forInvestmen.start()
        alterStockInfo.start()
        vAnnualReportSfcBranch.start()
        annulLicence.start()

        annBase.join()
        sponsor.join()
        forGuaranteeinfo.join()
        alter.join()
        webSiteInfo.join()
        forInvestmen.join()
        alterStockInfo.join()
        vAnnualReportSfcBranch.join()
        annulLicence.join()

        report["general"] = annBase.get_result()
        report["operation"] = annBase.get_operation()
        report["investors"] = sponsor.get_result()
        report["guarantees"] = forGuaranteeinfo.get_result()
        report["changes"] = alter.get_result()
        report["websites"] = webSiteInfo.get_result()
        report["inv_ents"] = forInvestmen.get_result()
        report["stock_changes"] = alterStockInfo.get_result()
        report["branchs"] = vAnnualReportSfcBranch.get_result()
        report["licenses"] = annulLicence.get_result()

        if report.get("year") is not None:
            reports.append(report)
    return reports


class repThread(Thread):

    def __init__(self, type, tmsg, keyword):
        Thread.__init__(self)
        self.type = type
        self.tmsg = tmsg
        self.keyword = keyword

    def run(self):
        if "reGeneral" == self.type:
            annBaseUrl = getReprotDetailUlr(self.tmsg, "annBaseUrl")
            general, operation = getReportBaseInfo(annBaseUrl, self.keyword, "rep基本信息\企业资产状况")
            self.result = EntityTimeFormat(general)
            self.operation = EntityTimeFormat(operation)
        if "reInvestors" == self.type:
            # 股东及出资信息
            sponsorUrl = getReprotDetailUlr(self.tmsg, "sponsorUrl")
            investors = getInvester("rep", sponsorUrl, self.keyword, "rep股东及出资信息")
            self.result = EntityTimeFormat(investors, "invester")
        if "reGuarteen" == self.type:
            # 对外提供保证担保信息
            forGuaranteeinfoUrl = getReprotDetailUlr(self.tmsg, "forGuaranteeinfoUrl")
            guarantees = extract(Entity.reGuarteen, forGuaranteeinfoUrl, self.keyword, "post", "rep对外提供保证担保信息")
            self.result = EntityTimeFormat(guarantees)
        if "reChange" == self.type:
            # 修改信息
            alterUrl = getReprotDetailUlr(self.tmsg, "alterUrl")
            changes = extract(Entity.reChange, alterUrl, self.keyword, "get", "rep修改信息")
            self.result = EntityTimeFormat(changes)
        if "reWebsite" == self.type:
            # 网站或网店信息
            webSiteInfoUrl = getReprotDetailUlr(self.tmsg, "webSiteInfoUrl")
            websites = graphExtract(Entity.reWebsite, webSiteInfoUrl, self.keyword, "get", "rep网站或网店信息")
            websites = EntityStataFormat(websites, "web")
            self.result = EntityTimeFormat(websites)
        if "reInvestEnt" == self.type:
            # 对外投资信息
            forInvestmentUrl = getReprotDetailUlr(self.tmsg, "forInvestmentUrl")
            inv_ents = graphExtract(Entity.reInvestEnt, forInvestmentUrl, self.keyword, "get", "rep对外投资信息")
            self.result = EntityTimeFormat(inv_ents)
        if "reStockChange" == self.type:
            # 股权变更信息
            alterStockInfoUrl = getReprotDetailUlr(self.tmsg, "alterStockInfoUrl")
            stock_changes = extract(Entity.reStockChange, alterStockInfoUrl, self.keyword, "get", "rep股权变更信息")
            self.result = EntityTimeFormat(stock_changes)
        if "reBranch" == self.type:
            # 分支机构信息
            vAnnualReportSfcBranchUrl = getReprotDetailUlr(self.tmsg, "vAnnualReportSfcBranchUrl")
            branchs = graphExtract(Entity.reBranch, vAnnualReportSfcBranchUrl, self.keyword, "get", "rep分支机构信息")
            self.result = EntityTimeFormat(branchs)
        if "reLicence" == self.type:
            # 行政许可信息
            annulLicenceUrl = getReprotDetailUlr(self.tmsg, "annulLicenceUrl")
            licenses = extract(Entity.reLicence, annulLicenceUrl, self.keyword, "post", "rep行政许可信息")
            licenses = EntityStataFormat(licenses)
            self.result = EntityTimeFormat(licenses)

    def get_result(self):
        return self.result

    def get_operation(self):
        return self.operation


# 工商公示、企业公示、年报公示 都有股东出资 但是返回格式都不一样 需要特殊处理
def getInvester(type, url, keyword, modelname):

    headers = keyword.get("headers")
    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")
    # cookies 处理
    headers["Cookie"] = fromCookiesToStr(cookies)
    if url is None or len(url) == 0:
        print(modelname, "url 为空")
        return None
    if type == "bus":
        model = Entity.busInvesterInfo
        item = []

        data = {
            "draw": 1,
            "start": 0,
            "length": 5
        }
        count = 1
        while True:
            response = RequestHeler.post(domain_url + url, data, headers=headers, timeout=Config.timeout)
            if response is None or response.status_code != 200:
                if response is None:
                    print(modelname + " request Exception :" + " " + keyword.get("keyword"))
                else:
                    print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
                return None

            try:
                message1 = json.loads(response.text)
            except Exception as e:
                logging.exception(e)
                return None

            totalPage = message1.get("totalPage")
            message = message1

            if message1.get("data") is not None:
                message = message1.get("data")

            if len(message) > 0:
                for tmsg in message:
                    temp = {}
                    """
                    "type": "invType_CN",
                    "name": "inv",
                    "cert_type": "cerType_CN",
                    "cert_no": "bLicNo",
                    "sub_capi": "liSubConAm",
                    "act_capi": "liAcConAm",
                    """
                    temp["type"] = removeHtml(tmsg.get("invType_CN"))
                    temp["name"] = removeHtml(tmsg.get("inv"))
                    temp["cert_type"] = removeHtml(tmsg.get("cerType_CN"))
                    temp["cert_no"] = getNumFromStr(tmsg.get("bLicNo"))
                    temp["sub_capi"] = tmsg.get("liSubConAm")
                    temp["act_capi"] = tmsg.get("liAcConAm")

                    item.append(temp)
            if totalPage is None:
                break
            elif totalPage == 1 or totalPage == 0:
                break
            elif totalPage > 1 and count >= totalPage:
                break
            else:
                data["start"] = count * 5
                count = count + 1
                data["draw"] = count
        if len(item) > 0:
            return item
        else:
            return None
    elif type == "ent":
        model = Entity.entInvester
        item = []

        data = {
            "draw": 1,
            "start": 0,
            "length": 5
        }
        count = 1
        while True:
            response = RequestHeler.post(domain_url + url, data, headers=headers, timeout=Config.timeout)
            if response is None or response.status_code != 200:
                if response is None:
                    print(modelname + " request Exception :" + " " + keyword.get("keyword"))
                else:
                    print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
                return None

            try:
                message1 = json.loads(response.text)
            except Exception as e:
                logging.exception(e)
                return None

            totalPage = message1.get("totalPage")
            message = message1
            if message1.get("data") is not None:
                message = message1.get("data")
            if len(message) > 0:
                for tmsg in message:
                    temp = {}
                    for tmodel in model:
                        temp[tmodel] = tmsg.get(model.get(tmodel))
                    subDetails = tmsg.get("subDetails")
                    if subDetails is not None and len(subDetails) > 0:
                        subs = []
                        for tsub in subDetails:
                            sub = {}
                            sub["type"] = tsub.get("subConForm_CN")
                            sub["capi"] = tsub.get("subConAmStr")
                            sub["date"] = tsub.get("currency")
                            subs.append(sub)
                        temp["subs"] = subs
                    aubDetails = tmsg.get("aubDetails")
                    if aubDetails is not None and len(subDetails) > 0:
                        acts = []
                        for tact in aubDetails:
                            act = {}
                            act["type"] = tsub.get("acConFormName")
                            act["capi"] = tsub.get("acConAmStr")
                            act["date"] = tsub.get("conDate")
                            acts.append(act)
                        temp["acts"] = acts
                    item.append(temp)
            if totalPage is None:
                break
            elif totalPage == 1 or totalPage == 0:
                break
            elif totalPage > 1 and count >= totalPage:
                break
            else:
                data["start"] = count * 5
                count = count + 1
                data["draw"] = count
        if len(item) > 0:
            return item
        else:
            return None
    elif type == "rep":
        model = Entity.reInvester
        item = []

        data = {
            "draw": 1,
            "start": 0,
            "length": 5
        }
        count = 1
        while True:
            response = RequestHeler.post(domain_url + url, data, headers=headers, timeout=Config.timeout)
            if response is None or response.status_code != 200:
                if response is None:
                    print(modelname + " request Exception :" + " " + keyword.get("keyword"))
                else:
                    print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
                return None

            try:
                message1 = json.loads(response.text)
            except Exception as e:
                logging.exception(e)
                return None

            totalPage = message1.get("totalPage")
            message = message1
            if message1.get("data") is not None:
                message = message1.get("data")
            if len(message) > 0:
                for tmsg in message:
                    temp = {}
                    for tmodel in model:
                        temp[tmodel] = tmsg.get(model.get(tmodel))
                    subs = []
                    acts = []
                    sub = {}
                    act = {}
                    sub["type"] = tmsg.get("subConFormName")
                    sub["capi"] = tmsg.get("liSubConAm")
                    sub["date"] = tmsg.get("subConDate")
                    subs.append(sub)
                    temp["subs"] = subs
                    act["type"] = tmsg.get("acConForm_CN")
                    act["capi"] = tmsg.get("liAcConAm")
                    act["date"] = tmsg.get("acConDate")
                    acts.append(act)
                    temp["acts"] = acts
                    item.append(temp)
            if totalPage is None:
                break
            elif totalPage == 1 or totalPage == 0:
                break
            elif totalPage > 1 and count >= totalPage:
                break
            else:
                data["start"] = count * 5
                count = count + 1
                data["draw"] = count
        if len(item) > 0:
            return item
        else:
            return None


def getMortgageInfo(model, url, keyword, modelname):
    if url is None or len(url) == 0:
        print(modelname, "url 为空")
        return None

    headers = keyword.get("headers")
    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")
    # cookies 处理
    headers["Cookie"] = fromCookiesToStr(cookies)

    personUrl = "/corp-query-entprise-info-mortregpersoninfo-"
    pawnUrl = "/corp-query-entprise-info-mortGuaranteeInfo-"
    mortMsgUlr = "/corp-query-entprise-info-mortCreditorRightInfo-"
    item = []

    data = {
        "draw": 1,
        "start": 0,
        "length": 5
    }
    count = 1
    while True:
        response = RequestHeler.post(domain_url + url, data, headers=headers, timeout=Config.timeout)
        if response is None or response.status_code != 200:
            if response is None:
                print(modelname + " request Exception :" + " " + keyword.get("keyword"))
            else:
                print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
            return None

        try:
            message1 = json.loads(response.text)
        except Exception as e:
            logging.exception(e)
            return None

        totalPage = message1.get("totalPage")
        message = message1
        if message1.get("data") is not None:
            message = message1.get("data")
        if len(message) > 0:
            for tmsg in message:
                temp = {}
                for tmodel in model:
                    temp[tmodel] = tmsg.get(model.get(tmodel))

                mortId = tmsg.get("morReg_Id")

                tpersonUrl = domain_url + personUrl + mortId + ".html"
                tResponse = RequestHeler.get(tpersonUrl, headers=headers, timeout=Config.timeout)

                try:
                    message = json.loads(tResponse.text).get("data")
                except Exception as e:
                    logging.exception(e)
                    return None

                if len(message) > 0:
                    mortgagers = []
                    for tmsg in message:
                        mortgager = {}
                        mortgager["name"] = tmsg.get("more")
                        mortgager["cert_type"] = tmsg.get("bLicType_CN")
                        mortgager["cert_no"] = tmsg.get("bLicNo")
                        mortgager["address"] = tmsg.get("")
                        mortgagers.append(mortgager)
                    temp["mortgagers"] = mortgagers

                tpawnUrl = domain_url + pawnUrl + mortId + ".html"
                tResponse = RequestHeler.get(tpawnUrl, headers=headers, timeout=Config.timeout)

                try:
                    message = json.loads(tResponse.text).get("data")
                except Exception as e:
                    logging.exception(e)
                    return None

                if len(message) > 0:
                    pawns = []
                    for tmsg in message:
                        pawn = {}
                        pawn["name"] = tmsg.get("guaName")
                        pawn["owner"] = tmsg.get("own")
                        pawn["status"] = tmsg.get("guaDes")
                        pawn["remark"] = tmsg.get("remark")
                        pawns.append(pawn)
                    temp["pawns"] = pawns

                tmortMsgUlr = domain_url + mortMsgUlr + mortId + ".html"
                tResponse = RequestHeler.get(tmortMsgUlr, headers=headers, timeout=Config.timeout)

                try:
                    message = json.loads(tResponse.text).get("data")
                except Exception as e:
                    logging.exception(e)
                    return None

                if len(message) > 0:
                    for tmsg in message:
                        obligee = {}
                        obligee["kind"] = tmsg.get("priClaSecKind_CN")
                        obligee["amount"] = tmsg.get("priClaSecAm")
                        obligee["scope"] = tmsg.get("warCov")
                        obligee["debt_term"] = tmsg.get("pefPerForm-pefPerTo")
                        obligee["remark"] = tmsg.get("remark")
                        temp["obligee"] = obligee
                item.append(temp)
        if totalPage is None:
            break
        elif totalPage == 1 or totalPage == 0:
            break
        elif totalPage > 1 and count >= totalPage:
            break
        else:
            data["start"] = count * 5
            count = count + 1
            data["draw"] = count
    if len(item) > 0:
        return item
    else:
        return None


def extract(model, url, keyword, http_type, modelname=""):
    item = []

    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")
    # cookies 处理
    Cookie = fromCookiesToStr(cookies)

    if url is None or len(url) == 0:
        print(modelname, "url 为空")
        return None
    data = {
        "draw": 1,
        "start": 0,
        "length": 5
    }
    count = 1
    while True:
        response = None
        # 循环设计解决变更数据不能正常返回
        for i in range(20):
            if http_type == "post":
                """
                Cookie:__jsluid=2d90464be28a6246dd87bedf148a3db9; __jsl_clearance=1516693332.365|0|pVl0%2FgM7q5P6nxKLfu0eC0J7JgI%3D; UM_distinctid=16121fa27263b0-03427426140f7-5b452a1d-e1000-16121fa2727581; tlb_cookie=S172.16.12.68; JSESSIONID=3C0E3EE254774AF7EC29C23BB0762DB3-n1:9; gsxtBrowseHistory1=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219%40FDDDDEBDDDDDD%40MGCLLMFAESXS%11%1A%00%1A%15%19%11SNS%E6%B8%A2%E5%8D%A3%E5%B1%BB%E7%B0%87%E9%94%8B%E6%B0%AB%E4%BB%93%E4%B9%AE%E5%9E%8E%E9%86%A5%E5%91%BC%E4%BD%AD%E4%BD%B5%E4%B9%AE%EF%BD%BC%E6%9D%BD%E9%98%A4%E5%91%BC%E4%BD%AD%EF%BD%BDSXS%11%1A%00%00%0D%04%11SN%40AGGXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGAMECDA%09; gsxtBrowseHistory2=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219EEDDDDFD%11GL%16L%16GCED%40%17EFDEGCF%15MD%40%10%40%10ADG%12SXS%11%1A%00%1A%15%19%11SNS%E5%8D%A3%E4%BB%98%E5%B1%BB%E7%B0%87%E7%A6%8F%E5%8B%9C%E8%BC%9B%E4%BA%82%E6%9D%BD%E9%98%A4%E5%84%98%E5%8E%8CSXS%11%1A%00%00%0D%04%11SNEEAFXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGBGMLFF%09; CNZZDATA1261033118=1432270782-1516692560-http%253A%252F%252Fwww.gsxt.gov.cn%252F%7C1516692560; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1516620611,1516630803; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1516693635
                Host:www.gsxt.gov.cn
                Origin:http://www.gsxt.gov.cn
                Referer:http://www.gsxt.gov.cn/%7BCV2-HBzSm3Ao_ZNZauugozxFDi3JAi1xJ7dPuteRivKpqSFcXXLPKbvhmMVvBEyhZVKLxpp7iMPasXOgSbpGpkNQphNL14tS3VWe_xEzhz3AKQrnkfi2e02zJlw2VirAJOFwmTdQxZz57bYthsHX8KkZ9iSpcXY4q65f2Y6UizhLOG5F8q_sOV_LwsiYt1Fm-1516693549741%7D
                User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
                """
                headers = Headers.get("post")
                headers["Cookie"] = Cookie
                headers["Origin"] = domain_url
                headers["Host"] = str(domain_url).replace(r'http://', r'', -1)
                headers["User-Agent"] = UserAgentRoute.ruote()
                response = RequestHeler.post(domain_url + url, data=data, headers=headers, timeout=Config.timeout)
            elif http_type == "get":
                """
                Cookie:__jsluid=2d90464be28a6246dd87bedf148a3db9; __jsl_clearance=1516693332.365|0|pVl0%2FgM7q5P6nxKLfu0eC0J7JgI%3D; UM_distinctid=16121fa27263b0-03427426140f7-5b452a1d-e1000-16121fa2727581; tlb_cookie=S172.16.12.68; JSESSIONID=3C0E3EE254774AF7EC29C23BB0762DB3-n1:9; gsxtBrowseHistory1=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219%40FDDDDEBDDDDDD%40MGCLLMFAESXS%11%1A%00%1A%15%19%11SNS%E6%B8%A2%E5%8D%A3%E5%B1%BB%E7%B0%87%E9%94%8B%E6%B0%AB%E4%BB%93%E4%B9%AE%E5%9E%8E%E9%86%A5%E5%91%BC%E4%BD%AD%E4%BD%B5%E4%B9%AE%EF%BD%BC%E6%9D%BD%E9%98%A4%E5%91%BC%E4%BD%AD%EF%BD%BDSXS%11%1A%00%00%0D%04%11SN%40AGGXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGAMECDA%09; gsxtBrowseHistory2=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219EEDDDDFD%11GL%16L%16GCED%40%17EFDEGCF%15MD%40%10%40%10ADG%12SXS%11%1A%00%1A%15%19%11SNS%E5%8D%A3%E4%BB%98%E5%B1%BB%E7%B0%87%E7%A6%8F%E5%8B%9C%E8%BC%9B%E4%BA%82%E6%9D%BD%E9%98%A4%E5%84%98%E5%8E%8CSXS%11%1A%00%00%0D%04%11SNEEAFXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGBGMLFF%09; CNZZDATA1261033118=1432270782-1516692560-http%253A%252F%252Fwww.gsxt.gov.cn%252F%7C1516692560; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1516620611,1516630803; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1516693635
                Host:www.gsxt.gov.cn
                Origin:http://www.gsxt.gov.cn
                Referer:http://www.gsxt.gov.cn/%7BCV2-HBzSm3Ao_ZNZauugozxFDi3JAi1xJ7dPuteRivKpqSFcXXLPKbvhmMVvBEyhZVKLxpp7iMPasXOgSbpGpkNQphNL14tS3VWe_xEzhz3AKQrnkfi2e02zJlw2VirAJOFwmTdQxZz57bYthsHX8KkZ9iSpcXY4q65f2Y6UizhLOG5F8q_sOV_LwsiYt1Fm-1516693549741%7D
                User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
                """
                headers = Headers.get("get")
                headers["Cookie"] = Cookie
                headers["Origin"] = domain_url
                headers["Host"] = str(domain_url).replace(r'http://', r'', -1)
                headers["User-Agent"] = UserAgentRoute.ruote()
                response = RequestHeler.get(domain_url + url, params=data, headers=headers, timeout=Config.timeout)
            else:
                print("http请求方式未知", modelname, url)
                return None
            if response is None or response.status_code != 200:
                if response is None:
                    print(modelname + " request Exception :" + " " + keyword.get("keyword"))
                else:
                    print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
                return None
            if response.text is not None and r'[' in response.text:
                break

        if response.text is None or r'[' not in response.text:
            print("response返回内容为空", modelname)
            print(response.text)
            print(url)
            return None

        try:
            message1 = json.loads(response.text)
        except Exception as e:
            logging.exception(e)
            return None
        totalPage = 1
        message = message1
        if message1.get("data") is not None:
            totalPage = message1.get("totalPage")
            message = message1.get("data")
        if isinstance(message, list) and len(message) > 0:
            for tmsg in message:
                temp = {}
                for tmodel in model:
                    if "term" in tmodel and "-" in str(model.get(tmodel)):
                        tt = model.get(tmodel).split("-")
                        temp[tmodel] = str(tmsg.get(tt[0])) + "-" + str(tmsg.get(tt[1]))
                    else:
                        temp[tmodel] = tmsg.get(model.get(tmodel))
                item.append(temp)
        if totalPage is None:
            break
        elif totalPage == 1 or totalPage == 0:
            break
        elif totalPage > 1 and count >= totalPage:
            break
        else:
            data["start"] = count * 5
            count = count + 1
            data["draw"] = count
    if len(item) > 0:
        return item
    else:
        return None


def graphExtract(model, url, keyword, http_type, modelname=""):
    item = []

    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")
    # cookies 处理
    Cookie = fromCookiesToStr(cookies)

    if url is None or len(url) == 0:
        print(modelname, "url 为空")
        return None
    data = {
        "start": 0
    }
    count = 1
    while True:
        response = None
        # 循环设计解决变更数据不能正常返回
        for i in range(20):
            if http_type == "post":
                """
                Cookie:__jsluid=2d90464be28a6246dd87bedf148a3db9; __jsl_clearance=1516693332.365|0|pVl0%2FgM7q5P6nxKLfu0eC0J7JgI%3D; UM_distinctid=16121fa27263b0-03427426140f7-5b452a1d-e1000-16121fa2727581; tlb_cookie=S172.16.12.68; JSESSIONID=3C0E3EE254774AF7EC29C23BB0762DB3-n1:9; gsxtBrowseHistory1=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219%40FDDDDEBDDDDDD%40MGCLLMFAESXS%11%1A%00%1A%15%19%11SNS%E6%B8%A2%E5%8D%A3%E5%B1%BB%E7%B0%87%E9%94%8B%E6%B0%AB%E4%BB%93%E4%B9%AE%E5%9E%8E%E9%86%A5%E5%91%BC%E4%BD%AD%E4%BD%B5%E4%B9%AE%EF%BD%BC%E6%9D%BD%E9%98%A4%E5%91%BC%E4%BD%AD%EF%BD%BDSXS%11%1A%00%00%0D%04%11SN%40AGGXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGAMECDA%09; gsxtBrowseHistory2=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219EEDDDDFD%11GL%16L%16GCED%40%17EFDEGCF%15MD%40%10%40%10ADG%12SXS%11%1A%00%1A%15%19%11SNS%E5%8D%A3%E4%BB%98%E5%B1%BB%E7%B0%87%E7%A6%8F%E5%8B%9C%E8%BC%9B%E4%BA%82%E6%9D%BD%E9%98%A4%E5%84%98%E5%8E%8CSXS%11%1A%00%00%0D%04%11SNEEAFXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGBGMLFF%09; CNZZDATA1261033118=1432270782-1516692560-http%253A%252F%252Fwww.gsxt.gov.cn%252F%7C1516692560; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1516620611,1516630803; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1516693635
                Host:www.gsxt.gov.cn
                Origin:http://www.gsxt.gov.cn
                Referer:http://www.gsxt.gov.cn/%7BCV2-HBzSm3Ao_ZNZauugozxFDi3JAi1xJ7dPuteRivKpqSFcXXLPKbvhmMVvBEyhZVKLxpp7iMPasXOgSbpGpkNQphNL14tS3VWe_xEzhz3AKQrnkfi2e02zJlw2VirAJOFwmTdQxZz57bYthsHX8KkZ9iSpcXY4q65f2Y6UizhLOG5F8q_sOV_LwsiYt1Fm-1516693549741%7D
                User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
                """
                headers = Headers.get("post")
                headers["Cookie"] = Cookie
                headers["Origin"] = domain_url
                headers["Host"] = str(domain_url).replace(r'http://', r'', -1)
                headers["User-Agent"] = UserAgentRoute.ruote()
                response = RequestHeler.post(domain_url + url, data=data, headers=headers, timeout=Config.timeout)
            elif http_type == "get":
                """
                Cookie:__jsluid=2d90464be28a6246dd87bedf148a3db9; __jsl_clearance=1516693332.365|0|pVl0%2FgM7q5P6nxKLfu0eC0J7JgI%3D; UM_distinctid=16121fa27263b0-03427426140f7-5b452a1d-e1000-16121fa2727581; tlb_cookie=S172.16.12.68; JSESSIONID=3C0E3EE254774AF7EC29C23BB0762DB3-n1:9; gsxtBrowseHistory1=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219%40FDDDDEBDDDDDD%40MGCLLMFAESXS%11%1A%00%1A%15%19%11SNS%E6%B8%A2%E5%8D%A3%E5%B1%BB%E7%B0%87%E9%94%8B%E6%B0%AB%E4%BB%93%E4%B9%AE%E5%9E%8E%E9%86%A5%E5%91%BC%E4%BD%AD%E4%BD%B5%E4%B9%AE%EF%BD%BC%E6%9D%BD%E9%98%A4%E5%91%BC%E4%BD%AD%EF%BD%BDSXS%11%1A%00%00%0D%04%11SN%40AGGXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGAMECDA%09; gsxtBrowseHistory2=%0FS%04%06%1D%04%1D%10SNS%24%26%3B%22%3D%3A71%3A%3B01%3A%219EEDDDDFD%11GL%16L%16GCED%40%17EFDEGCF%15MD%40%10%40%10ADG%12SXS%11%1A%00%1A%15%19%11SNS%E5%8D%A3%E4%BB%98%E5%B1%BB%E7%B0%87%E7%A6%8F%E5%8B%9C%E8%BC%9B%E4%BA%82%E6%9D%BD%E9%98%A4%E5%84%98%E5%8E%8CSXS%11%1A%00%00%0D%04%11SNEEAFXS%02%1D%07%1D%00%00%1D%19%11SNEAEBBMGBGMLFF%09; CNZZDATA1261033118=1432270782-1516692560-http%253A%252F%252Fwww.gsxt.gov.cn%252F%7C1516692560; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1516620611,1516630803; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1516693635
                Host:www.gsxt.gov.cn
                Origin:http://www.gsxt.gov.cn
                Referer:http://www.gsxt.gov.cn/%7BCV2-HBzSm3Ao_ZNZauugozxFDi3JAi1xJ7dPuteRivKpqSFcXXLPKbvhmMVvBEyhZVKLxpp7iMPasXOgSbpGpkNQphNL14tS3VWe_xEzhz3AKQrnkfi2e02zJlw2VirAJOFwmTdQxZz57bYthsHX8KkZ9iSpcXY4q65f2Y6UizhLOG5F8q_sOV_LwsiYt1Fm-1516693549741%7D
                User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
                """
                headers = Headers.get("get")
                headers["Cookie"] = Cookie
                headers["Origin"] = domain_url
                headers["Host"] = str(domain_url).replace(r'http://', r'', -1)
                headers["User-Agent"] = UserAgentRoute.ruote()
                response = RequestHeler.get(domain_url + url, params=data, headers=headers, timeout=Config.timeout)
            else:
                print("http请求方式未知", modelname, url)
                return None
            if response is None or response.status_code != 200:
                if response is None:
                    print(modelname + " request Excepation :" + " " + keyword.get("keyword"))
                else:
                    print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
                return None
            if response.text is not None and r'[' in response.text:
                break

        if response.text is None or r'[' not in response.text:
            print("response返回内容为空", modelname)
            print(response.text)
            print(url)
            return None

        message1 = None
        try:
            message1 = json.loads(response.text)
        except Exception as e:
            logging.exception(e)
            return None
        totalPage = 1
        message = message1
        if message1.get("data") is not None:
            totalPage = message1.get("totalPage")
            message = message1.get("data")
        if isinstance(message, list) and len(message) > 0:
            for tmsg in message:
                temp = {}
                for tmodel in model:
                    if "term" in tmodel and "-" in str(model.get(tmodel)):
                        tt = model.get(tmodel).split("-")
                        temp[tmodel] = str(tmsg.get(tt[0])) + "-" + str(tmsg.get(tt[1]))
                    else:
                        temp[tmodel] = tmsg.get(model.get(tmodel))
                item.append(temp)
        if totalPage is None:
            break
        elif totalPage == 1 or totalPage == 0:
            break
        elif totalPage > 1 and count >= totalPage:
            break
        else:
            # 成员信息16、分支机构9、网站8、对外投资9、分支机构9
            if "成员" in modelname:
                data["start"] = count * 16
            elif "分支" in modelname or "投资" in modelname:
                data["start"] = count * 9
            elif "网站" in modelname:
                data["start"] = count * 8
            count = count + 1
    if len(item) > 0:
        return item
    else:
        return None


def getBusBaseInfo(htmltext):
    item = {}
    htmll = html.etree.HTML(htmltext)
    list_type = htmll.xpath("//dl")
    item_one = {}
    for i in list_type:
        info = i.xpath('string(.)').split()
        if len(info) == 1:
            item_one[info[0][:-1]] = ''
        else:
            item_one[info[0][:-1]] = info[1]

    for k,v in item_one.items():
        if "注册号" in k:
            item["reg_no"] = v
        elif "统一社会信用代码" in k:
            item["credit_code"] = v
        elif '企业名称' in k or "名称" in k:
            item['name'] = v
        elif "类型" in k:
            item['type'] = v
        elif "登记状态" in k:
            item['state'] = v
        elif "组成形式" in k:
            item['formation'] = v
        elif '经营者' in k or "人" in k or "首席代表" in k:
            item['leg_rep'] = v
        elif '注册资本' in k or "出资总额" in k or "注册资金" in k:
            item['reg_capi'] = v
        elif "登记机关" in k:
            item['reg_org'] = v
        elif "范围" in k:
            item['scope'] = v
        elif '住所' in k or "场所" in k:
            item['address'] = v
        elif "期限自" in k:
            item['op_from'] = v
        elif "期限至" in k:
            item['op_to'] = v
        elif '成立日期' in k or "注册日期" in k:
            item['date_reg'] = v
        elif "核准日期" in k:
            item['date_approved'] = v
        elif "注销日期" in k:
            item['date_canceled'] = v
        elif '注销理由' in k or "注销原因" in k or "注销凭证" in k:
            item['reason_canceled'] = v
        elif "吊销日期" in k:
            item['date_revoked'] = v
        elif '吊销原因' in k or "吊销凭证" in k or "吊销理由" in k:
            item['reason_revoked'] = v

    return item

def getReportBaseInfo(url, keyword, modelname):

    if url is None or len(url) == 0:
        print(modelname, "url 为空")
        return None,None

    generalModel = Entity.reBaseInfo
    operationModel = Entity.reOperation

    headers = keyword.get("headers")
    cookies = keyword.get("cookies")
    domain_url = keyword.get("domain_url")
    # cookies 处理
    headers["Cookie"] = fromCookiesToStr(cookies)

    response = RequestHeler.post(domain_url + url, headers=headers, timeout=Config.timeout)

    if response is None or response.status_code != 200:
        if response is None:
            print(modelname + " request Exception :" + " " + keyword.get("keyword"))
        else:
            print(modelname + " request err :" + str(response.status_code) + " " + keyword.get("keyword"))
        return None, None

    try:
        message = json.loads(response.text)
    except Exception as e:
        logging.exception(e)
        return None, None

    if isinstance(message, dict) and len(message) > 0:
        general = {}
        operation = {}
        for tmodel in generalModel:
            general[tmodel] = message.get(generalModel.get(tmodel))
        for tmodel in operationModel:
            operation[tmodel] = message.get(operationModel.get(tmodel))
        return general, operation
    else:
        return None, None


def getReprotDetailUlr(msg, key):
    reportUrls = {
        "annBaseUrl": "/corp-query-entprise-info-annualReportBaseinfo-",
        "sponsorUrl": "/corp-query-entprise-info-sponsor-",
        "forGuaranteeinfoUrl": "/corp-query-entprise-info-forGuaranteeinfo-",
        "alterUrl": "/corp-query-entprise-info-annualAlter-",
        "webSiteInfoUrl": "/corp-query-entprise-info-webSiteInfo-",
        "forInvestmentUrl": "/corp-query-entprise-info-forInvestment-",
        "alterStockInfoUrl": "/corp-query-entprise-info-vAnnualReportAlterstockinfo-",
        "vAnnualReportSfcBranchUrl": "/corp-query-entprise-info-vAnnualReportBranchProduction-",
        "annulLicenceUrl": "/corp-query-entprise-info-annualLicence-",
    }
    anCheId = msg.get("anCheId")
    if msg is None or anCheId is None:
        return None
    url = msg.get("")
    if url is None or len(url) == 0:
        return reportUrls.get(key) + anCheId + ".html"
    else:
        return url


def getUrls(content):
    result = {}
    pattern = re.compile(r'var.*"/.*?"')
    item_list = pattern.findall(str(content))
    for i in item_list:
        ru = i.split("=")
        if len(ru) == 2:
            key = ru[0].replace("var", "").strip()
            val = ru[1].replace(r'"', '').strip()
            result[key] = val
    if len(result) > 0:
        return result
    else:
        return None


def timeStampFormat(timestamp):
    if len(str(timestamp)) == 13:
        timeStamp = float(timestamp)
        timeStamp = timeStamp / 1000
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        return otherStyleTime
    elif timestamp is not None and "年" in str(timestamp):
        otherStyleTime = str(timestamp).replace("年", "-", -1).replace("月", "-", -1).replace("日", "", -1)
        return otherStyleTime
    else:
        # print("传入时间格式有误")
        return None


def EntityTimeFormat(datas, type_=None):
    # date from to term debt_term guar_term remove_date
    # entItelPlege.term - -------
    # reGuarteen.debt_term - ----
    # reGuarteen.guar_term
    #
    # busItelPlege.term - ------
    #
    # busItelPlege.term
    #
    # busAbnormal.remove_date
    #
    # busMortgageInfo.reg_at
    # busMortgageInfo.debt_term
    # busMortgageInfo.ObligeeInfo.debt_term
    #
    # busbaseInfo.op_from
    # busbaseInfo.op_to
    # busbaseInfo.date_reg
    # busbaseInfo.date_approved
    # busbaseInfo.date_canceled
    # busbaseInfo.date_revoked
    if datas is None:
        return None
    if type(datas) is dict:
        if type_ == "busBase":
            datas["op_from"] = timeStampFormat(datas.get("op_from"))
            datas["op_to"] = timeStampFormat(datas.get("op_to"))
            datas["date_reg"] = timeStampFormat(datas.get("date_reg"))
            datas["date_approved"] = timeStampFormat(datas.get("date_approved"))
            datas["date_canceled"] = timeStampFormat(datas.get("date_canceled"))
            datas["date_revoked"] = timeStampFormat(datas.get("date_revoked"))
        return datas
    elif type(datas) is list:
        pass
    for data in datas:
        if type_ is None:
            for t in ["date", "from", "to", "term", "debt_term", "guar_term", "remove_date"]:
                if data.get(t) is not None:
                    tt = data.get(t)
                    if "-" in str(tt):
                        ttt = str(data.get(t)).split("-")
                        try:
                            data[t] = timeStampFormat(ttt[0].strip()) + timeStampFormat(ttt[1].strip())
                        except:
                            pass
                    else:
                        data[t] = timeStampFormat(tt)
        elif type_ == "invester":
            subs = data.get("subs")
            acts = data.get("acts")
            if subs is not None:
                for i in range(len(subs)):
                    subs[i]["date"] = timeStampFormat(subs[i].get("date"))
            if acts is not None:
                for i in range(len(acts)):
                    acts[i]["date"] = timeStampFormat(acts[i].get("date"))
        elif type_ == "busMort":
            data["reg_at"] = timeStampFormat(data.get("reg_at"))
            if data.get("debt_term") is not None:
                tt = data.get("debt_term")
                if "-" in tt:
                    ttt = str(tt).split("-")
                    data["debt_term"] = timeStampFormat(ttt[0]) + timeStampFormat(ttt[1])
                else:
                    data["debt_term"] = timeStampFormat(tt)
            if data.get("obligee") is not None:
                if data.get("obligee").get("debt_term") is not None:
                    tt = data.get("obligee").get("debt_term")
                    if "-" in tt:
                        ttt = str(tt).split("-")
                        data["obligee"]["debt_term"] = timeStampFormat(ttt[0]) + timeStampFormat(ttt[1])
                    else:
                        data["obligee"]["debt_term"] = timeStampFormat(tt)
    return datas


def EntityStataFormat(datas, type_=None):
    if datas is None:
        return None
    if type(datas) is dict:
        return datas
    elif type(datas) is list:
        pass
    for data in datas:
        if type_ is None:
            if data.get("state") is not None:
                tt = data.get("state")
                if tt == 1:
                    data["state"] = "有效"
                elif tt == 2:
                    data["state"] = "无效"
                else:
                    data["state"] = ""
        elif type_ == "spotcheck":
            if data.get("type") is not None:
                tt = data.get("type")
                if tt == 1:
                    data["type"] = "抽查"
                elif tt == 2:
                    data["type"] = "检查"
                else:
                    data["type"] = ""
        elif type_ == "web":
            if data.get("type") is not None:
                tt = data.get("type")
                if tt == 1:
                    data["type"] = "网站"
                elif tt == 2:
                    data["type"] = "网店"
                else:
                    data["type"] = ""
    return datas


def formatMembers(members):
    if members is not None and len(members) > 0 and isinstance(members, list):
        for temp in members:
            temp["name"] = getFontFromStr(temp.get("name"))
            duty = temp.get("position")
            if duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABaUlEQVR42mNgwA7SgNgUiV8OxEoM\nxAN7II4lRmERENtC2cuBOBzKlgbiL0DMg0VPIhDPxoIPAvE1HHJpyAYsRLII2dIuIH4MFUPGWUCs\nB8ReWPAEIN6CQ86AkKXyQPwBiP2waNZD0rsJagkMXwLi+2hi27AFLzZLdwNxLdTyHUAsiyNqPqHx\nk4F4CprYD2IsrYS6jgkqVgDE74DYEYelhHyK1VKQywKwxCky8IHGLxeSmCU0pQYg4SlQByOLgdSI\nY7OYDYpBhmsh8ZExH5qeLKglyHgvEF9BE7sLTQsoAJQl/gPxayjGx4ZlH0do/KHjhVCLkcXOQVO1\nG7qln3BE/A+0+ONBCtpwLHgmNOEhi50E4g6ksoBsSxmgrl+Iho8C8Q00sYe4gpccS62B2AUN90Hz\nLrLYNiiNUgSuAeJfSCXOHxzsX1C1RWiO5oOm0HCoT3MIlbvGOIosfNgYzQxQfl4MdVgPjrIaDAC5\nfoW6ShoocQAAAABJRU5ErkJggg==\"/>':
                temp["position"] = "监事"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABoUlEQVR42r2UT0REURTGr5G0eCJJ\nWkWrFrNLxshom1m0mM1IRkak1WgRLUbSLmmRJDIyRtImaTFGJC3Sov0s0ma0GEkkSVrE9J18L2fu\nvDtv2nT5effdd+89/77zjGkefWDV/PNYA0ecz4JPBxPcMwkyCjkzB94c1E1AlE9gOMSpG/W+AHbp\nyD7YBvNck5EEp5x303DT2ALr/CgX9Frfl8E9GAhw5hl4nIvRPd4zDc4492yjMV7YA/LgUn2TzUXQ\nACuODNhGa6AMbsEj5xXbaJEpksVXpjjC9EkdCmCcB6tgKsRoR+mNEIlwEUTpodQvYRlI0REpxQ4v\navBZo9EyDfoaSDLVLTXNK6/8lHsOhogr0jtQYhAPnB/aRsWLL7bLCTjmWp28gA/1vtkmvV3Uhp1e\no/b89tsByHJjv3Vpho6YDoSUowaEc6a8oBgNukBqG+fzL0Zn2CqigTTZoILTikH/UJx9KjV4p0o7\niVR695qluaIu9LDT26LIJTCmRHShqFLNei1H0aRUDbMUTSlASD6uXv/5JSZCGAk4F2V07Yh9A2Qg\ng+AVrBiLAAAAAElFTkSuQmCC\"/>':
                temp["position"] = "经理"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAOCAYAAAC2POVFAAACPUlEQVR42sWVX2SVYRzHHzNHcsSR\nJF2MyWR2l5kk3SXnYjKOYzKZMV0dk9jFJF3EZCZJzMwcSczMLmZipovM7H4XGZkuJhlJki5ifX98\n3vl59j7vToz9+DjP8573eZ7fn+/ze0M4alfEg5znDf7Ls4p4HE7BLog9Meie3RTfxMXEmifiLeN7\n4k+CG7xzSww5bM198TPBXt6hVZgUz9z8s5h28zirFkhHQQIsmA03HxWvCGBGvBAjPMv8WGJcwuEj\ndiAWxLsEC7zjbUo8ZVM7+Fz0/yOxQ8Vi2xdlxubsa/bpF8uMy0XOlgoyVIqc7cORM2JCrLv/7JB5\n3h9P7Bc7uytWxJb4ynj1pJydp5S22Q+k0EaZTWezopcDt8WdY5z9bxnUxN0EtcjZNling/SQkQ0u\npbcBAjDJvMSBA353cXYFRzONV5HEiWl2wmUhk0Y5wSVIZfaTaBL8F8ZvUs5WyVSW/k3RHWWy5uYW\n9V/a1iIB9ZNB47v47ebPC2TQjvZjGQT3zqHNobUq5Qj0wB3aU6DP2qGdrl/aumHWnY/2HCKA0MIF\na6Bx4z3SmHVczRadJQMdkbMBjdnz27ShUfpuJTrYsn7dVaZVZwdpWabxOkzSEeqOww/SQ6LJSrCW\ns/E4mwbKPo1zU2jsF7e+lcxa0B+R0Ad0H8txKRVhnYPNLpPlpivBHF+pXqehdm74mLjmLteaY5vu\n4J81uEwDTqPDnNfMuWAZqV4duqIS1GlLx1mFchbRmbOux33KU/T9A1cGuQIA/VG9AAAAAElFTkSu\nQmCC\"/>':
                temp["position"] = "总经理"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACqElEQVR42r2WUYSUURTHx1irh8RK\nkqzoIVlj7dsaayWykmRfMg9ZSezDyDysXpL00EvWWvMwljWStTIkSdaItVZW1rL2IUkiWaOHLMk+\njQx1Tn43Z447830zDx1+Zu65937f/d97zrlfJtNui8IR0x4Qqpl0dkWYyPRnt4Qx0x7Dl9YuCDNp\nBx8IR017UGilmHdC+C4UaK90QTeuyOYFPgvrpr2Oz44pIrwa4a3wsUPfbBqRzQSBOn5HWDa+Qhey\nwqhwyVAXHpj2PeEl/y8LU8wZJWI8ZWGtQ9+/CFlFzG9+n4P1NU1fsOPCO+EV7VM9hNh9xL0RvkKD\njd5k0Ws824fua9OvvGe+9dXThOsAIg45UeU6OxzsEaJ17G1hN6XAEXeSgccIiPWNmPmH7nn67orz\nNdPmZE74YdrTTuSQOcEDCk+JF3aiRJGI9WkufujQN+NEJp1kV5G6Y+Psqi5o24msuTlZwusZ7ZjI\nFmEXRIZcrjm2KTjenzPvyyN42lAhPK1Px5z0JfgJ6rVK3mUx2t5KEFkjbytdwlOfM+l8mgobJhUG\nyb0l56sTrsGKkU3ciETAFwpPWxF4SBjYcF0yQocjIheEPfKyH5ENV+43I1fBvhF5kfzzrCDU+vao\nulNJOamhcxUBWuKvkZNZ7sY8i63+J5H5DtfSMlXa+nZIucluIlXQNwTZrxoNn/MsMFg/IvU9c/wG\nZlmw9WnanDPzypEPDL3GPjnfvg9XL3KIQSXXr+J+cpW86EFkK/LJN05UWHbJJe+3cyci18ti5Orx\nufx3l28IvwjDLUInZg1OuJQgUqvtU17WoogEO+0qYaAcqZKBYff8Y1TQAid5J+lyvskRz9GeN3eg\ntxwCB4yvRNWzNo/wMrlk7QwL7IWzkatrlUK44GpJm/0B+H4BqS3ysBwAAAAASUVORK5CYII=\"/>':
                temp["position"] = "执行董事"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABaUlEQVR42mNgwA7SgNgUiV8OxEoM\nxAN7II4lRmERENtC2cuBOBzKlgbiL0DMg0VPIhDPxoIPAvE1HHJpyAYsRLII2dIuIH4MFUPGWUCs\nB8ReWPAEIN6CQ86AkKXyQPwBiP2waNZD0rsJagkMXwLi+2hi27AFLzZLdwNxLdTyHUAsiyNqPqHx\nk4F4CprYD2IsrYS6jgkqVgDE74DYEYelhHyK1VKQywKwxCky8IHGLxeSmCU0pQYg4SlQByOLgdSI\nY7OYDYpBhmsh8ZExH5qeLKglyHgvEF9BE7sLTQsoAJQl/gPxayjGx4ZlH0do/KHjhVCLkcXOQVO1\nG7qln3BE/A+0+ONBCtpwLHgmNOEhi50E4g6ksoBsSxmgrl+Iho8C8Q00sYe4gpccS62B2AUN90Hz\nLrLYNiiNUgSuAeJfSCXOHxzsX1C1RWiO5oOm0HCoT3MIlbvGOIosfNgYzQxQfl4MdVgPjrIaDAC5\nfoW6ShoocQAAAABJRU5ErkJggg==\"/>':
                temp["position"] = "董事"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAOCAYAAAC2POVFAAAB/0lEQVR42rWVQUSDYRjHJ5MOiUw6\nTCJJJtltMpmYyQ7pNh12SOwwSbol6dClQ7LDRHaaDpEkySdmpkMS0yFJIpkOHbqlw+xSz5v/x9Pj\n+fZ+O/Tys33P+z7f+7zP+3+eLxDQxyIRZc9R2PyOBJH1sS5CFC1rgtKQJ0qMZ6LCniuw8TV5HKCk\ncEU8eszl2L5J4sMjyH6iTBzLiUk4ujjEJnteJ07xf5ZIwceQVigQFx5zUR/BLhHvxAkxoJ1kA0Fe\nEq/gDS+rYXPDmSKJczZvuIc/tznKnjzYbtyWucEnHMxTO0mFHQSizUWY/6eSGanFZptg+4gvok4s\n2ISexcslRqsPHnNZEawts01LZoc6KOBAL3EkuMG1SPsE85tC4POMIq6d28yaQfiYwvnukD83FSKq\n0I6L0ea+sDnICO8kMutV5UZeFB3KAssiQdYRQkHxNlNTWlCDBTsDfUrKCJjb7tAlUm2C7cJ+uf8I\n1kggo3CArsJttyjYaUvrikHfSZtm1/DrksPG3LZCjDG/AjLJuUb74baGDxmME2EcrgWJqSOGxs+p\nQ2vSHmd+caWt7Sktz1Gy5QabwHyLfTTSmDPymeNOYVG5LgWlql1kq+lDgWSQ2WUfdbKKSjdBbSlf\nqxCKswUJ/Y5hbNQJI+LFpjgO0dp2IRnbGCW2iR7LOtPygj81EMiFCWOxNQAAAABJRU5ErkJggg==\"/>':
                temp["position"] = "董事长"
            elif duty == '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEcAAAAOCAYAAAB95wG7AAAC9UlEQVR42q2XT2RcURTGnxgR8WRTVVE1RBfVxSiVRVTVUCNGVJQaFW9RQ8SoqmwiiyxLVVUXo0TMYkQMNbKoGGVEVFV1UxVVFaqqi6hS8VSNGNpz63t8Pb33/cnk8DP3nffue/d+955zz3ie3eaFSbpeEia89HZFCLzsNi2UMvbJCcvCqSN876xwL82Di8JltFtCBe3Twk/Bt/S5JaxZeCF8cNybd3z/mvBd2FcLk8Y2MeY4G8f8GLMYvzAmfe8cd26SICzOA+ErfExNKAhlC4+FLce9C5aBlyDMFJ75Jlx0TPKEBSNmQzhpuRdZFfPYSslSkjh54QCrqidZoL7P1It3hc/K13FMNsA3iuS7KYTCDfWsDxE1PWC7N0ziNNEuOsYT0vNekjhdYQUiPRfOOCYYqmszkLry9dT1GFZ737FLzAL8ENrIDXEWhWycmTFtYKFeQzi9W/oQzbTvxImzjAeH4LuLwRYd4iTtHBZnDqJ0EYKbDp7QoB8egzhN7L4ZYQdtpodQNO0R7mxWetaSc9hmELej5JtCaMwSdQjLvoBOlOuUmCcdualMiXk6IUlnEcfYVcxDHxZ9V1h5uDEMEc7TNTOm+tQgBrMtvFe+T5jwoGYm8Tsla2qcDbQLtBl2qN1GafCf+XhhlMji2j4ltqqFJgRi31uEUAmEGSkNuHPqCNM8oiLClB2rype3iRM6EmhP5RefQqpiYRUJnH1vhPuoIXIq1icgfMWSByJyA4rTQmgb9qjPHgSKrj/aCtijiONhNzQVr/AR9n1xhFUOW3uFfAsoD0YyhFqSOLv4fkC5JzqIqupdxybOJSQ45hEmx74OfrU9pVzAgnXoRBlUHFMKHOK9LnHG8a1tnKb//HVo4wVRBdx3tA/x7KKlbgkQGmbn3E6YkEnu75DDOthpByjne2ibhXhJp+M6FXxpWQcNKiMaFnEWENpdVVn/LcLKGdGF2xAG0UJNkmbF53BKlHCCjFJd5SGs2jg5B7FazB/nuutP8h/afy6iI8pTTAAAAABJRU5ErkJggg=="/>':
                temp["position"] = "监事会主席"
            elif duty == '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACxUlEQVR42r2WX2RbURzHr4iYiRE1NXsoNTNTM6aqpvYyM3moKRFVNVWqDxMzIw8104dSUzVTY6aiZkJN7KGmVE1NTdljH6bM7CFiwkzN4oyzRt0Yl70R47vRG/Pdx8Zr5hOcG8V1nrlhTArunbsJdteP64iacSdGZB4WjQVZfzGWZe1H0TmgL+Gbzgm7sp4xVvj+C+OpMc1eaEeNeQahbcMZ2EB9SIP9TiL/GutGNYZ1ntGxZMxjjDP4jPf7Q+OADPFHEzsCRD7nnFHjLfNslMgVXtChXuokMpMQkYwncggBp4w5Y9srhwrPl2PO80V+NTaMPQLj5u/iRO4YL4WdExJZ4QxnxE9SNkU61vn2IIbuG7c7iOw6XV0h35P6ybOe7FJkgd+jKHgiU7BNRx4gArs0Kx1jCJ+nAR5y1iERnCZyeanhPKnbJtKlzVoC2ROoyTnxepjC2RjOQVwkP2Onc9o35q98kWGR3oQjmX8yerrorilJk4/GZS9yBVk7L7e4Pt7giFFpeD+M37J+kpCuaYLkp2sgz7SJHIEjme91ELlKLeVJmzD1D7gmAu5JZ2y/3HfuvSne64konWpCjavIkvSQTVJY+8ol/4IP06sl8wZGXKGdq8jTeLzPExlQQ27/FtfBDPdmzjPYRXlYMqFbkeNcHS4QRVgkKEWhV0U25RCN1Jbn6Zz8/gDvhamyFWFQGWMC0nMZUUvU0C+6aDeRdM76QBDeU9d+2dTiPBNGZwNaMm8iskyr3iQiAZ4aZn6eqK5Jqqzyr2ZQvpOmY943rknT2RL2ySDdK9FkxqQGp7wGqY0npKzdtUrT8FnAuFmMdsZfjXHWRS9VilwPnUZOekAc/RHvDXhXXhRD/wB5SwMiRVOUpAAAAABJRU5ErkJggg=="/>':
                temp["position"] = "副总经理"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFUAAAAOCAYAAABevFBuAAAEC0lEQVR42r2YcUScYRzHXzknk8hk\nMnNkJjkTk5NkYjL3RyaSzEkikzmTyJzM/hhnTjInkiRJZDKZjHPOzElMf0xm4uTkTCIzk/tjtN/L\n95nv/fY819myh4973+d5n+d9nu/z+/2e33ueZy+jQgfdd6Cu1nJXiNX47C1hWNU1CFMX9LspPLLU\nx9FmK03CjPefyoSwSBwIGbrPoI6fmYDQixbeC58dbeNCQAiCkHAitFHdsvCa7oPow6VZKKkN6RGO\nhWuOdT4T1nD9UCg76FbGYfD7jAjfHZT4ZbeFe8Q2dtTcPxU2cX1f6EMfn6iFOeGto823+gQ2ylAU\n9nG9B2EyigTN14yVFF7QfUGYpXttpcfYRK+K6Hm69w0gDaEXsK4x1Jl5bOI6CGErSgJivhMOwRGs\nKAeRfN5YQsEWtft8Qn+u266ymDSFC56oq5wLG8K6gw08wyUlPMfifYEaVfsUvLHZ8r4ThCQPos5j\nnH7oEUR7hajtylINSQhma2un/nqHeDdNKav7ebiLz5lwiutT3JcIm6jBKqIHlagRCFYP48mq+L2M\n56cd42lRjcHsCl/JaCp0iEEETQZuaWuLKVEvstTyX1pq+RJEXcY4/jy/IQTUwb1LiPWdEGYfIa6a\nqDW7f4PFjXaww7o+TP26IMgDIo0Jcl2MDpA4JmPwY+FHXOexUNP2E7/TStRBNT4zqEStA1lkDGFY\nWB6HG5cBvN8PFa8g1Dl+DyGqOS9MDI4iFPwh6lW8lE/cUYofhm24P2cO2oqzFgsv0OFRj000LMBq\nGrCoLWor47f+H2NqQnlARM2BaQEuS/0irGCdRVyvukQ9UulPzpIaFUnUXrxEY17IdXs4PfvUyZqm\nkz8NKyhQm839o7A843Y7KsbXwVpN6YfFryFVW0ddyRHHX1Zx/wBtsA5VDZchqu/6QxYWkEVw3S4O\nPuNudzCpEQiXIpc6p9RoQ81zCRsSxQaYM+EAaZOHMOOL00r55hI8L4q16jNlvUqMZlHjpIXJlFif\nNh1TJ5UbjEMgrovjK8iUOVgmkycXMRQtuWMLYmleHVQ5bMKYev4KLCqkRPUQA0PwhCnMvUBCsxV3\nkaXXKuowQmEPGUoS82TjqfjwiKjDYxMLLljqu6lftyXdmrWkYjoW98C6eh2nfxMsIUvWPYk681zG\nIsA0Fu/B3WchYgpj/bDkzC5R/c35gNCRUx8gF+bU1x2n6JzlFDfcUGM0YnJDsLzHVXZ+BoK21ZBS\njSMsJTB2F835DF5gXG8JX02d5H0BHH5PEHKMAfHX2j6yAa6Lw1MGKIaOKu/jg8rwO0sJqW/cWmi1\nuNUqdjxlC9pUQnBlU5IQzIM1r1jGDjj+jNHxPFzDfx1NsP5qtFr6hR2f3kzkF9n7lseFpaXKAAAA\nAElFTkSuQmCC\"/>':
                temp["position"] = "董事兼总经理"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAOCAYAAAC2POVFAAAB6klEQVR42p2VQUTDURzH/2bSYWKH\nmUy67JB0iB2SmRlJksyYDvlLYod0mkiHTol0SJJdpkOSbumQxMwk2a1Tku7ZYSSTJGN9H9/xPO+9\n///fjw97b//fe9/f773f7zmO3jbAtPN/K5KgNgayQRyWQA+4IKMQ1XxfoI/MHVHnCx57V8CFX6Hz\noANuFJoMQBd1CawrNIg6X/LY/xyc+BG6Br7AnDI/AB7AocEvHiCzcQ8NNbDtJbQM2mAf5BWuwasy\nJ2+aYKAydaLOJywaQuCHflaLcqE2ozuz8M3r4rAIXQ01ovvPVLhZrv0JYn6ughA7I43TYEv55l0S\nm9Fkz4uMYe8jcAlONXv6Eivu2ZVFbN9WfIh0LfsOsbBnmfkWGAwqdtmn2A4r3TVQ4tomE7XyIo1F\n99kNKnZT0/dMYiPSWLSfY2kcsYidAl1mVZ1L28RWwQR/i2N4ZoU2JMcD6RuTWNEvV32IHeWRVzX/\niVb5AVJeGc7zWOoU3W9tDYPzAghLWWlzoyZPJ6k5jRRPqc5errNbJsJVIywywhYXKSuOEd6tX16N\nYTDOR0QU4h54BG8gR58cr4QQ/0ThMWa9y3qwFVKYp9STH4tJHnmFGQhZFkjyoYgz4nu2nB3LHRPr\nLTJIkcURH0+vbMI3/AfD25Gqfup5qQAAAABJRU5ErkJggg==\"/>':
                temp["position"] = "负责人"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACk0lEQVR42rWWQWRcURSGn4roYoSI\n6qKqVESMitlVRUSJqCxidhExiwgjYlR1U1XVRZUsqkY9pSIisggREREjjIgsIsLoIqqqVEXULGYX\nXTxPaM+p/9bpce6dN6WXz9x37rtzz3/vOee+KOq8dREznrFZoiCeC7BlbaNEKcN7eSLO4OdfbYW4\nCPBWvJsjEvQXiCXBF6IunuuwyXcWIHzJ4JD45BkrCx/GiJZHXC+xSmz8wwFGW0RRiRzCgo4a8Vw8\nP8U87j8gxjGHmTCoEruesUIGkXNEk9gkrlkiFvHCd0ETdp9Ibs8gbo/4Bs7hxAGcZraN0N0R48wp\n5ktbzfBViuxGdHDEfMaGeFuMndA7EwdE5tVJOhYhwBrLi/+/CKznWhIQ2UP8IBrEdJZwjJETOkdC\nIksY13AufvSMlZTIdieZtDnJm53kHC9eUXlQEU75wpWf1xXHCB9tvyPm3cN/FwUxwlPa+J3rmMMF\n5WeH/ImMq/gDH7mAyD5iH7nh4Nx7p2w1nEAkKrM+5X0jAr4aeaYLTwkbG2w5hI7Lm1T0GxASEnmu\nwvzAuArOhMj7yD/NKoRK2wdU3fGAyCtYr5xF5AhIRf/kP4jkUJ0yeI8qLW0nKGQjba6Qu/BrLCQy\nEblzKfpNCBnC3WPl5GP8OspwWNoeEgNiXtVIiyNcA9J2liFcB4kb2JQUqWCKbHnKdh0i5RdFonZw\nS9FALmn7sJg3bFwvb4yrp2acjhM5ivFUfCxMYIzDfNI6SVe2L0W/BZFPUAj2ICDC7hUNqkaVdOiS\n34PCMYWTrGS4CR6hcrJvL4yvmz74moqPmd/VdV1VQ8crbMI8sYz8crt2Cw52wm3lEBeNNaz/Gmu1\na/3ES/gdanz1dP0CG38SpdFXf2kAAAAASUVORK5CYII=\"/>':
                temp["position"] = "副董事长"
            elif duty == '<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACg0lEQVR42rWXQWScQRTHR0SsWqGH\n6qFWyaGihypRqyKixB6qokJEVFWUVTlUDyGicqheqodaVbmsHKJiiYiIiBA5VA97yaGqclh66KGq\nQtUe6hNL+qZ+H5PJ++abrfbxY/b73nwz/5k3780ac9puCFWTbVV8NHsoXPKeTQvDJt4GhVHzn21K\naATeN/DxrV84Fga853XEx9qSsBrhV2e8dga/8Dll94UjHBLaGgk+R/RJ7bGwR/urUPxLkW+FN5Ei\nQ36zmsheJvZAWKetsY5PkT6ptYQx2m1P5IIwIdSE9zmT38M/RuQWY2rUNJFuuDbZJY2mEq4z7LBx\nRD5iV74J34U14YnQCUy8h+/sR4r8LGxk8CFPZItQ0Gh5Is8jJCHB2LNwwrmySWfHCdeCtxi+jdL/\np3AhIkFdCbwv4fNPEs8KghKST1EJ11Rk+i7Lanx/WZgP+N0lIpIcOhlJ8s/DThcdnwsXlXDVRF4j\nKZmM7Gz7VYSbREchIHJbKW1+6dkIiey2hPRFiNwUPrHzmr0QDp3fTRYwVuQquSEossqZ2404k7u0\nZ7sQeUcYF4bIzq6ViZCK8mw4UuSOsvhnRI4xmZR5hKe/54Snnk8lQuSSt8J20HfO78uEppYJXwk/\nWJiQyBIXgwPm1ZcXrvZsLJLhprwycUy4jkSE60AgLJdpD3FG952JGWWH2t7Fo8ep0WVKiV3MW0SZ\nXZiXLOCZkEmvSrbgX1UGtAnmGbedj4SfJrLB+VrxWOP7ZRatw2oXAjmgl3p7wiXBjnWbjThgARaU\n8lJ3NuW6u1O1nNpjnHo3xy0mncim935SuUhMO98v5fwR8G2ccezZ/kKiuSecy6mVr+24vwGFkdkz\nltO0vAAAAABJRU5ErkJggg==\"/>':
                temp["position"] = "其它人员"
            else:
                temp["position"] = duty
    return members


def formatChange(changes):
    if changes is not None and len(changes) > 0 and isinstance(changes, list):
        # "item": "altItem_CN",
        # "before": "altAf",
        # "after": "altBe",
        # "date": "altDate",
        for temp in changes:
            temp["item"] = removeHtml(temp.get("item"))
            temp["before"] = removeHtml(temp.get("before"))
            temp["after"] = removeHtml(temp.get("after"))
    return changes

def formatInvester(investers):
    if investers is not None and len(investers) > 0 and isinstance(investers, list):
        for temp in investers:
            temp["name"] = removeHtml(temp.get("name"))
            temp["type"] = removeHtml(temp.get("type"))
            temp["cert_type"] = removeHtml(temp.get("cert_type"))
    return investers

def getNumFromStr(str):
    if str is None:
        return None
    else:
        pattern = re.compile(r'[0-9]')
        item_list = pattern.findall(str)
        return ''.join(item_list)


def getFontFromStr(str):
    if str is None:
        return None
    else:
        pattern = re.compile(r'[\u4e00-\u9fa5]')
        item_list = pattern.findall(str)
        return ''.join(item_list)


def removeHtml(str):
    if str is None:
        return None
    else:
        str = re.sub('<div.*?div>', '', str)
        str = re.sub('<span.*?span>', '', str)
        return str


def fromCookiesToStr(cookies):
    # cookies 处理
    Cookie = ""
    for temp in cookies:
        key = temp
        value = cookies.get(temp)
        if key is not None and value is not None:
            Cookie = Cookie + key + "=" + value + ";"
    return Cookie

    """
    todo:parser: 1.数字和文本的转化 2.基本信息获取完善3.get set统计4.url的获取5.完善抓取流程6.确定模块其它url 7.翻页开发

    get set统计 翻页开发 数字和文本的转化 时间处理

    成员信息16、分支机构9、网站8、对外投资9、分支机构9

    去反扒处理

    记录主页url

    530 rep invester 463 ent invester 1040 rep baseinfo
    """