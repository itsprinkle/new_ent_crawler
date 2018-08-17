# -*- coding: utf-8 -*-
"""
@Time : 18-1-10 下午3:14
@Author : courage
@Site : 
@File : entity.py
@Software: PyCharm
"""

"""
    type>>>>[]
    Year         string            `json:"year" key:"年度" sd:"ancheyear"`
    Date         string            `json:"date" key:"日期" sd:"firstpubtime"`
    From         string            `json:"from" key:"纸质年报"`
"""
entReprotHead = {
    "year": "anCheYear",
    "date": "anCheDate",
    "from": "annRepFrom",
}

"""
    type>>>>{data:[]}
    Type     string     `json:"type" key:"合伙人类型,股东（发起人）类型,股东类型,出资人类型,发起人类型,出资方式,投资人类型,主管部门类型" sd:"invtype"`
    Name     string     `json:"name" key:"股东,出资人,姓名,发起人,投资人,人,股东名称,名称" sd:"inv"`
    CertType string     `json:"cert_type" key:"证件类型,证照类型" sd:"blictype"`
    CertNo   string     `json:"cert_no" key:"证件号码,证照号码" sd:"blicno"`
    SubCapi  string     `json:"sub_capi,omitempty" key:"认缴额,认缴" sd:"lisubconam"`
    ActCapi  string     `json:"act_capi,omitempty" key:"实缴额,实缴" sd:"liacconam"`
    Subs     []CapiInfo `json:"subs,omitempty"`
    Acts     []CapiInfo `json:"acts,omitempty"`
            Type string `json:"type" key:"类型,方式"`
            Capi string `json:"capi" key:"出资额,额"`
            Date string `json:"date" key:"日期,时间"`
    "subs()": "subDetails()",
    "acts()": "aubDetails()",        
    "subDetails": {
        "type": "subConForm_CN",
        "capi": "subConAmStr",
        "date": "currency",
    },
    "aubDetails": {
        "type": "acConFormName",
        "capi": "acConAmStr",
        "date": "conDate",
    }
"""
entInvester = {
    "type":"",
    "name": "inv",
    "cert_type":"",
    "cert_no":"",
    "sub_capi": "subSum",
    "act_capi": "aubSum",
    "subs":"",
    "acts":""
}

"""
    // 股权变更信息
    type StockChangeInfo struct {
        Stockholder string `json:"stockholder" key:"股东,发起人" sd:"inv"`
        Before      string `json:"before" key:"变更前" sd:"transamprpre"`
        After       string `json:"after" key:"变更后" sd:"transampraft"`
        Date        string `json:"date" key:"变更日期" sd:"firstpubtime"`
    }
"""
entStockChange = {
    "stockholder": "inv",
    "before": "transAmPrBf",
    "after": "transAmPrAf",
    "date": "altDate"
}

"""
    // 行政许可信息
    type LicenseInfo struct {
        No      string `json:"no,omitempty" key:"编号" sd:"licno"`
        Name    string `json:"name" key:"名称" sd:"licname"`
        From    string `json:"from,omitempty" key:"有效期自" sd:"valfrom"`
        To      string `json:"to" key:"有效期至" sd:"valto"`
        Org     string `json:"org,omitempty" key:"机关" sd:"licanth"`
        Content string `json:"content,omitempty" key:"内容" sd:"licitem"`
        State   string `json:"state,omitempty" key:"状态" sd:"type"`
    }
"""
entLicence = {
    "no": "licNo",
    "name": "licName_CN",
    "from": "valFrom",
    "to": "valTo",
    "org": "licAnth",
    "content": "licItem",
    "state": "status"
}

"""
    // 知识产权出质登记信息
    type IntellInfo struct {
        No      string `json:"no" key:"编号,号,代码" sd:"tmregno"`
        Name    string `json:"name" key:"名称" sd:"tmregno"`
        Kind    string `json:"kind" key:"种类,类别" sd:"kinds"`
        Pledgor string `json:"pledgor" key:"出质人" sd:"pledgor"`
        Pledgee string `json:"pledgee" key:"质权人" sd:"imporg"`
        Term    string `json:"term" key:"期限" sd:"pleregperfrom"`
        State   string `json:"state" key:"状态" sd:"type"`
    }
"""
entItelPlege = {
    "no": "tmRegNo",
    "name": "tmName",
    "kind": "kinds",
    "pledgor": "pledgor",
    "pledgee": "impOrg",
    "term": "pleRegPerFrom-pleRegPerTo",
    "state": "type"
}

