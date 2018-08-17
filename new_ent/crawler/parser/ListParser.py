# -*- coding: utf-8 -*-
"""
@Time : 18-1-9 上午8:41
@Author : courage
@Site : 
@File : ListParser.py
@Software: PyCharm
"""

from lxml.html import etree

class ListParser():

    @classmethod
    def parser(cls,content=""):
        if len(content)==0:
            return None
        elif '查询到<span class="search_result_span1">0</span>条信息' in content:
            return "not_found"
        else:
            doc = etree.HTML(content)
            urls = doc.xpath("//a[@class='search_list_item db']/@href")
            if len(urls)>0:
                return [urls[0]]
            else:
                return None