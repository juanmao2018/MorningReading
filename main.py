#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-06

import os
import re
import pymysql
import matplotlib # 注意这个也要import一次
import matplotlib.pyplot as plt
# myfont = matplotlib.font_manager.FontProperties(fname=r'C:/Windows/Fonts/SimHei.ttf') 
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import pandas as pd



class MyDB:
    '''数据库操作类'''
    def __init__(self, host, user, passwd, db):
        self.conn = pymysql.connect(host=host, user=user, passwd=passwd, db=db)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor) # 创建游标对象，以字典的形式返回数据

    def create_table(self):
        '''创建聊天记录表'''
        try:
            sql = """CREATE TABLE IF NOT EXISTS MESSAGE5 (
                     idx INT AUTO_INCREMENT PRIMARY KEY NOT NULL, # 自增主键
                     msgDate DATE COMMENT "打卡日期",
                     msgTime TIME COMMENT "打卡时间", 
                     QQName CHAR(30) NOT NULL COMMENT "昵称",
                     QQ CHAR(15) NOT NULL,
                     note TEXT COMMENT "笔记",
                     idea TEXT COMMENT "感想")
                     ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
            self.cursor.execute(sql)
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback() # 发生错误时回滚
            print("!E: Create table failed")
            print(e)

    def execute_sql(self, sql, params):
        '''执行增、删、改的SQL'''
        effect_row = 0
        try:
            effect_row = self.cursor.execute(sql, params)
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback() # 发生错误时回滚
            print(e)
        return effect_row

    def execute_manysql(self, sql, params):
        '''执行多条增、删、改的SQL'''
        effect_row = 0
        try:
            effect_row = self.cursor.executemany(sql, params)
            self.conn.commit()
        except BaseException as e:
            self.conn.rollback() # 发生错误时回滚
            # print("!E: execute sql failed")
            print(e)
        return effect_row

    def query_sql(self, sql, params):
        '''执行查询SQL'''
        rows = []
        try:
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall() 
        except BaseException as e:
            self.conn.rollback() # 发生错误时回滚
            print(e)
        return rows
        
    def __del__(self):
        '''析构函数'''
        self.conn.close(); # 关闭数据库连接



def pickup_data(fileName):
    """
        从fileName文件中提取每一条发言的时间、昵称、QQ号、笔记，写入数据库
    """
    with open(fileName, encoding="UTF-8") as fhand:
        txt = fhand.read()
    # 以日期时间作为分割符(保留分隔符)得到聊天记录的列表，两个列表成员组成次一次发言的完整信息
    txtLst = re.split('(20\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', txt)
    # print(len(txtLst))
    # 从聊天记录中逐条提取发言的信息
    msgLst = []
    i = 0
    while i < (len(txtLst)-1):  
        try: # 保留正常的聊天数据。异常聊天记录将被剔除，例如没有发言时间、QQ、昵称、内容等
            msg = dict()
            date_time = re.search('^20\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 
                txtLst[i]).group().split(" ",1)
            content = txtLst[i+1].split('\n', 1)
            tempStr = "".join(re.findall('\S', content[0])) # 去掉空格
            msg['QQName'] = re.search('.+(?=\((\d{5,12})\))', tempStr).group()
            msg['QQ'] = re.search('\(\d{5,12}\)', tempStr).group()
            tempStr = content[-1].strip()
            if re.search('#早起读书现学现卖#', tempStr) and (re.search('第5期', tempStr)\
                or re.search('大众传播理论', tempStr) or re.search('传播学教程', tempStr)):
                # print(tempStr)
                msg['msgDate'] = date_time[0]
                msg['msgTime'] = date_time[-1]
                msg['note'] = ''
                msg['idea'] = ''
                # 将笔记和感想分开存储
                if re.search('笔记：', tempStr) and re.search('感想：', tempStr):
                    content = re.split('(笔记：)', tempStr)
                    msg['note'] = content[1]
                    content = re.split('(感想：)', content[-1])
                    msg['note'] += content[0]
                    msg['idea'] = content[-2] + content[-1]
                elif re.search('笔记：', tempStr):
                    content = re.split('(笔记：)', tempStr)
                    msg['note'] = content[1] + content[2]
                elif re.search('感想：', tempStr):
                    content = re.split('(感想：)', tempStr)
                    msg['idea'] = content[1] + content[2]
                if len(msg['note'])>0 or len(msg['idea']) > 0:
                    msgLst.append(msg)
                # print(msg)
            i += 2
        except:
            i += 1  # 如果异常聊天记录，则查找列表中下一个成员
            # print("!E: Not find")
    ## END while
    print(len(msgLst))

    # 将数据写入数据库
    sql = "INSERT INTO MESSAGE5(msgDate, msgTime, QQName, QQ, idea, note) \
               VALUES (%(msgDate)s, %(msgTime)s, %(QQName)s, %(QQ)s, %(idea)s, %(note)s)" 
               # SQL中的格式化字符串，不是Python通常的字符串，所有字段值都用%s插入
    # for msg in msgLst:
    #     mydb.execute_sql(sql, msg)
    print(mydb.execute_manysql(sql, msgLst))
    return 0



class CollectionChcek():
    """总体打卡信息"""
    def __init__(self, description):
        self.description = description
        self.requirs = {
            'daysLimit': "msgDate BETWEEN %(beginStr)s AND %(endStr)s",
            'wordLenLimit': "(char_length(note) + char_length(idea)) >= %(wordLen)s",
        }
        self.daysNum = 0
        self.checkNum = 0
        self.reachCheckNum = 0
        self.noteLens = 0
        self.ideaLens = 0
        self.QQNum = 0
        self.reachQQNum = 0


    def get_days(self, params):
        '''获取打卡的日期列表和天数'''
        sql = """SELECT  distinct(msgDate) FROM message5 WHERE %s;""" % self.requirs['daysLimit']
        rows = mydb.query_sql(sql, params)
        # self.days = [row['msgDate'] for row in rows]
        self.daysNum = len(rows)
        # print(self.days)
        return self.daysNum
        

    def get_num(self, params):
        '''总体打卡信息'''
        # 获取打卡次数
        sql = """SELECT count(*) FROM MESSAGE5 WHERE %s;""" % self.requirs['daysLimit']
        rows = mydb.query_sql(sql, params)
        self.checkNum  = rows[0]['count(*)']
        
        # 获取字数达标的打卡次数#
        sql = """SELECT count(*) FROM MESSAGE5 WHERE %s AND %s;""" % \
            (self.requirs['daysLimit'], self.requirs['wordLenLimit'])
        rows = mydb.query_sql(sql, params)
        self.reachCheckNum = rows[0]['count(*)']

        # 获取打卡字数
        sql = """SELECT sum(char_length(note)) 'noteLens', sum(char_length(idea)) 'ideaLens' 
            FROM message5 WHERE %s;""" % self.requirs['daysLimit']
        rows = mydb.query_sql(sql, params) 
        # print(rows)
        self.noteLens = rows[0]['noteLens']
        self.ideaLens = rows[0]['ideaLens']

        # 获取打卡QQ数量#
        sql = """SELECT count(distinct(QQ)) QQNum FROM message5 
            WHERE %s;""" % self.requirs['daysLimit']
        rows = mydb.query_sql(sql, params)
        self.QQNum = rows[0]['QQNum']

        # 获取有效打卡的QQ数量
        sql = """SELECT count(distinct(QQ)) QQNum FROM message5 WHERE %s AND %s;""" % \
            (self.requirs['daysLimit'], self.requirs['wordLenLimit'])
        rows = mydb.query_sql(sql, params)
        self.reachQQNum = rows[0]['QQNum']

        return 0


    def get_avgs(self):
        '''计算平均值'''
        self.checkNumPerQQ = self.checkNum / self.QQNum
        self.wordLensPerQQ = (self.noteLens + self.ideaLens) / self.QQNum
        self.checkNumPerDay = self.checkNum / self.daysNum
        self.wordLensPerDay =  (self.noteLens + self.ideaLens) / self.daysNum
        return 0


    def get_numsByDay(self, params):
        '''获取按天进行统计的数据'''
        # 统计每天打卡的QQ数量、字数
        sql = """SELECT distinct(msgDate), count(distinct(QQ)) QQNum,
            SUM(char_length(note)) noteLens, SUM(char_length(idea)) ideaLens 
            FROM message5 WHERE %s GROUP BY msgDate;""" % self.requirs['daysLimit'] 
        rows = mydb.query_sql(sql, params)
        # print(len(rows))
        self.lensByDay = [[row['msgDate'].strftime("%Y-%m-%d"), int(row['QQNum']),
            int(row['noteLens']), int(row['ideaLens']), int(row['noteLens'] + row['ideaLens'])] 
            for row in rows]


    def show(self):
        '''CollectionChcek类的展示统计信息'''
        statement = """第五期晨读的主题是“传播学”。在%(daysNum)d天中，参与打卡的人数为%(QQNum)s人，
