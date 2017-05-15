# -*- coding: utf-8 -*-
#! python3

from PortfolioInfo import *
import json, time, os
import gc

MonitorData = [
    {'Symbol': '', 'Time': 0}
]

MonitorDelay = 60 * 60 * 1

def GetLastestTime(Symbol):
    data = GetPortfolioHistories(Symbol)
    Time = data[0]['Date']
    del data
    return Time

# 当检测到调仓变化后调用该函数
def InvokeWhenUpdated(Symbol, Last):
    print('不可思议! 标志为%s的组合居然调仓啦~' % Symbol)
    data = GetPortfolioHistories(Symbol)
    i = 0
    while(True):
        if data[i]['Date'] == Last:
            break
        i = i + 1
    ShowHistories(data[:i])
    # You can add your logic here! data[:i] means delta History!
    # Saving data to history file is best way!
    del data
    return 'Amazing!'

def InvokeWhenAdded(Symbol):
    print('组合 %s 进入监视!' % Symbol)
    # You can add your logic here!

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

def CheckUpdate(Data):
    for item in Data:
        if item['Symbol'] == '':
            continue
        Last = GetLastestTime(item['Symbol'])
        if Last != item['Time']:
            if item['Time'] == 0:
                InvokeWhenAdded(item['Symbol'])
            else:
                InvokeWhenUpdated(item['Symbol'], item['Time'])
            item['Time'] = Last
        gc.collect()

def Monitor():
    global MonitorData
    MonitorData = LoadFromDisk('Monitor.json')
    try:
        while(True):
            try:
                CheckUpdate(MonitorData)
                time.sleep(MonitorDelay)
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except Exception as e:
                print("出现错误: " + e)
            except:
                print("大概不可能会出现的其他错误!!!!")

    except KeyboardInterrupt:
        print("监视终止!")
    finally:
        SaveToDisk('Monitor.json')

if __name__ == '__main__':
    Monitor()