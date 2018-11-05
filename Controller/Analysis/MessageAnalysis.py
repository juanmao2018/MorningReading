#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-30

from sqlalchemy.orm import aliased
from sqlalchemy import text, case, outerjoin, func
import pandas as pd
import numpy as np
import datetime
from decimal import *

from Utils.Figure import Figure
from Model.MessageModel import MessageModel
Message = aliased(MessageModel, name='Message')


class CollectionAnalysis(object):
    """总体分析"""

    def __init__(self, DBCtrl):
        self.DBCtrl = DBCtrl
        self.userList = [] # 用户号和用户名列表
        self.userNum_wordLen_everyday = [] # 每天的打卡的用户数和字数
        self.dayNum_wordLen_rank = [] # 每个用户的打卡天数、字数、排名
        self.descrip = ''


    def query_userList(self):
        """查询参与打卡的用户号和昵称"""
        #   （存在一个用户有多个用户名的情况，用max()和group_by()筛选一个用户名）
        rows = None
        try:
            rows = self.DBCtrl.dbSession.query(Message.useruid, func.max(Message.useruname)).\
                group_by(Message.useruid).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['useruid', 'useruname'])
            self.userList = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
        return rows


    def query_userNum_wordLen_everyday(self):
        """查询每天的打卡人数和字数（一个人一天多次打卡仅统计一次）"""
        rows = None
        try:
            rows = self.DBCtrl.dbSession.query(Message.msgdate, 
                func.count(Message.useruid.distinct()).label('userNum'), 
                func.sum(Message.contentLen).label('wordLen')).group_by(Message.msgdate).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['date', 'checkUserNum', 'wordLen'])
            rows.set_index(["date"], inplace=True) # 指定某一列的值作为索引
            self.userNum_wordLen_everyday = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
        return rows


    def query_dayNum_wordLen_rank(self):
        """查询每个用户的打卡天数、字数，并排名（按照天数、字数降序排列，一天多次打卡算一次）"""
        rows = None
        try:
            stmt = self.DBCtrl.dbSession.query(Message.useruid, func.count(Message.msgdate.\
                distinct()).label('dateNum')).group_by(Message.useruid).subquery()
            stmt2 = self.DBCtrl.dbSession.query(Message.useruid, func.sum(Message.contentLen).\
                label('wordLen')).group_by(Message.useruid).subquery()
            rows = self.DBCtrl.dbSession.query(stmt.c.useruid, stmt.c.dateNum, 
                stmt2.c.wordLen).filter(stmt.c.useruid==stmt2.c.useruid).\
                order_by(stmt.c.dateNum.desc(), stmt2.c.wordLen.desc()).all()
            rows = pd.DataFrame(rows, index=range(1,len(rows)+1), 
                columns=['useruid', 'checkDayNum', 'wordLen'])
            rows.index.names = ['rank']
            self.dayNum_wordLen_rank = rows
        except Exception as e:
            print('!Error: 没有查询到信息')
            raise e
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
        

    def __repr__(self):
        return "<%s(descrip=%s)>" % (self.__class__.__name__, self.descrip)
        
        

class PersonAnalysis(object):
    """个人分析"""
    def __init__(self, DBCtrl, useruid, rank):
      self.DBCtrl = DBCtrl
      self.useruid = useruid
      self.rank = rank
      self.useruname = ''
      self.wordLen_checkFlag_everyday = []
      self.descrip = ''


    def query_name_by_useruid(self):
        """查找指定用户号的用户名"""
        rows = []
        try: # （存在一个用户由多个用户名的情况，用max()和group_by()删选一个）
            rows = self.DBCtrl.dbSession.query(Message.useruid, func.max(Message.useruname)).\
            filter(text("useruid=:useruid")).params(useruid=self.useruid).all()
            self.useruname = rows[0][1]
        except Exception as e:
            print('!Error: 没有该用户的信息')
            raise e
        return rows


    def query_wordLen_checkFlag_everyday(self):
        """查询指定用户号的每天的打卡字数和打卡标志"""
        rows = None
        try:
            stmt = self.DBCtrl.dbSession.query(Message.msgdate.distinct().label('msgdate')).subquery()
            stmt2 = self.DBCtrl.dbSession.query(Message).filter(Message.useruid==self.useruid).subquery()
            caseStmt = case(
                [(func.sum(stmt2.c.contentLen) > 0, func.sum(stmt2.c.contentLen)),], 
                else_ = 0
            ).label('wordLen')
            caseStmt2 = case(
                [(stmt2.c.msgdate, 1),], else_ = 0
            ).label('checkFlag')
            rows = self.DBCtrl.dbSession.query(stmt.c.msgdate, caseStmt, caseStmt2).\
                outerjoin(stmt2, stmt.c.msgdate==stmt2.c.msgdate).group_by(stmt.c.msgdate).\
                order_by(stmt.c.msgdate).all()
            rows = pd.DataFrame(rows, columns=['date', 'wordLen', 'checkFlag'])
            # rows.index = rows['date'].tolist()
            rows.set_index(["date"], inplace=True) # 指定某一列的值作为索引
            self.wordLen_checkFlag_everyday = rows
        except Exception as e:
            print('!Error: 没有该用户的信息')
            raise e
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
                    