其中字数达到200字的有%(reachQQNum)s人；共打卡%(checkNum)s次，
其中字数超过200的打卡有%(reachCheckNum)s次。一共输出笔记%(noteLens)s字，感想%(ideaLens)s字。
平均每个人打卡了%(checkNumPerQQ)d次，每人输出内容%(wordLensPerQQ)d字；
平均每天打卡%(checkNumPerDay)d次，每天输出内容%(wordLensPerDay)d字。
每天打卡人数和字数如图一所示。""" % self.__dict__
        # statement = re.findall('\s', statement)
        # statement = "".join(statement)
        # print(statement)
        # print(self.__dict__)
        frame = pd.DataFrame(self.__dict__['lensByDay'], 
                columns=['日期','人数', '笔记字数','感想字数','合计字数'])
        # print(frame['日期'])
        fig = plt.figure()
        ax1 = fig.add_subplot(2,1,1)
        ax1.plot(0,0)
        plt.axis('off')
        ax1.text(0, 0, statement, transform=ax1.transAxes, 
            bbox=dict(facecolor='blue', alpha=0.5))
        ax2 = fig.add_subplot(2,1,2)
        ax2.plot(frame['日期'],frame['笔记字数'],label="笔记字数") 
        ax2.plot(frame['日期'],frame['感想字数'],label="感想字数") 
        ax2.plot(frame['日期'],frame['合计字数'],label="合计字数")
        plt.xticks(frame['日期'], rotation=75)
        ax2.set_xlabel("日期") 
        ax2.set_ylabel("字数") 
        ax2.set_title("打卡字数统计图") 
        plt.legend()  
        plt.tight_layout()
        # plt.show() 
        plt.savefig(self.description + '.png') 



class PersonCheck():
    '''个人打卡信息类'''
    def __init__(self, QQ):
        self.QQ = QQ
        self.requirs = {
            'getNameSQL': """SELECT QQ, QQName FROM message5 
                        WHERE QQ = '%s' order by idx DESC LIMIT 1;""" % QQ,
            'daysLimit': "msgDate BETWEEN %(beginStr)s AND %(endStr)s",
            'QQLimit': "QQ = %(QQ)s",
        }
        rows = mydb.query_sql(self.requirs['getNameSQL'], {})
        self.QQName = rows[0]['QQName']


    def get_numsByDay(self, params):
        '''获取按天统计的打卡信息'''
        # 统计每天打卡的字数，打卡标志位
        sql = """SELECT a.msgDate, 
                    CASE sum(char_length(b.note)) WHEN sum(char_length(b.note)) 
                        THEN sum(char_length(b.note)) ELSE 0 END AS noteLen, 
                    CASE sum(char_length(b.idea)) WHEN sum(char_length(b.idea)) 
                        THEN sum(char_length(b.idea)) ELSE 0 END AS ideaLen, 
                    CASE (sum(char_length(b.note)) + sum(char_length(b.idea))) 
                        WHEN (sum(char_length(b.note)) + sum(char_length(b.idea))) 
                        THEN (sum(char_length(b.note)) + sum(char_length(b.idea))) 
                        ELSE 0 END AS wordLen,
                    CASE b.msgDate WHEN b.msgDate THEN 1 ELSE 0 END AS checkFlag
                FROM 
                    (   SELECT DISTINCT(msgDate) msgDate FROM message5 WHERE %s) AS a
                    LEFT JOIN
                    (   SELECT * FROM message5 WHERE %s) AS b 
                    ON a.msgDate = b.msgDate
                    GROUP BY a.msgDate ORDER BY a.msgDate ASC;""" % \
                    (self.requirs['daysLimit'], self.requirs['QQLimit'])
        rows = mydb.query_sql(sql, params)
        self.noteLen = sum([row['noteLen'] for row in rows])
        self.ideaLen = sum([row['ideaLen'] for row in rows])
        self.daysNum = len(rows)
        self.checkByDay = [[row['msgDate'].strftime("%Y-%m-%d"), int(row['noteLen']), 
            int(row['ideaLen']), int(row['wordLen'])] for row in rows]


    def get_rank(self, params):
        '''获取排名顺序'''
        # 按打卡次数排名。数据相同排名一样且占位（prevRank记录上一次的排名，incrRank记录排序号码），
        # 例如1,2,2,4,……
        sql = """SELECT obj_new.QQ, obj_new.checkNum, obj_new.checkRank
                FROM
                    (SELECT obj.QQ, obj.checkNum,
                            @incrRank := @incrRank + 1 AS incr_rank,
                            @curRank := CASE
                                WHEN @prevRank = obj.checkNum THEN @curRank
                                WHEN @prevRank := obj.checkNum THEN @incrRank
                                END AS checkRank
                    FROM
                        (SELECT QQ, COUNT(DISTINCT(msgDate)) checkNum
                        FROM message5 WHERE %s 
                        GROUP BY QQ ORDER BY checkNum DESC) AS obj,
                        (SELECT @curRank := 0 ,@prevRank := NULL ,@incrRank := 0) r
                    ) AS obj_new 
                WHERE obj_new.%s;""" % (self.requirs['daysLimit'], self.requirs['QQLimit'])
        rows = mydb.query_sql(sql, params)
        self.checkRank = rows[0]['checkRank']
        self.checkNum = rows[0]['checkNum'] # 打卡天数
        # 按字数排名。数据相同排名一样且占位（prevRank记录上一次的排名，incrRank记录排序号码），
        # 例如1,2,2,4,……
        sql = """SELECT obj_new.QQ, obj_new.wordLen, obj_new.lenRank
                FROM
                    (SELECT obj.QQ, obj.wordLen,
                            @incrRank := @incrRank + 1 AS incr_rank,
                            @curRank := CASE
                                WHEN @prevRank = obj.wordLen THEN @curRank
                                WHEN @prevRank := obj.wordLen THEN @incrRank
                                END AS lenRank
                    FROM
                        (SELECT QQ, (sum(char_length(note)) + sum(char_length(idea))) AS wordLen
                        FROM message5 WHERE %s 
                        GROUP BY QQ ORDER BY wordLen DESC) AS obj,
                        (SELECT @curRank := 0 ,@prevRank := NULL ,@incrRank := 0) r
                    ) AS obj_new
                WHERE obj_new.%s;""" % (self.requirs['daysLimit'], self.requirs['QQLimit'])
        rows = mydb.query_sql(sql, params)
        self.lenRank = rows[0]['lenRank']
        self.wordLen = rows[0]['wordLen'] # 打卡字数
        # 字数贡献度
        self.lenPercent = (self.noteLen + self.ideaLen) / (params['noteLens'] + params['ideaLens'])


    def show(self):
        '''展示个人打卡类PersonCheck的信息'''
        statement = """亲爱的%(QQName)s，你参加了第五期传播学的晨读打卡。