"""
    // 行政处罚
    type PunishInfo struct {
        No      string `json:"no" key:"书文号" sd:"pendecno"`
        Name    string `json:"name" key:"名称" sd:"uname"`
        RegNo   string `json:"reg_no" key:"注册号,信用代码" sd:"regno"`
        LegRep  string `json:"leg_rep" key:"经营者,人,姓名" sd:"lerep"`
        Type    string `json:"type" key:"违法行为类型,处罚事由" sd:"illegacttype"`
        Content string `json:"content" key:"处罚种类,行政处罚内容,处罚依据" sd:"pentype"`
        DecOrg  string `json:"dec_org" key:"机关,作出行政处罚机关名称" sd:"penauth"`
        Date    string `json:"date" key:"日期" sd:"pendecissdate"`
        Detail  string `json:"detail" key:"地址" sd:""`
        Remark  string `json:"remark" key:"备注" sd:"remark"`
    }
"""
entPunish = {
    "no": "penDecNo",
    "name": "entName",  # ?
    "reg_no": "uniscId",
    "leg_rep": "",  # ?
    "type": "penType_CN",
    "content": "penContent",
    "dec_org": "judAuth",
    "date": "penDecIssDate",
    "detail": "",  # ?
    "remark": "remark"
}

"""
    // 企业基本信息
    type GeneralInfo struct {
        RegNo            string `json:"reg_no" key:"注册" sd:"regno"`
        CreditCode       string `json:"credit_code" key:"信用代码" sd:"uniscid"`
        Name             string `json:"name" key:"企业名称,个体户名称：,名称" sd:"traname,entname,farspeartname"`
        Type             string `json:"type" key:"主体类型"`
        State            string `json:"state" key:"状态" sd:"busst"`
        Telphone         string `json:"telphone" key:"电话" sd:"tel"`
        Postcode         string `json:"postcode" key:"邮政编码" sd:"postalcode"`
        Email            string `json:"email" key:"电子邮箱,电子邮件" sd:"email"`
        Address          string `json:"address" key:"住所,场所,地址" sd:"addr"`
        EmployNum        string `json:"employ_num" key:"成员人数,从业人数,人数" sd:"empnum,memnum"`
        LegRep           string `json:"leg_rep" key:"经营者,负责人,执行合伙人,法人" sd:"name,lerep"`
        WomenNum         string `json:"women_num" key:"其中女性从业人数" sd:"womempnum"`
        HoldingSituation string `json:"holding_situation" key:"控股情况" sd:"nbholdingsmsg"`
        Capi             string `json:"capi" key:"资金数额" sd:"fundam"`
        DependEnt        string `json:"depend_ent" key:"隶属企业名称"`
        IsStock          string `json:"is_stock" key:"股权转让"`
        IsWebsite        string `json:"is_website" key:"网店,网站"`
        IsInvest         string `json:"is_invest" key:"购买,投资"`
        IsGuar           string `json:"is_guar" key:"对外担保,担保"`
        MainActivity     string `json:"main_activity" key:"主营业务活动"`
        Relation         string `json:"relation,omitempty" key:"隶属关系"`
    }
"""
reBaseInfo = {
    "reg_no": "regNo",
    "credit_code": "uniscId",
    "name": "entName",
    "type": "entType",
    "state": "busSt_CN",
    "telphone": "tel",
    "postcode": "postalCode",
    "email": "email",
    "address": "addr",
    "employ_num": "colEmplNum",
    "leg_rep": "",
    "women_num": "womemPNum",
    "holding_situation": "",
    "capi": "totEqu",
    "depend_ent": "dependentEntName",
    "is_stock": "",
    "is_website": "",
    "is_invest": "",
    "is_guar": "",
    "main_activity": "mainBusiAct",
    "relation": ""
}

