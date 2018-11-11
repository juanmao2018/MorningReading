#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-29

from Controller.DBController import DB_ScopedSession
from Model.MessageModel import MessageModel


class StoreMessage(object):
    """ 将消息保存在数据"""
    def __init__(self):
        pass

    def store_message(self, msgLst):
        dbSession = DB_ScopedSession()
        try:
            # dbSession.add_all(msgLst) # 要求列表元素为类
            msgDctLst = [item.__dict__ for item in msgLst] # 将类转化为字典
            # dbSession.bulk_insert_mappings(MessageModel, msgDctLst)  # 要求列表元素为字典
            dbSession.execute(MessageModel.__table__.insert().prefix_with('IGNORE'), msgDctLst)   # 要求列表元素为字典
            dbSession.commit()
        except Exception as e:
            dbSession.rollback()
            raise
        else:
            # print('插入' + str(len(msgLst)) + '个数据')
            pass
        finally:
            dbSession.close()
            # DB_ScopedSession.remove()
