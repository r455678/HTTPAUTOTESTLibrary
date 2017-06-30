#!/usr/bin/env python
# coding:utf8
# author andre.yang

from httpautotest import requests

class httpautotestone():

    @staticmethod
    def getres(domain, remethod, payload, do):
        payload = payload.encode("utf-8")
        if remethod == 'get':
            res = requests.get(domain + do, params=payload, timeout=3)
            resd = res.content.decode("utf-8")
            return resd
        elif remethod == 'post':
             res =requests.post(domain + do, params=payload, timeout=3)
             resd=res.content.decode("utf-8")
             return resd