"""
    type>>>>{data:[]}
    Type     string     `json:"type" key:"合伙人类型,股东（发起人）类型,股东类型,出资人类型,发起人类型,出资方式,投资人类型,主管部门类型" sd:"invtype"`
    Name     string     `json:"name" key:"股东,出资人,姓名,发起人,投资人,人,股东名称,名称" sd:"inv"`
    CertType string     `json:"cert_type" key:"证件类型,证照类型" sd:"blictype"`
    CertNo   string     `json:"cert_no" key:"证件号码,证照号码" sd:"blicno"`
    SubCapi  string     `json:"sub_capi,omitempty" key:"认缴额,认缴" sd:"lisubconam"`
    ActCapi  string     `json:"act_capi,omitempty" key:"实缴额,实缴" sd:"liacconam"`
    Subs     []CapiInfo `json:"subs,omitempty"`
    Acts     []CapiInfo `json:"acts,omitempty"`
            Type string `json:"type" key:"类型,方式"`
            Capi string `json:"capi" key:"出资额,额"`
            Date string `json:"date" key:"日期,时间"`

    "subs()": "subDetails()",
    "acts()": "aubDetails()",
    "aubDetails": {
        "type": "acConForm_CN",
        "capi": "liAcConAm",
        "date": "acConDate",
    },
    "subDetails": {
        "type": "subConFormName",
        "capi": "liSubConAm",
        "date": "subConDate",
    }
"""
reInvester = {
    "Type":"",
    "name": "invName",
    "CertType":"",
    "CertNo":"",
    "sub_capi": "liSubConAm",
    "act_capi": "liAcConAm",
    "subs":"",
    "acts":""
}

"""
    // 保证担保
    type GuaranteeInfo struct {
        Creditor   string `json:"creditor" key:"债权人" sd:"more"`
        Debtor     string `json:"debtor" key:"债务人" sd:"mortgagor"`
        DebtKind   string `json:"debt_kind" key:"主债权种类" sd:"priclaseckind"`
        DebtAmount string `json:"debt_amount" key:"主债权数额" sd:"priclasecam"`
        DebtTerm   string `json:"debt_term" key:"履行债务的期限" sd:"pefperfrom"`
        GuarTerm   string `json:"guar_term" key:"保证的期间" sd:"guaranperiod"`
        GuarType   string `json:"guar_type" key:"方式,保证的方式" sd:"gatype"`
    }
"""
reGuarteen = {
    "creditor": "more",
    "debtor": "mortgagor",
    "debt_kind": "priClaSecKind",  # ?
    "debt_amount": "priClaSecAm",
    "debt_term": "pefPerForm-pefPerTo",
    "guar_term": "guaranperiod",
    "guar_type": "gaType"
}

"""
    // 变更事项
    type ChangeInfo struct {
        Item   string `json:"item" key:"项" sd:"altitem,altfield"`
        Before string `json:"before" key:"前" sd:"altbe,altbefore"`
        After  string `json:"after" key:"后" sd:"altaf,altafter"`
        Date   string `json:"date" key:"时间,日期" sd:"altdate"`
    }
"""
reChange = {
    "item": "alitem",
    "before": "altBe",
    "after": "altAf",
    "date": "altDate",
}

"""
    // 网站或者网店信息
    type WebsiteInfo struct {
        Name string `json:"name" key:"名称" sd:"websitname"`
        Type string `json:"type" key:"类型" sd:"webtype"`
        Url  string `json:"url" key:"网址" sd:"domain"`
    }
"""
reWebsite = {
    "name": "webSitName",
    "type": "webType",  # ?
    "url": "domain"
}

"""
    // 对外投资信息
    type InvEntInfo struct {
        Name  string `json:"name" key:"名称" sd:"entname"`
        RegNo string `json:"reg_no" key:"注册号,信用代码" sd:"regno"`
    }
"""
reInvestEnt = {
    "name": "entName",
    "reg_no": "uniscId"
}

"""
    // 股权变更信息
    type StockChangeInfo struct {
        Stockholder string `json:"stockholder" key:"股东,发起人" sd:"inv"`
        Before      string `json:"before" key:"变更前" sd:"transamprpre"`
        After       string `json:"after" key:"变更后" sd:"transampraft"`
        Date        string `json:"date" key:"变更日期" sd:"firstpubtime"`
    }
"""
reStockChange = {
    "stockholder": "inv",
    "before": "transAmPr",
    "after": "transAmAft",
    "date": "altDate",
}

