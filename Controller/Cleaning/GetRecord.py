#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 2018-10-28

import os


class GetRecord():
    """获取文件中的内容"""

    @staticmethod
    def get_record(filesDir):
        """获取文件夹中文件的文件内容，每个文件内容以str存入List，返回List"""
        record = []
        for dirpath, dirnames, filenames in os.walk(filesDir):
            for filename in filenames:
                # print(os.path.join(filesDir,filename))
                with open(os.path.join(filesDir,filename), encoding="UTF-8") as fhand:
                    record.append(fhand.read())
        return record

