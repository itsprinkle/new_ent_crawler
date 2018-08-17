# -*- coding: utf-8 -*-

"""
@Time : 18-1-5 下午3:44
@Author : courage
@File : utils.py
@Software: PyCharm
"""

import time
from crawler.utils.JiaSuLe import JiaSuLe
import subprocess
import os

class ADSL(object):

    @staticmethod
    def exe(province,pd=False):
        if pd :
            while True :
                JiaSuLe.remove(province)
                count = 0
                (status, output) = subprocess.getstatusoutput('pppoe-stop')
                if status == 0:
                    count += 1
                    print("pppoe-stop ok --", output)
                else:
                    print("pppoe-stop err --", output)
                (status, output) = subprocess.getstatusoutput('pppoe-start')
                if status == 0:
                    count += 1
                    print("pppoe-start ok --", output)
                else:
                    print("pppoe-start err --", output)
                time.sleep(2)

                exit_code = os.system('ping www.baidu.com -c 2')
                if exit_code:
                    print("pppoe-faild")
                else:
                    return count
        return 0