"""
    // 行政许可信息
    type LicenseInfo struct {
        No      string `json:"no,omitempty" key:"编号" sd:"licno"`
        Name    string `json:"name" key:"名称" sd:"licname"`
        From    string `json:"from,omitempty" key:"有效期自" sd:"valfrom"`
        To      string `json:"to" key:"有效期至" sd:"valto"`
        Org     string `json:"org,omitempty" key:"机关" sd:"licanth"`
        Content string `json:"content,omitempty" key:"内容" sd:"licitem"`
        State   string `json:"state,omitempty" key:"状态" sd:"type"`
    }
"""
reLicence = {
    "no": "",
    "name": "licName_CN",
    "from": "",
    "to": "valTo",
    "org": "",
    "content": "",
    "state": "",
}

"""
    // 生产经营
    type OperationInfo struct {
        TotalAsset    string `json:"total_asset" key:"资产总额"`
        TotalTax      string `json:"total_tax" key:"纳税金额,纳税总额"`
        TotalDebt     string `json:"total_debt" key:"负债总额"`
        MainIncome    string `json:"main_income" key:"主营务业收入,营业总收入中主营业务收入,主营业务"`
        TotalTurnover string `json:"total_turnover" key:"营业收入,营业总收入,总收入,销售额,销售总额,营业额"`
        TotalProfit   string `json:"profit" key:"利润总额,盈余总额"`
        NetProfit     string `json:"net_profit" key:"净利润"`
        TotalEquity   string `json:"total_equity" key:"权益合计"`
        FinancialLoan string `json:"financial_loan,omitempty" key:"金融贷款"`
        FundSubsidy   string `json:"fund_subsidy,omitempty" key:"获得政府扶持资金,补助"`
    }
"""
reOperation = {
    "total_asset": "assGro",
    "total_tax": "ratGro",
    "total_debt": "liaGro",
    "main_income": "vendInc",
    "total_turnover": "maiBusInc",
    "profit": "proGro",
    "net_profit": "netInc",
    "total_equity": "totEqu",
    "financial_loan": "",
    "fund_subsidy": ""
}

"""
    // 分支机构
    type BranchInfo struct {
        Name   string `json:"name" key:"名称" sd:"brname"`
        RegNo  string `json:"reg_no" key:"注册号,信用代码" sd:"regno,farspeartregno"`
        RegOrg string `json:"reg_org" key:"登记机关" sd:"regorg"`
    }
"""
reBranch = {
    "name": "brName",
    "reg_no": "uniscId",
    "reg_org": ""
}

"""
    // 抽查检查信息
    type SpotCheckInfo struct {
        CheckOrg string `json:"check_org" key:"机关" sd:"insauthname"`
        Type     string `json:"type" key:"类型" sd:"instype"`
        Date     string `json:"date" key:"日期" sd:"insdate"`
        Result   string `json:"result" key:"结果" sd:"insres"`
    }
"""
busSpotCheck = {
    "check_org": "insAuth_CN",
    "type": "insType_CN",
    "date": "insDate",
    "result": "insRes_CN"
}

"""
    // 知识产权出质登记信息
    type IntellInfo struct {
        No      string `json:"no" key:"编号,号,代码" sd:"tmregno"`
        Name    string `json:"name" key:"名称" sd:"tmregno"`
        Kind    string `json:"kind" key:"种类,类别" sd:"kinds"`
        Pledgor string `json:"pledgor" key:"出质人" sd:"pledgor"`
        Pledgee string `json:"pledgee" key:"质权人" sd:"imporg"`
        Term    string `json:"term" key:"期限" sd:"pleregperfrom"`
        State   string `json:"state" key:"状态" sd:"type"`
    }
"""
busItelPlege = {
    "no": "tmRegNo",
    "name": "tmName",
    "kind": "kinds",
    "pledgor": "pledgor",
    "pledgee": "impOrg",
    "term": "pleRegPerFrom-pleRegPerTo",
    "state": "type"
}

"""
    // 经营异常
    type AbnormalInfo struct {
        AddCause    string `json:"add_cause" key:"列入经营异常,标记经营异常,纳入经营" sd:"specause"`
        AddDate     string `json:"add_date" key:"列入日期,标记日期" sd:"abntime"`
        DecOrg      string `json:"dec_org" key:"机关" sd:"decorg"`
        RemoveCause string `json:"remove_cause" key:"移出经营,恢复正常" sd:"remexcpres"`
        RemoveDate  string `json:"remove_date" key:"移出日期,恢复日期" sd:"remdate"`
    }
"""
busAbnormal = {
    "add_cause": "speCause_CN",
    "add_date": "abntime",
    "dec_org": "decOrg_CN",
    "remove_cause": "remExcpRes_CN",
    "remove_date": "remDate"
}

