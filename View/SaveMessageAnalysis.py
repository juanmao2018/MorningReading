#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-31

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import time
import multiprocessing
# myfont = matplotlib.font_manager.FontProperties(fname=r'C:/Windows/Fonts/SimHei.ttf') 
plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号

from Controller.Analysis.MessageAnalysis import CollectionAnalysis
from Controller.Analysis.MessageAnalysis import PersonAnalysis
from Utils.Figure import Figure


class SaveMessageAnalysis(object):
    """保存SaveMessageAnalysis类的分析结果到文件"""
    def __init__(self, outpath='outputs\\'):
        self.outpath = outpath


    def save_message_analysis(self, ClctAnls, filename='统计结果.xlsx'):
        """将分析结果保存到文件"""
        procsPool = multiprocessing.Pool()
        dataLst = list()
        sheetnams = list()
        prsFileNames = list()

        if isinstance(ClctAnls, CollectionAnalysis):
            dataLst = [
                ClctAnls.userLst, ClctAnls.userNum_wordLen_everyday, 
                ClctAnls.dayNum_wordLen_rank
            ]
            sheetnams = [
                '用户列表', '每日打卡用户数量和字数',
                '用户打卡天数和字数排名'
            ]
            self.draw_collection_analysis(ClctAnls, self.outpath + filename \
                + Figure.imgInfo['filetype']) # 总体分析绘图
        else:
            print("不是总体分析结果！")

        psnAnlsLst = ClctAnls.psnAnlsLst
        for PsnAnls in psnAnlsLst:
            dataLst.append(PsnAnls.wordLen_checkFlag_everyday)
            sheetnams.append(PsnAnls.useruid + '每日打卡情况')
            prsFileNames.append(self.outpath + filename + PsnAnls.useruid \
                + Figure.imgInfo['filetype'])
        temp = zip(psnAnlsLst, prsFileNames)
        list(procsPool.map(self.draw_person_analysis, temp))
        procsPool.close() 
        procsPool.join() 
        SaveMessageAnalysis.save_to_excel(self.outpath+filename+'.xlsx', dataLst, sheetnams) # 存入EXCEL文件
        return 1
        

    def draw_collection_analysis(self, ClctAnls, filename='统计结果'):
        """将总体分析的结果绘图"""
        fig, axes = plt.subplots(2,1)
        ax1, ax2 = axes[0], axes[1]
        data = ClctAnls.userNum_wordLen_everyday
        data['checkUserNum'] = pd.to_numeric(data['checkUserNum'])
        data['wordLen'] = pd.to_numeric(data['wordLen'])

        # -- 绘图：分析结果
        ax1.text(0.0, 0.5, ClctAnls.descrip)
        ax1.axis('off')

        # -- 绘图：每日打卡用户数、打卡字数绘制在一张图中
        # -- 绘图：按照日期统计的打卡用户数
        lns1 =data['checkUserNum'].plot(kind='line', ax=ax2, rot=90, 
            xticks=pd.date_range(start=min(data.index), end=max(data.index), freq='2D'),
            ylim=[0, max(data['checkUserNum'])])
        # -- 绘图：按照日期统计的打卡字数
        ax2_twins = ax2.twinx()  # 双y轴绘制
        lns2 = data['wordLen'].plot(kind='line', ax=ax2_twins, rot=90, color='r',
            xticks=pd.date_range(start=min(data.index), end=max(data.index), freq='2D'),
            ylim=[0, max(data['wordLen'])])
        fig.legend(loc=1, bbox_to_anchor=(1,1), bbox_transform=ax2.transAxes) # 合并图例
        date_format = mpl.dates.DateFormatter("%m/%d")
        ax2.xaxis.set_major_formatter(date_format)
        # plt.show()
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        return 1


    def draw_person_analysis(self, args):
        """将个人分析的结果绘图"""
        PsnAnls, filename = args
        # print("Starting draw_person_analysis() " + PsnAnls.useruid + " " + time.ctime())

        fig, axes = plt.subplots(2,1)
        ax1, ax2 = axes[0], axes[1]
        data = PsnAnls.wordLen_checkFlag_everyday
        data.wordLen = pd.to_numeric(data.wordLen)

        # -- 绘图：分析结果
        ax1.text(0.0, 0.5, PsnAnls.descrip)
        ax1.axis('off')

        # -- 绘图：按照日期统计的打卡字数
        data['wordLen'].plot(kind='line', ax=ax2, rot=90, 
            xticks=pd.date_range(start=min(data.index), end=max(data.index), freq='2D'),
            ylim=[0, max(data['wordLen'])])
        date_format = mpl.dates.DateFormatter("%m/%d")
        ax2.xaxis.set_major_formatter(date_format)
        fig.legend(loc=1, bbox_to_anchor=(1,1), bbox_transform=ax2.transAxes)

        # plt.show()
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        return 1


    @staticmethod
    def save_to_excel(filename='result.xlsx', dataLst=[], sheetnams=[]):
        """数据保存在指定的EXCEL文件中，每个sheet按照要求命名"""
        if len(dataLst) != len(sheetnams):
            print('!Error: 存入EXCEL的列表长度不一致！')
            return 0
        fwriter = pd.ExcelWriter(filename)
        for i in range(len(sheetnams)):
            dataLst[i].to_excel(fwriter, sheetnams[i])
        fwriter.save()
        fwriter.close()
        return 1



