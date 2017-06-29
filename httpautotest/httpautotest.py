#!/usr/bin/env python
# coding:utf8
# author andre.yang

import requests
import xlrd
import urllib,sys
from requests.adapters import HTTPAdapter
import pymysql
import robot
from urllib import urlencode
from robot.libraries.BuiltIn import BuiltIn
import logging


try:
    from requests_ntlm import HttpNtlmAuth
except ImportError:
    pass

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

class myURLOpener(urllib.FancyURLopener):
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

class httpautotest(myURLOpener):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache('No sessions created')
        self.builtin = BuiltIn()

    def _utf8_urlencode(self, data):
        if type(data) is unicode:
            return data.encode('utf-8')

        if not type(data) is dict:
            return data

        utf8_data = {}
        for k, v in data.iteritems():
            utf8_data[k] = unicode(v).encode('utf-8')
        return urlencode(utf8_data)

    """
    打开excel
    """
    def openexcel(self, excelurl,sheetname):
        bk = xlrd.open_workbook(excelurl)
        try:
            sh = bk.sheet_by_name(sheetname)
            return sh
        except:
            print "no sheet in %s named %s" % (excelurl, sheetname)
            exit()

    """
    读取excel参数
    """
    def getexcelparas(self,sheetname,exceldir,num):
        sh = self.openexcel(exceldir, sheetname)
        try:
            row_data=sh.row_values(int(num))
        except Exception, e:
            print u'所选列没有数据'
        return row_data


    #数据校验方法
    def checkdb(self,host,dbname,username,password,port,excelurl,sheetname,rownum):
        """
        'host': dbhost

        'dbname': database's name

        'username': dbusername

        'password': dbpassword
        
        'port': dbport
        
        'excelurl': exp D://downloads/case.xls
        
        sheetname: sheet's name exp sheet1
        
        rownum :row num
        """
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            passwd=password,
            db=dbname,
            charset='utf8'
        )
        cur = conn.cursor()
        ischeckdb = self.getexcelparas(sheetname, excelurl, rownum)[5]
        sqlscript = self.getexcelparas(sheetname, excelurl, rownum)[6]
        expectedvalue=self.getexcelparas(sheetname, excelurl, rownum)[7]
        if ischeckdb == 1:
            size = cur.execute(sqlscript)
            if size> 0:
                logging.info(u"查询出数据条数为 "+str(size)+u" 条")
                info = cur.fetchmany(1)
                if info[0][0]==expectedvalue:
                    logging.info(u"数据库校验通过")
                else:
                    logging.info(u"数据库校验未通过,预期值: "+str(expectedvalue).replace('.0',''))
                    logging.info(u" 实际值: "+str(info[0][0]))
                    raise AssertionError()
            else :
                logging.info(u"数据库中没有查询到数据")
                raise AssertionError

        elif ischeckdb == 'FLASE' or ischeckdb == '':
            logging.info(u"不进入SQL判断")
        else :
            logging.info(u'第'+str(rownum)+u'行'+u'是否检查数据库输入不合法')
            raise RuntimeError
        cur.close()
        conn.commit()
        conn.close()

    #数据校验
    def checkdata(self,domain,descontent,remethod,payload,do):
        """
        'domain': server host

        'descontent': wish content

        'remethod': request method

        'payload': params

        'do': request do
        """
        descontent = descontent.replace("\n","")
        descontent = descontent.replace(" ", "")
        descontent = descontent.encode("utf-8")
        payload=payload.encode("utf-8")
        logging.info (u'请求参数为:' + str(payload))
        if remethod.upper() == 'GET':
            res = requests.get(domain + do, params=payload, timeout=3)
            if res.status_code != 200:
                logging.info(u"请求失败,statuscode非200")
                raise AssertionError
            logging.info(u"实际响应数据为:" + res.content.replace(" ", ""))
            resreplace=res.content.replace(" ", "")
            if descontent == resreplace:
                logging.info(u"接口断言通过")
            else:
                logging.info(u"接口断言与期望不符")
                raise AssertionError
        elif remethod.upper() == 'POST':
            res = requests.post(domain + do, params=payload, timeout=3)
            if res.status_code != 200:
                logging.info(u"请求失败,statuscode非200")
                raise AssertionError
            logging.info(u"实际响应数据为:"  + res.content.replace(" ", ""))
            resreplace=res.content.replace(" ", "")
            if descontent == resreplace:
                logging.info(u"接口断言通过")
            else:
                logging.info(u"与期望不符")
                logging.info(u"预期结果为"+descontent)
                raise AssertionError
        else:
            logging.info(u'请求方式错误')
            logging.info(u'请求方式只能为get/post,现为' + remethod)
            raise AssertionError

    def checktype(self, db):
        if type(db) == type({}):
            logging.info(u"数据库配置不为字典类型")
            raise AssertionError
        else:
            pass

    #case执行方法
    def testcase(self,domain,sheetname,excelurl,rownum,db):

        """
        'domain': host
        
        'sheetname': sheet's name exp sheet1
        
        'excelurl': exp D://downloads/case.xls
        
        'rownum': row number
        
        'db': database config
        
        Examples:
        | `Testcase` | http://192.168.20.154 | zkk | ${CURDIR}${/}case1${/}case1.xlsx | 1 | ${db} |
        """
        '''
        print domain
        print sheetname
        print excelurl
        print rownum
        print db
        '''
        logging.info(u'用例名称: '+self.getexcelparas(sheetname, excelurl, rownum)[0])
        do=self.getexcelparas(sheetname, excelurl, rownum)[1]
        remethod=self.getexcelparas(sheetname, excelurl, rownum)[2]
        payload=self.getexcelparas(sheetname, excelurl, rownum)[3]
        descontent=self.getexcelparas(sheetname, excelurl, rownum)[4]
        self.checkdata(domain,descontent, remethod, payload, do)
        db=eval('dict(%s)' % db)
        self.checkdb(db['host'], db['db'], db['user'],db['passwd'],db['port'],excelurl, sheetname, rownum)