"""
    // 变更事项
    type ChangeInfo struct {
        Item   string `json:"item" key:"项" sd:"altitem,altfield"`
        Before string `json:"before" key:"前" sd:"altbe,altbefore"`
        After  string `json:"after" key:"后" sd:"altaf,altafter"`
        Date   string `json:"date" key:"时间,日期" sd:"altdate"`
    }
"""
busChange = {
    "item": "altItem_CN",
    "before": "altAf",
    "after": "altBe",
    "date": "altDate",

}

"""
    // 成员信息
    // 参加经营的家庭成员姓名
    type MemberInfo struct {
        Name     string `json:"name" key:"姓名" sd:"name"`
        Position string `json:"position" key:"职务" sd:"position"`
    }
"""
busMemberInfo = {
    "name": "name",
    "position": "position_CN",  # picture need to change
}

"""
    // 股东信息
    // 投资人信息
    // 发起人
    // 主管部门（出资人）信息
    type InvestorInfo struct {
        Type     string     `json:"type" key:"合伙人类型,股东（发起人）类型,股东类型,出资人类型,发起人类型,出资方式,投资人类型,主管部门类型" sd:"invtype"`
        Name     string     `json:"name" key:"股东,出资人,姓名,发起人,投资人,人,股东名称,名称" sd:"inv"`
        CertType string     `json:"cert_type" key:"证件类型,证照类型" sd:"blictype"`
        CertNo   string     `json:"cert_no" key:"证件号码,证照号码" sd:"blicno"`
        SubCapi  string     `json:"sub_capi,omitempty" key:"认缴额,认缴" sd:"lisubconam"`
        ActCapi  string     `json:"act_capi,omitempty" key:"实缴额,实缴" sd:"liacconam"`
        Subs     []CapiInfo `json:"subs,omitempty"`
        Acts     []CapiInfo `json:"acts,omitempty"`
    }
"""
busInvesterInfo = {
    "type": "invType_CN",
    "name": "inv",
    "cert_type": "cerType_CN",
    "cert_no": "bLicNo",
    "sub_capi": "liSubConAm",
    "act_capi": "liAcConAm",
    "subs": "",
    "acts": "",
}

"""
    // 出质信息
    type PledgeInfo struct {
        No           string `json:"no" key:"登记编号" sd:"equityno"`
        Pledgor      string `json:"pledgor" key:"出质人" sd:"pledgor"`
        PledgorNo    string `json:"pledgor_no" sd:"blicno"`
        EquityAmount string `json:"equity_amount" key:"股权数额" sd:"impam"`
        Pledgee      string `json:"pledgee" key:"质权人" sd:"imporg"`
        PledgeeNo    string `json:"pledgee_no" sd:"impmorblicno"`
        Date         string `json:"date" key:"登记日期,日期" sd:"equpledate"`
        State        string `json:"state" key:"状态" sd:"type"`
    }
    # json:"state" key:"状态"

    num = i.get("type")
    if num==3:
        item["state"] = ""
    elif num==1:
        item["state"] = "有效"
"""
busSockPlegeInfo = {
    "no": "equityNo",
    "pledgor": "pledgor",
    "pledgor_no": "pledBLicNo",
    "equity_amount": "impAm",
    "pledgee": "impOrg",
    "pledgee_no": "impOrgBLicNo",
    "date": "equPleDate",
    "state": "type",  #
}

"""
    // 行政处罚
    type PunishInfo struct {
        No      string `json:"no" key:"书文号" sd:"pendecno"`
        Name    string `json:"name" key:"名称" sd:"uname"`
        RegNo   string `json:"reg_no" key:"注册号,信用代码" sd:"regno"`
        LegRep  string `json:"leg_rep" key:"经营者,人,姓名" sd:"lerep"`
        Type    string `json:"type" key:"违法行为类型,处罚事由" sd:"illegacttype"`
        Content string `json:"content" key:"处罚种类,行政处罚内容,处罚依据" sd:"pentype"`
        DecOrg  string `json:"dec_org" key:"机关,作出行政处罚机关名称" sd:"penauth"`
        Date    string `json:"date" key:"日期" sd:"pendecissdate"`
        Detail  string `json:"detail" key:"地址" sd:""`
        Remark  string `json:"remark" key:"备注" sd:"remark"`
    }
"""
busPunish = {
    "no": "penDecNo",
    "name": "",
    "reg_no": "",
    "leg_rep": "",
    "type": "",
    "content": "penContent",
    "dec_org": "penAuth_CN",
    "date": "penDecIssDate",
    "detail": "",
    "remark": ""
}

