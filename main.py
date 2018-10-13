#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-09-19

import re
import json
import pymysql
import datetime
import pandas as pd

# 打开数据库连接
db = pymysql.connect("localhost","test","123456","test" )
cursor = db.cursor(pymysql.cursors.DictCursor) # 创建游标对象，以字典的形式返回数据


def create_table():
    # 如果表存在则删除
    cursor.execute("DROP TABLE IF EXISTS CHECK_COUNT")
    # 创建表
    sql = """CREATE TABLE CHECK_COUNT (
             IDX INT AUTO_INCREMENT PRIMARY KEY NOT NULL, # 自增主键
             DATE_TIME DATETIME COMMENT "打卡时间",  
             QQNAME CHAR(30) NOT NULL COMMENT "昵称",
             QQ CHAR(15) ,
             CONTENT TEXT COMMENT "打卡内容")"""
    cursor.execute(sql)
    return 0


def pickup_data():
    """
        从input.txt文件中提取每一条发言的日期、时间、昵称、QQ号、内容，写入数据库
    """
    rhand = open('input.txt', encoding="UTF-8")
    txt = rhand.read()
    rhand.close()
    txtLst = re.findall('\S', txt) 
    txt = "".join(txtLst)
    # 以日期时间作为分割符，保留分隔符。两个列表成员组成一个人的发言。
    txtLst = re.split('(20\d{2}-\d{2}-\d{2}\d{2}:\d{2}:\d{2})', txt)
    txtLst = txtLst[1:] 
    print(len(txtLst))

    # 从input.txt文件中读取数据，分类写入数据库
    for i in range(0, len(txtLst), 2): 
        j = i + 1   # i索引发言人的信息，j索引发言内容
        if j > (len(txtLst) - 1):
            break
        # 字符内容分类
        if re.search('^梦梦', txtLst[j]): # 剔除异常数据（梦梦的发言）
            # print(txtLst[j])
            pass
        else: # 对数据进行分类
            templst = list()
            templst.append(re.search('20\d{2}-\d{2}-\d{2}', txtLst[i]).group()) # 日期
            templst.append(re.search('\d{2}:\d{2}:\d{2}', txtLst[i]).group()) # 时间
            templst.append(re.search('.+(?=\((\d{5,12})\))', txtLst[j]).group()) # 昵称
            templst.append(re.search('\(\d{5,12}\)', txtLst[j]).group()) # QQ号
            templst.append(re.sub('.*\(\d{5,12}\)', '', txtLst[j])) # 发言内容
            # 写入数据库
            sql = "INSERT INTO CHECK_COUNT(DATE_TIME, QQNAME, QQ, CONTENT) \
               VALUES ('%s', '%s', '%s', '%s')" % \
               (templst[0]+' '+templst[1], templst[2], templst[3], templst[4])
            try:
               cursor.execute(sql)
               db.commit()
            except:
               db.rollback() # 发生错误时回滚
        ## END if
    ## END for
    return 0



def count_check():
    """
        统计打卡次数
    """
    sql = """SELECT * FROM check_count WHERE
             content LIKE '%#早起读书现学现卖#%' AND CHAR_LENGTH(CONTENT) >= 200
             AND DATE_TIME BETWEEN '2018-06-25 00:00:00' AND '2018-07-02 00:00:00';"""
          # char_length()计算一个汉字为3个字符,一个字母、数字为1个字符
          # char计算一个汉字、字母、数字为1个字符
    try:
        cursor.execute(sql)
        rows = cursor.fetchall() 
    except:
        print ("Error: unable to fetch data")
    print(len(rows))
    dateLst = ['2018-06-25', '2018-06-26', '2018-06-27', '2018-06-28', '2018-06-29', 
    '2018-06-30', '2018-07-01']
    countDi = dict()
    for row in rows:
        QQ = row['QQ']
        if QQ not in countDi:
            # countDi[QQ]的内容：['昵称','2018-06-25','2018-06-26','2018-06-27',
            #  '2018-06-28','2018-06-29','2018-06-30','2018-07-01','字数','频次']
            countDi[QQ] = [0]*10
            countDi[QQ][0] = row['QQNAME'] + QQ[0:3] + '*'*3 + QQ[6:] # 昵称+QQ隐藏
        timestr = row['DATE_TIME'].strftime("%Y-%m-%d") 
        # print(timestr)
        idx = dateLst.index(timestr)
        if countDi[QQ][idx+1] == 0: # 每天仅统计一次打卡
            countDi[QQ][idx+1] = 1 # 打卡
            countDi[QQ][8] += len(row['CONTENT']) # 打卡字数累加
            countDi[QQ][9] += 1  # 打卡次数累加
    ## END for
    print(len(countDi))
    # print(countDi)

    # # 检验key值是否重复
    # print(len(countDi.keys())) 
    # print(len(list(set(countDi.keys()))))

    db.close() # 关闭数据库连接
    return countDi


def write_excel(countDi):
    """
        将统计内容写入EXCEL
    """
    ## 按照频次、字数的优先级进行排序
    whand = pd.ExcelWriter('0625-0701晨读统计.xlsx')
    data = list()
    for k,v in countDi.items():
        data.append(v)
    print(len(data))
    frame = pd.DataFrame(data, 
                columns=['昵称','2018-06-25','2018-06-26','2018-06-27','2018-06-28','2018-06-29','2018-06-30','2018-07-01','字数','频次'], 
                index=range(len(data)))
    frame = frame[frame['频次'] > 0]
    print(len(frame)) 
    frame = frame.sort_values(by=['频次', '字数'], ascending=False) # 按照频次、字数的优先级进行降序排序
    frame.to_excel(whand, sheet_name="打卡统计", na_rep='', float_format=None, columns=None, header=True, 
        index=False, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, encoding=None, 
        inf_rep='inf', verbose=True, freeze_panes=None)
    frame.head(10).to_excel(whand, sheet_name="勤奋名单", na_rep='', float_format=None, columns=None, 
        header=True, index=False, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, 
        encoding=None, inf_rep='inf', verbose=True, freeze_panes=None)
    frame.tail(10).to_excel(whand, sheet_name="高危名单", na_rep='', float_format=None, columns=None, 
        header=True, index=False, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, 
        encoding=None, inf_rep='inf', verbose=True, freeze_panes=None)
    whand.save()

    return 0



def main():
    # create_table()
    # pickup_data()
    data = count_check()
    write_excel(data)

    
if __name__ == '__main__':
    main()




    