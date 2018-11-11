#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-29

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from Utils.Figure import Figure
from Model.MessageModel import Base



DB_URL = "mysql+pymysql://%(USERNAME)s:%(PASSWORD)s@%(HOSTNAME)s:%(PORT)s/%(DATABASE)s" \
    % Figure.DBInfo
DB_engine = create_engine(DB_URL, 
    max_overflow=0, # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    echo=False # 是否开启提示
)
DB_session_factory = sessionmaker(bind=DB_engine)
DB_ScopedSession = scoped_session(DB_session_factory)


class DBOperator():
    """数据库控制类"""
    def init_db(self):
        """定义初始化数据库函数"""
        Base.metadata.create_all(DB_engine) # Create a Schema

    def drop_db(self):
        """删除数据库函数"""
        Base.metadata.drop_all(DB_engine)
        

