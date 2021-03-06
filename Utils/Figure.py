#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-28

import threading

class Figure(object):
    """记录指标、要求的类"""
    # -- 数据库配置信息
    DBInfo = {
        'HOSTNAME' : 'localhost',
        'PORT' : '3306',
        'DATABASE' : 'test',
        'USERNAME' : 'test',
        'PASSWORD' : '123456'
    }

    readingInfo = {
        'books': ['大众传播理论', '传播学教程'],
        'tag': '#早起读书现学现卖#',
        'term': '第5期',
        'wordLen': 200
    }

    imgInfo = {
        'filetype': '.pdf'
    }

    pathInfo = {
        'inputPath': "inputs\\",
        'outputPath': "outputs\\"
    }

    fileName = '统计结果'

    ThreadInfo = {
        'mutex': threading.Lock(), # 创建线程锁
        'threadMaxnum': threading.Semaphore(8)  # 限制线程的最大数量
    }
