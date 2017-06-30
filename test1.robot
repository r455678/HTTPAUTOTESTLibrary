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
    ${res1}    Testcase One    ${url}    zkk    ${case}    1
    ${to_j}    To Json    ${res1}
    Set Global Variable    ${token}    ${to_j['data']['token']}
    ${res_2}    Testcase One    ${url}    zkk    ${case}    2    token=${token}
