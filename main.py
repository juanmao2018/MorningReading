#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-27

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
# myfont = matplotlib.font_manager.FontProperties(fname=r'C:/Windows/Fonts/SimHei.ttf') 
plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

from Controller.DBController import DBController
from Model.MessageModel import MessageModel
from Controller.Cleaning.GetRecord import GetRecord
from Controller.Cleaning.CleanMessage import CleanMessage
from Controller.Persistence.StoreMessage import StoreMessage
from Controller.Analysis.MessageAnalysis import CollectionAnalysis
from Controller.Analysis.MessageAnalysis import PersonAnalysis
from View.SaveMessageAnalysis import SaveMessageAnalysis


def main():
    DBCtrl = DBController()
    
    DBCtrl.init_db() # -- 建表模型

    # --消息入库
    recordLst = GetRecord().get_record("sample\\")
    # print(len(recordLst))
    StoreMsg = StoreMessage(DBCtrl)
    for record in recordLst:
        msgLst = CleanMessage(record).clean_message()
        StoreMsg.store_message(msgLst)
        # print(len(msgLst))

    
    # -- 集合分析
    ClctAnls = CollectionAnalysis(DBCtrl)
    rows = ClctAnls.query_userList()
    rows = ClctAnls.query_userNum_wordLen_everyday()
    rows = ClctAnls.query_dayNum_wordLen_rank()
    ClctAnls.get_description()
    # print(ClctAnls)

    targetUseruid = '555555'
    # -- 个人分析
    PsnAnls = PersonAnalysis(DBCtrl, targetUseruid, ClctAnls.get_rank_by_useruid(targetUseruid))
    rows = PsnAnls.query_name_by_useruid()
    rows = PsnAnls.query_wordLen_checkFlag_everyday()
    PsnAnls.get_description()

    # -- 分析结果存储
    SaveMsgAnls = SaveMessageAnalysis('outputs\\')
    SaveMsgAnls.save_message_analysis(ClctAnls, PsnAnls, '统计结果')



if __name__ == '__main__':
    main()   
