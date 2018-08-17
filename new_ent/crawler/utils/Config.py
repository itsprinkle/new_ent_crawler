#[machine_name]
MCNAME = "proudark000"

#配置数据库
#[mysql]
DBHOST = "180.76.172.153"
DBPORT = 3306
DBUSER = "crawler"
DBPWD = "ark#2017"
DBNAME = "ent"
DBCHAR = "utf8"

#[redis]
RDHOST = "180.76.164.253"
RDPORT = 6379
RDPWD = "ark@2017"
RQUEUE = "queue"
#用于dispatcher工作的队列
RDQNAME = "keyword"
RDQNAME1 = "keyword1"
#用于worker工作的队列
RWQNAME = "keyword"

#[requests]
timeout = 20

#[database table]

# bus = "business_info_copy"
# ent = "enterprise_info_copy"
# reprot = "report_info_copy"
# keyword = "keyword_info"
# keyword = "lingang_keyword_info"

bus = "business_info"
ent = "enterprise_info"
reprot = "report_info"
keyword = "keyword_info"
mainUrl = "main_url_record"

#[jiasule ]



#[worker thread count]
thread = 4

#[http request exception retry count]
retry_count = 4