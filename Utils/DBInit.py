#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-27

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBInit(object):
    """数据库配置信息、初始化类"""
    def __init__(self):
        DBInfo = {
            'HOSTNAME' : 'localhost',
            'PORT' : '3306',
            'DATABASE' : 'test',
            'USERNAME' : 'test',
            'PASSWORD' : '123456'
        }
        self.DB_URI = "mysql+pymysql://%(USERNAME)s:%(PASSWORD)s@%(HOSTNAME)s:%(PORT)s/%(DATABASE)s" % DBInfo
        self.engine = create_engine(self.DB_URI, max_overflow=5, echo=False) # Connecting
        self.Session = sessionmaker(bind=self.engine)
        self.dbSession = self.Session()

