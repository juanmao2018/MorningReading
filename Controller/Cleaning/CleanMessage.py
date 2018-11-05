#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-28

import re

from Utils.Figure import Figure
from Model.MessageModel import MessageModel



class CleanMessage():
    """获取每条聊天记录的中的内容并将其分类"""
    def __init__(self, record):
        # 以日期时间、昵称、QQ作为分割符(保留分隔符)得到聊天记录的列表，两个成员组成次一次发言的完整信息
        self.recordList = re.split('(20\d{2}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s+[^\n]*)', record)[1:]
        self.MsgLst = []


    def clean_message(self):
        """检查聊天记录是否符合要求，并获取合格的聊天记录的详细信息"""
        i = 0
        while(i < len(self.recordList)):
            title = self.recordList[i]
            content = self.recordList[i+1]
            # -- 校验消息内容是否符合打卡要求
            if self.verify_message(content) == 1:  # 校验合格，获取记录的详细信息
                Msg = self.pack_message(title, content)
                if (Msg.useruid != '0000') and (Msg.contentLen > 0):
                    self.MsgLst.append(Msg)
            i += 2
        # -- End While
        return self.MsgLst


    def verify_message(self, content):
        """检查聊天记录是否符合打卡要求。
           返回值：1-合格，0-不合格"""
        if len(content) < Figure.readingInfo['wordLen']:
            return 0
        findBookFlag = 0 # 书有多本，使用特定的标志位帮助检查书名：1-找到书名，0-未找到书名
        for book in Figure.readingInfo['books']:
            if re.search(book, content):
                findBookFlag = 1
        if findBookFlag == 0:
            return 0
        if not re.search(Figure.readingInfo['tag'], content):
            return 0
        if not re.search(Figure.readingInfo['term'], content):
            return 0
        return 1


    def pack_message(self, title, content):
        """获取一条记录的用户信息、内容信息"""
        # -- 类实现 Msg
        Msg = MessageModel('0000', '****', '0000-00-00', '00:00:00', '', 0, '', 0, '', 0) 
        try: # -- 保留正常的聊天数据。异常聊天记录将被剔除，例如没有发言时间、QQ、昵称、内容等
            tempstr = re.split('(20\d{2}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2})', title)
            Msg.msgdate = tempstr[-2].split(" ")[0]
            Msg.msgtime = tempstr[-2].split(" ")[1]
            Msg.useruid = re.findall('\d{5,12}', tempstr[-1])[0]
            tempstr = re.split('\(\d{5,12}\)', tempstr[-1])
            Msg.useruname = tempstr[-2].strip()
            Msg.content = content.strip()
            Msg.contentLen = len(Msg.content)
            # -- 将笔记和感想分开
            if re.search('笔记：', content) and re.search('感想：', content):
                tempstr = re.split('(笔记：)', content)
                Msg.note = tempstr[1]
                tempstr = re.split('(感想：)', tempstr[-1])
                Msg.note += tempstr[0]
                Msg.thought = tempstr[-2] + tempstr[-1]
            elif re.search('笔记：', content):
                tempstr = re.split('(笔记：)', tempstr)
                Msg.note = tempstr[1] + tempstr[2]
            elif re.search('感想：', content):
                tempstr = re.split('(感想：)', tempstr)
                Msg.thought = tempstr[1] + tempstr[2]
            Msg.note = Msg.note.strip()
            Msg.thought = Msg.thought.strip()
            Msg.noteLen = len(Msg.note)
            Msg.thoughtLen = len(Msg.thought)
        except:
            # print("!Error: 获取详细消息信息异常")
            pass
        return Msg 

    