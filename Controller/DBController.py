#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-29


from Model.MessageModel import Base
from Model.MessageModel import MessageModel
from Utils.DBInit import DBInit

class DBController(DBInit):
    """数据库控制类"""
    def init_db(self):
        """定义初始化数据库函数"""
        Base.metadata.create_all(self.engine) # Create a Schema


    def drop_db(self):
        """删除数据库函数"""
        Base.metadata.drop_all(self.engine)
        

