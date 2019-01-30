#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: andre
# Created Time:  2019-1-30
#############################################


from setuptools import setup, find_packages

setup(
    name = "httpautotest",
    version = "2.0.0",
    keywords = ("pip", "pathtool","http", "test", "api"),
    description = "httpapi test frameword",
    long_description = "httpapi test frameword",
    license = "MIT Licence",

    url = "https://github.com/r455678/httpautotest/tree/master/httpautotest",
    author = "r455678",
    author_email = "717577064@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = [requests,xlrd,pymysql]
)