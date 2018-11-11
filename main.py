#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-27

import pandas as pd
# import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# myfont = matplotlib.font_manager.FontProperties(fname=r'C:/Windows/Fonts/SimHei.ttf') 
plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

from Utils.Figure import Figure
from Controller.DBController import *
from Model.MessageModel import MessageModel
from Controller.Cleaning.GetRecord import GetRecord
from Controller.Cleaning.CleanMessage import CleanMessage
from Controller.Persistence.StoreMessage import StoreMessage
from Controller.Analysis.MessageAnalysis import CollectionAnalysis
from View.SaveMessageAnalysis import SaveMessageAnalysis


def main():
    DBOprt = DBOperator()
    
    # -- 建表模型
    # DBOprt.init_db()

    # # --消息入库
    # recordLst = GetRecord().get_record(Figure.pathInfo['inputPath'])
    # # # print(len(recordLst))
    # StoreMsg = StoreMessage()
    # for record in recordLst:
    #     msgLst = CleanMessage(record).clean_message()
    #     StoreMsg.store_message(msgLst)
    #     print(len(msgLst))

    
    # -- 集合分析（包含个体分析）
    ClctAnls = CollectionAnalysis()
    rows = ClctAnls.query_userLst()
    rows = ClctAnls.query_userNum_wordLen_everyday()
    rows = ClctAnls.query_dayNum_wordLen_rank()
    ClctAnls.get_description()
    ClctAnls.get_psnAnlsLst([]) # 列表为空，所有的个体分析
    # print(ClctAnls)

    # # -- 分析结果保存
    SaveMsgAnls = SaveMessageAnalysis(Figure.pathInfo['outputPath'])
    SaveMsgAnls.save_message_analysis(ClctAnls, Figure.fileName)



if __name__ == '__main__':
    main()   
