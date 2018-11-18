#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-30

from sqlalchemy.orm import aliased
from sqlalchemy import text, case, outerjoin, func
import pandas as pd
import numpy as np
from decimal import *
import datetime, threading

from Utils.Figure import Figure
from Controller.DBController import DB_ScopedSession
from Model.MessageModel import MessageModel
Message = aliased(MessageModel, name='Message')


class CollectionAnalysis(object):
    """总体分析"""

    def __init__(self):
        self.userLst = [] # 用户号和用户名列表
        self.userNum_wordLen_everyday = [] # 每天的打卡的用户数和字数
        self.dayNum_wordLen_rank = [] # 每个用户的打卡天数、字数、排名
        self.descrip = ''
        self.psnAnlsLst = [] # 个体分析的结果列表


    def query_userLst(self):
        """查询参与打卡的用户号和昵称"""
        #   （存在一个用户有多个用户名的情况，用max()和group_by()筛选一个用户名）
        dbSession = DB_ScopedSession()
        rows = None
        try:
            rows = dbSession.query(Message.useruid, func.max(Message.useruname)).\
                group_by(Message.useruid).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['useruid', 'useruname'])
            self.userLst = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
        dbSession.close()
        return rows


    def query_userNum_wordLen_everyday(self):
        """查询每天的打卡人数和字数（一个人一天多次打卡仅统计一次）"""
        dbSession = DB_ScopedSession()
        rows = None
        try:
            rows = dbSession.query(Message.msgdate, 
                func.count(Message.useruid.distinct()).label('userNum'), 
                func.sum(Message.contentLen).label('wordLen')).group_by(Message.msgdate).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['date', 'checkUserNum', 'wordLen'])
            rows.set_index(["date"], inplace=True) # 指定某一列的值作为索引
            self.userNum_wordLen_everyday = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
        dbSession.close()
        return rows


    def query_dayNum_wordLen_rank(self):
        """查询每个用户的打卡天数、字数，并排名（按照天数、字数降序排列，一天多次打卡算一次）"""
        dbSession = DB_ScopedSession()
        rows = None
        try:
            stmt = dbSession.query(Message.useruid, func.count(Message.msgdate.\
                distinct()).label('dateNum')).group_by(Message.useruid).subquery()
            stmt2 = dbSession.query(Message.useruid, func.sum(Message.contentLen).\
                label('wordLen')).group_by(Message.useruid).subquery()
            rows = dbSession.query(stmt.c.useruid, stmt.c.dateNum, 
                stmt2.c.wordLen).filter(stmt.c.useruid==stmt2.c.useruid).\
                order_by(stmt.c.dateNum.desc(), stmt2.c.wordLen.desc()).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['useruid', 'checkDayNum', 'wordLen'])
            rows.index.names = ['rank']
            self.dayNum_wordLen_rank = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
        dbSession.close()
        return rows


    def get_rank_by_useruid(self, useruid):
        """通过用户号获取打卡排名"""
        rank = (0, 0)
        try:
            rankNum = self.dayNum_wordLen_rank[self.dayNum_wordLen_rank['useruid']==useruid].\
                index.tolist()[0]
            rank = (rankNum, 1 - rankNum/len(self.dayNum_wordLen_rank))
        except Exception as e:
            print('!Error: 没有该用户的排名信息')
        return rank


    def get_description(self):
        """描述分析结果"""
        descrip = ''
        descrip += '    %s%s活动自%s开始，\n阅读了书籍：' % (Figure.readingInfo['tag'], 
            Figure.readingInfo['term'], min(self.userNum_wordLen_everyday.index))
        for item in Figure.readingInfo['books']:
            descrip += '《' + item + '》'
        descrip += '。\n在这%s天中，共有%s人参与打卡。' % (len(self.userNum_wordLen_everyday), 
            len(self.dayNum_wordLen_rank))
        descrip += '\n每天打卡的人数及输出的文字数量如下图：'
        self.descrip = descrip
        return descrip


    def get_psnAnlsLst(self, targetUserLst=[]):
        """查询目标列表中的个体分析结果"""
        psnAnlsLst = []
        if len(targetUserLst) == 0:
            targetUserLst = self.userLst['useruid']
        # 定义线程池并创建线程对象
        threads = [threading.Thread(target=self.get_psnAnls, args=(item, psnAnlsLst)) for item in targetUserLst] # 创建线程
        for thrd in threads: # 启动所有线程
            thrd.start()
        for thrd in threads: # 等待线程运行完毕
            thrd.join() 
        self.psnAnlsLst = psnAnlsLst
        return psnAnlsLst


    def get_psnAnls(self, targetUseruid, psnAnlsLst):
        """查询个体分析结果"""
        with Figure.ThreadInfo['threadMaxnum']:
            # print("thread-%s is running %s" % (threading.current_thread().name, datetime.datetime.now()))
            PsnAnls = PersonAnalysis(targetUseruid, self.get_rank_by_useruid(targetUseruid))
            rows = PsnAnls.query_name_by_useruid()
            rows = PsnAnls.query_wordLen_checkFlag_everyday()
            PsnAnls.get_description()
            Figure.ThreadInfo['mutex'].acquire() # 取得锁
            psnAnlsLst.append(PsnAnls) 
            Figure.ThreadInfo['mutex'].release() # 释放锁
            # print("thread-%s ended %s" % (threading.current_thread().name, datetime.datetime.now()))
            return 1
         

    def __repr__(self):
        return "<%s(descrip=%s)>" % (self.__class__.__name__, self.descrip)
        
        