在这%(daysNum)s天中，你一共打卡%(checkNum)d次，打卡排名%(checkRank)s。
写了笔记%(noteLen)d字，感想%(ideaLen)d字，共输出%(wordLen)d字的内容，字数排名%(lenRank)s，
本期晨读内容贡献度为%(lenPercent).2f%%。
每天的打卡统计如下图所示。""" % self.__dict__
        # print(statement)
        # print(self.__dict__)
        frame = pd.DataFrame(self.__dict__['checkByDay'], 
                columns=['日期','笔记字数','感想字数','合计字数'])
        # print(frame['日期'])
        fig = plt.figure()
        ax1 = fig.add_subplot(2,1,1)
        ax1.plot(0,0)
        plt.axis('off')
        ax1.text(0, 0, statement, transform=ax1.transAxes, 
            bbox=dict(facecolor='blue', alpha=0.5))
        ax2 = fig.add_subplot(2,1,2)
        ax2.plot(frame['日期'],frame['笔记字数'],label="笔记字数") 
        ax2.plot(frame['日期'],frame['感想字数'],label="感想字数") 
        ax2.plot(frame['日期'],frame['合计字数'],label="合计字数")
        plt.xticks(frame['日期'], rotation=75)
        ax2.set_xlabel("日期") 
        ax2.set_ylabel("字数") 
        ax2.set_title("打卡字数统计图") 
        plt.legend()  
        plt.tight_layout()
        # plt.show() 
        plt.savefig(self.QQ + '.png') 



def collection_statistics(requireDi):
    '''统计总体打卡情况'''
    cllctCheck = CollectionChcek('整体打卡统计')
    cllctCheck.get_days(requireDi)
    cllctCheck.get_num(requireDi)
    cllctCheck.get_avgs()
    cllctCheck.get_numsByDay(requireDi)
    cllctCheck.show()
    # print(cllctCheck.__dict__)
    return cllctCheck



def person_statistics(requireDi, QQ):
    '''个人打卡情况统计。
        如果QQ为空，统计所有QQ号的打卡信息；如果QQ非空，则统计指定QQ号的打卡信息
    '''
    if len(QQ) > 6:
        personCheck = PersonCheck(QQ)
        requireDi['QQ'] = QQ
        personCheck.get_numsByDay(requireDi)
        personCheck.get_rank(requireDi)
        personCheck.show()
        # print(personCheck.__dict__)
    else:
        sql = """SELECT distinct(QQ) FROM message5
                WHERE msgDate BETWEEN %(beginStr)s AND %(endStr)s;"""
        rows = mydb.query_sql(sql, requireDi)
        QQLst = [row['QQ'] for row in rows]
        # print(len(QQLst))
        personCheckLst = list()
        for QQ in QQLst:
            personCheck = PersonCheck(QQ)
            requireDi['QQ'] = QQ
            personCheck.get_numsByDay(requireDi)
            personCheck.get_rank(requireDi)
            personCheck.show()
            # print(personCheck.__dict__)
            personCheckLst.append(personCheck)
        print(len(personCheckLst))



def main():
    rootdir = "week7-8任务\\晨读打卡记录"

    for dirpath, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            # print(os.path.join(rootdir,filename))
            # pickup_data(os.path.join(rootdir,filename)) # 将聊天记录文件导入数据库
            pass

    requireDi = {
        'wordLen': 200,
        'beginStr': "2018-06-07",
        'endStr': "2018-07-09"
    }

    cCheck = collection_statistics(requireDi)
    requireDi['noteLens'] = cCheck.noteLens
    requireDi['ideaLens'] = cCheck.ideaLens
    pCheck = person_statistics(requireDi, '(820307567)')

    return 0


if __name__ == '__main__':
    mydb = MyDB(host = "localhost", user = "test", passwd = "123456", db ="test" )
    # mydb.create_table()
    main()


