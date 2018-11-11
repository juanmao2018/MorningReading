#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-27

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Date, Time, Text, Integer

Base = declarative_base()  # create the base class

class MessageModel(Base):
    """定义映射关系类MessageModel"""
    __tablename__ = 'message' # 表名
    # 字段
    msgidx = Column(Integer, primary_key=True, autoincrement=True) # 消息的索引值
    useruid = Column(String(20), nullable=False) # 用户编号
    useruname = Column(String(50)) # 用户名
    msgdate = Column(Date) # 消息发送日期
    msgtime = Column(Time) # 消息发送时间
    content = Column(Text, nullable=False)
    contentLen = Column(Integer, default=0)
    note = Column(Text) # 笔记
    noteLen = Column(Integer, default=0) # 笔记字数
    thought = Column(Text) # 感想
    thoughtLen = Column(Integer, default=0) # 感想字数


    def __init__(self, useruid, useruname, msgdate, msgtime, content=None, contentLen=0,
        note=None, noteLen=0, thought=None, thoughtLen=0):
        self.useruid = useruid
        self.useruname = useruname
        self.msgdate = msgdate
        self.msgtime = msgtime
        self.content = content
        self.contentLen = contentLen
        self.note = note
        self.noteLen = noteLen
        self.thought = thought
        self.thoughtLen = thoughtLen
        

    def __repr__(self):
        return "<%s(useruid='%s', useruname='%s', msgdate=%s, msgtime='%s', contentLen='%s', noteLen='%s', thoughtLen='%s')>" % (
            self.__class__.__name__, self.useruid, self.useruname, self.msgdate, self.msgtime, 
            self.contentLen, self.noteLen, self.thoughtLen)
   

   