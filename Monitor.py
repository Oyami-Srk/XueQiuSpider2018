# -*- coding: utf-8 -*-
#! python3

from PortfolioInfo import *
import re, json, time, os
import numpy as np

MonitorData = [
    {'Symbol': '', 'Time': 0}
]

def GetLastestTime(Symbol):
    data = GetPortfolioHistories(Symbol)
    Time = data[0]['Date']
    del data
    return Time

# 当检测到调仓变化后调用该函数
def InvokeWhenUpdate(Symbol, Last):
    print('不可思议! 标志为%s的组合居然调仓啦~' % Symbol)
    data = GetPortfolioHistories(Symbol)
    i = 0
    while(True):
        if data[i]['Date'] == Last:
            break
        i = i + 1
    ShowHistories(data[:i])
    del data
    # You can add your logic here! data[:i] means delta History!
    return 'Amazing!'

def LoadFromDisk(Filename):
    if os.path.exists(Filename) == False:
        raise FileNotFoundError("诶, %s不存在的说~" % Filename)
    fp = open(Filename)
    data = []
    try:
        data = json.load(fp)
    except:
        raise Exception("不能读取json文件!")
    finally:
        fp.close()
    return data

def SaveToDisk(Filename):
    global MonitorData
    fp = open(Filename, 'w')
    try:
        json.dump(MonitorData, fp)
    except:
        raise Exception("不能保存json文件!")
    finally:
        fp.close()




if __name__ == '__main__':
    GetLastestTime('ZH888882')