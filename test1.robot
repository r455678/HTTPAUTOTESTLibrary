*** Settings ***
Library           httpautotest

*** Variables ***
${case}           ${CURDIR}${/}case1.xlsx
${db}             host='192.168.20.155',db='zlax_test',user='test',port=3306,passwd='test123'
${url}            http://192.168.20.154

*** Test Cases ***
无需数据库校验
    Testcase    ${url}    测试1    ${case}    1    ${db}

需要数据库校验
    Testcase    ${url}    测试1    ${case}    2    ${db}

单接口
    ${a}    Testcase One    ${url}    测试1    ${case}    2
    ${j}    To Json    ${a}
    log    ${j['msg']}