"""
    // 行政许可信息
    type LicenseInfo struct {
        No      string `json:"no,omitempty" key:"编号" sd:"licno"`
        Name    string `json:"name" key:"名称" sd:"licname"`
        From    string `json:"from,omitempty" key:"有效期自" sd:"valfrom"`
        To      string `json:"to" key:"有效期至" sd:"valto"`
        Org     string `json:"org,omitempty" key:"机关" sd:"licanth"`
        Content string `json:"content,omitempty" key:"内容" sd:"licitem"`
        State   string `json:"state,omitempty" key:"状态" sd:"type"`
    }
"""
busLicence = {
    "no": "licNo",
    "name": "licName_CN",
    "from": "valFrom",
    "to": "valTo",
    "org": "licAnth",
    "content": "licItem",
    "state": "status",
}

busBaseInfo = {

}

""""
    // 抵押权人概况
    type MortgagerInfo struct {
        Name     string `json:"name" key:"抵押权人名称,名称" sd:"more"`
        CertType string `json:"cert_type" key:"证件类型" sd:"blictype"`
        CertNo   string `json:"cert_no" key:"证件号码" sd:"blicno"`
        Address  string `json:"address,omitempty" key:"住所"`
    }

    // 被担保债权概况
    type ObligeeInfo struct {
        Kind     string `json:"kind" key:"种类" sd:"priclaseckind"`
        Amount   string `json:"amount" key:"数额" sd:"priclasecam"`
        Scope    string `json:"scope" key:"担保的范围" sd:"warcov"`
        DebtTerm string `json:"debt_term" key:"期限"`
        Remark   string `json:"remark" key:"备注" sd:"remark"`
    }
    // 抵押物概况
    type PawnInfo struct {
        Name   string `json:"name" key:"名称" sd:"guaname"`
        Owner  string `json:"owner" key:"所有权" sd:"own"`
        Status string `json:"status" key:"数量,质量,状况" sd:"guades"`
        Remark string `json:"remark" key:"备注" sd:"remark"`
    }
    // 动产抵押信息
    type MortgageInfo struct {
        No          string          `json:"no" key:"登记编号" sd:"morregcno"`
        RegOrg      string          `json:"reg_org" key:"登记机关" sd:"regorg"`
        RegDate     string          `json:"reg_at" key:"登记日期" sd:"regidate"`
        DebtType    string          `json:"debut_type" key:"种类" sd:""`
        DebtAmount  string          `json:"debt_amount" key:"数额" sd:"priclasecam"`
        DebtTerm    string          `json:"debt_term" key:"期限" sd:"pefperform"`
        SecureScope string          `json:"secure_scope" key:"范围"`
        State       string          `json:"state" key:"状态" sd:"type"`
        Remark      string          `json:"remark" key:"备注" sd:"remark"`
        Obligee     ObligeeInfo     `json:"obligee"`
        Mortgagers  []MortgagerInfo `json:"mortgagers"`
        Pawns       []PawnInfo      `json:"pawns"`
        Alters      []AlterInfo     `json:"alters"`
    }
"""
busMortgageInfo = {
    "no":"morRegCNo",
    "reg_org":"regOrg_CN",
    "reg_at": "canDate",
    "debut_type": "type_CN",
    "debt_amount": "priClaSecAm",
    "debt_term": "",
    "secure_scope": "",
    "state": "",
    "remark": "",
    "obligee": "",
    "mortgagers": "",
    "pawns": "",
    "alters": "",
}

"""
    // 分支机构
    type BranchInfo struct {
        Name   string `json:"name" key:"名称" sd:"brname"`
        RegNo  string `json:"reg_no" key:"注册号,信用代码" sd:"regno,farspeartregno"`
        RegOrg string `json:"reg_org" key:"登记机关" sd:"regorg"`
    }
"""
busBranchInfo = {
    "name":"brName",
    "reg_no":"regNo",
    "reg_org":"regOrg_CN",
    "unisc_id":"uniscId"
}