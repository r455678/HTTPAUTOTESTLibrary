#!/usr/bin/env python
# coding:utf8
# author andre.yang
import requests, xlrd, pymysql,logging, json
from robot.libraries.BuiltIn import BuiltIn

class httpautotest():
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.builtin = BuiltIn()

    #打开excel
    def _openexcel(self, excelurl, sheetname):
        bk = xlrd.open_workbook(excelurl)
        try:
            sh = bk.sheet_by_name(sheetname)
            return sh
        except:
            logging.info("no sheet in %s named %s" % (excelurl, sheetname))

    #读取excel参数
    def _getexcelparams(self, sheetname, exceldir, num):
        sh = self._openexcel(exceldir, sheetname)
        rows = sh.nrows
        if int(num) >= int(rows):
            logging.info(u"所选列超出最大行")
        try:
            row_data = sh.row_values(int(num))
            return row_data
        except:
            logging.info(u"所选列没有数据")

    def _todict(self, db):
        try:
            redb=eval('dict(%s)' % db)
        except:
            return (u'数据库配置错误')
        return redb

    #数据库校验
    def _checkdb(self, rownum, **kwargs):
        if 'db' in kwargs:
            db = self._todict(kwargs['db'])
            sqlscript = self.data[5]
            expectedvalue = self.data[6]
            if sqlscript:
                conn = pymysql.connect(
                    host=db['host'],
                    port=int(db['port']),
                    user=db['user'],
                    passwd=db['password'],
                    db=db['dbname'],
                    charset='utf8'
                )
                cur = conn.cursor()
                try:
                    size = cur.execute(sqlscript)
                except:
                    logging.info(u'第' + str(rownum) + u'行' + u'是否检查数据库输入不合法')
                    raise RuntimeError
                cur.close()
                conn.commit()
                conn.close()
                if size > 0:
                    logging.info(u"查询出数据条数为 " + str(size) + u" 条")
                    info = cur.fetchmany(1)
                    infol = list(info[0])
                    arr = expectedvalue.split(',')
                    for i in range(len(infol)):
                        infol[i] = str(infol[i]).encode("utf-8")
                    for i in range(len(arr)):
                        arr[i] = str(arr[i]).encode("utf-8")
                    infol.sort()
                    arr.sort()
                    if infol == arr:
                        logging.info(u"数据库校验通过")
                    else:
                        logging.info(u"数据库校验未通过,预期值: " + str(expectedvalue).replace('.0', ''))
                        logging.info(u"实际值: " + str(info[0][0]))
                        raise AssertionError()
                else:
                    logging.info(u"数据库中没有查询到数据")
                    raise AssertionError
            else:
                logging.info(u"不进入SQL判断")
        else:
            logging.info(u"不进入SQL判断")


    # 数据校验
    def _checkdata(self, res,**kwargs):
        """
        'domain': server host
        'descontent': wish content
        'remethod': request method
        'payload': params
        'do': request do
        """
        descontentreplace = self.data[4].replace("\n", "").replace(" ", "").replace("\t", "").replace("\r", "").encode("utf-8")
        ignorefields = self.data[7]
        logging.info(u'请求参数为:' + str(self.data[4]))
        resd = res.content.decode("utf-8")
        if res.status_code != 200:
            logging.info(u"请求失败,statuscode非200")
            raise AssertionError
        resreplace = resd.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "").encode("utf-8")
        ignorefieldsl=ignorefields.split(',')
        if ignorefields:
            try:
                dictdescontent = json.loads(descontentreplace)
                for i in range(len(ignorefieldsl)):
                    dictdescontent.pop(ignorefieldsl[i])
                descontent=json.dumps(dictdescontent, encoding='UTF-8', ensure_ascii=False)
            except:
                logging.info(u'预期结果非json格式')
                raise AssertionError
            logging.info(u'忽略校验字段为:' + str(ignorefields))
            resreplacel = json.loads(resreplace)
            for i in range(len(ignorefieldsl)):
                if json.loads(res.content):
                    logging.info(u"返回内容中无忽略字段,实际返回为"+res.content)
                    raise RuntimeError
                else:
                    resreplacel.pop(ignorefieldsl[i])
            resreplace2 = json.dumps(resreplacel, encoding='UTF-8', ensure_ascii=False)
        else:
            logging.info(u'无忽略校验字段')
            descontent=descontentreplace
            resreplace2=resreplace
        if descontent in resreplace2:
            logging.info(u"接口断言通过")
        else:
            logging.info(u"实际响应数据为:" + resreplace)
            logging.info(u"接口断言与期望不符,执行失败")
            logging.info(u"预期响应结果为:" + descontentreplace)
            raise AssertionError


    #发起请求
    def _excute_case(self,domain, do, method, payload, **kwargs):
        payload = payload.encode("utf-8")
        if 'params' in kwargs:
            payload = payload  + '&' +  kwargs['params']
        if 'headers' in kwargs:
            headers_t = kwargs['headers']
            logging.info(u"自定义请求头为"+headers_t)
            headers_t=headers_t.replace("'", "\"")
            headers=json.loads(headers_t)
        else:
            headers={'Content-type':'application/x-www-form-urlencoded'}
        if domain[-1] != '/' and do[0] !='/':
            host=domain + '/' + do
        else :
            host=domain+do
        session = requests.session()
        if method.upper() == 'GET':
            res=session.request('GET',host,params=payload,headers=headers,timeout=8)
        elif method.upper() == 'POST':
            res=session.request('POST',host, data=payload, headers=headers,timeout=8)
        else:
            logging.info(u'请求方式错误，只能为get/post,现为' + method.upper())
            raise AssertionError
        self._checkdata(res)

    # case执行方法
    def testcase(self, domain, excelurl,sheetname,rownum, **kwargs):
        """
        'domain': host
        'sheetname': sheet's name exp sheet1
        'excelurl': exp D://downloads/case.xls
        'rownum': row number exp 1
        'db': database config exp db={'host':'127.0.0.1','port':3306,'user':'root','password':'123456','dbname':'milor'}
        Examples:
        | `Testcase` | http://192.168.20.154 | zkk | ${CURDIR}${/}case1${/}case1.xlsx | 1 | db=${db} |
        """
        self.data=self._getexcelparams(sheetname, excelurl, rownum)
        logging.info(u'用例名称: ' + self.data[0])
        self._excute_case(domain,self.data[1],self.data[2],self.data[3],**kwargs)#data[0] 用例名称 data[1] 方法名 data[2] 请求方式 data[3] 请求参数 data[4] 预期结果
        self._checkdb(rownum, **kwargs)
'''
if __name__ == '__main__':
    T=httpautotest()
    T.testcase('http://localhost:8083','case1.xlsx','case',1,db={'host':'127.0.0.1','port':3306,'user':'root','password':'123456','dbname':'milor'})
'''
