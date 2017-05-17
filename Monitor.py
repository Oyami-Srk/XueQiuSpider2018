# -*- coding: utf-8 -*-
#! python3

from PortfolioInfo import *
import json, time, os
import gc

# MonitorData = [
#     {'Symbol': '', 'Time': 0}
# ]

# MonitorDelay = 60 * 60 * 1
MonitorDelay = 5 * 60 * 1
RestDelay = 1 * 60

def GetLastestTime(Symbol):
    data = GetPortfolioHistories(Symbol)
    Time = data[0]['Date']
    # del data
    return Time, data

# 当检测到调仓变化后调用该函数
def InvokeWhenUpdated(Symbol, Last, data):
    print('注意！组合 %s 调仓了！' % Symbol)
    # data = GetPortfolioHistories(Symbol)
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
    print('组合 %s 开始监控！' % Symbol)
    # You can add your logic here!

def LoadFromDisk(Filename):
    if os.path.exists(Filename) == False:
        raise FileNotFoundError('Oops! 组合 %s 不存在' % Filename)
    fp = open(Filename)
    # data = []
    try:
        data = json.load(fp)
    except:
        raise Exception('无法读取json文件！')
    finally:
        fp.close()
    return data

def SaveToDisk(Filename):
    global MonitorData
    fp = open(Filename, 'w')
    try:
        json.dump(MonitorData, fp)
    except:
        raise Exception('无法保存json文件！')
    finally:
        fp.close()

def CheckUpdate(Data):
    for item in Data:
        if item['Symbol'] == '':
            continue
        Last, data = GetLastestTime(item['Symbol'])
        if Last != item['Time']:
            if item['Time'] == 0:
                InvokeWhenAdded(item['Symbol'])
            else:
                InvokeWhenUpdated(item['Symbol'], item['Time'], data)
            item['Time'] = Last
        gc.collect()

def Monitor():
    global MonitorData
    MonitorData = LoadFromDisk('Monitor.json')
    try:
        while(True):
            now = time.strftime('%H:%M', time.localtime())
            if ('09:30' <= now <= '11:30') or ('13:00' <= now <= '15:00'):
                try:
                    CheckUpdate(MonitorData)
                    time.sleep(MonitorDelay)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt()
                except Exception as e:
                    print('出现错误：' + str(e))
                    # print('出现错误：' + e.message)
                    time.sleep(RestDelay)
                except:
                    print('大概不会出现的其他错误！！！')
                    time.sleep(RestDelay)
            else:
                print('尚未到交易时间')
                time.sleep(RestDelay)
                continue
                # break

    except KeyboardInterrupt:
        print('监控终止！')
    finally:
        SaveToDisk('Monitor.json')

if __name__ == '__main__':
    Monitor()