class PersonAnalysis(object):
    """个人分析"""
    def __init__(self, useruid, rank):
        self.useruid = useruid
        self.rank = rank
        self.useruname = ''
        self.wordLen_checkFlag_everyday = []
        self.descrip = ''


    def query_name_by_useruid(self):
        """查找指定用户号的用户名"""
        dbSession = DB_ScopedSession()
        rows = []
        try: # （存在一个用户由多个用户名的情况，用max()和group_by()删选一个）
            rows = dbSession.query(Message.useruid, func.max(Message.useruname)).\
            filter(text("useruid=:useruid")).params(useruid=self.useruid).all()
            self.useruname = rows[0][1]
        except Exception as e:
            print('!Error: 没有该用户的信息')
            raise e
        dbSession.close()
        return rows


    def query_wordLen_checkFlag_everyday(self):
        """查询指定用户号的每天的打卡字数和打卡标志"""
        dbSession = DB_ScopedSession()
        rows = None
        try:
            stmt = dbSession.query(Message.msgdate.distinct().label('msgdate')).subquery()
            stmt2 = dbSession.query(Message).filter(Message.useruid==self.useruid).subquery()
            caseStmt = case(
                [(func.sum(stmt2.c.contentLen) > 0, func.sum(stmt2.c.contentLen)),], 
                else_ = 0
            ).label('wordLen')
            caseStmt2 = case(
                [(stmt2.c.msgdate, 1),], else_ = 0
            ).label('checkFlag')
            rows = dbSession.query(stmt.c.msgdate, caseStmt, caseStmt2).\
                outerjoin(stmt2, stmt.c.msgdate==stmt2.c.msgdate).group_by(stmt.c.msgdate).\
                order_by(stmt.c.msgdate).all()
            rows = pd.DataFrame(rows, columns=['date', 'wordLen', 'checkFlag'])
            # rows.index = rows['date'].tolist()
            rows.set_index(["date"], inplace=True) # 指定某一列的值作为索引
            self.wordLen_checkFlag_everyday = rows
        except Exception as e:
            print('!Error: 没有该用户的信息')
            raise e
        dbSession.close()
        return rows


    def get_description(self):
        """描述分析结果"""
        descrip = '亲爱的%s(%s)：' % (self.useruname, self.useruid[0:2]+'*'*4+self.useruid[-3:])
        descrip += '\n    你好!\n    %s%s自%s开始，' % (
            Figure.readingInfo['tag'], Figure.readingInfo['term'], 
            min(self.wordLen_checkFlag_everyday.index))
        descrip += '\n在这%s天中，你参与打卡%s天, 共输出%s字。' % (len(self.wordLen_checkFlag_everyday), 
            len(self.wordLen_checkFlag_everyday[self.wordLen_checkFlag_everyday['checkFlag'] == 1]),
            np.sum(self.wordLen_checkFlag_everyday['wordLen']))
        descrip += '\n在打卡排名中位列%s，超过了%.2f%%的小伙伴\\(^o^)/~' % (self.rank[0], self.rank[1]*100)
        descrip += '\n每天输出的文字数量如下图：'
        self.descrip = descrip
        return descrip


    def __repr__(self):
        return "<%s(useruid=%s, useruname=%s, rank=%s, descrip=%s)>" % (
            self.__class__.__name__, self.useruid, self.useruname, self.rank, self.descrip)
                    