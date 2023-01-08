import re
import os
import pandas as pd
import Check


def writeData(tableName, tableKeys, values, keyType):
    temp = dict()
    for i, j in zip(tableKeys, values):
        temp[i] = j
    try:
        Data = pd.read_pickle('./Data/' + tableName + '.data')
        all_tableKeys = Data.columns
        data_tmp = pd.DataFrame()
        for item in all_tableKeys:
            isPrimary = []
            for row in keyType.itertuples():
                if getattr(row, 'isPrimary') == True:
                    isPrimary.append(getattr(row, 'key'))
            if isPrimary is not None:
                if item in temp:
                    hasRepeat = False
                    Pkeys = []
                    for Pkey in isPrimary:
                        Pkeys.append(temp[Pkey])
                    if Pkeys in Data[isPrimary].values.tolist():
                        hasRepeat = True
                    if hasRepeat == True:
                        return (False, item + ' HAS REPEATED')
                    else:
                        if item in temp:
                            data_tmp[item] = [temp[item]]
                        else:
                            data_tmp[item] = None
                else:
                    return (False, 'PRIMARY KEY IS NOT NULL')
            else:
                if item in temp:
                    data_tmp[item] = [temp[item]]
                else:
                    data_tmp[item] = None
        Data = pd.concat([Data, data_tmp])
        Data.reset_index(drop=True, inplace=True)  # 重新排序index
        Data.to_pickle('./Data/' + tableName + '.data')
        return (True, '成功插入表格，共' + str(Data.shape[0]) + '项')
    except Exception as e:
        return (False, '操作未成功，原因：' + e)


def insertData(username, sql):
    matchObj = re.search(r'^insert into (.*) (\(.*\)) values (.*);$', sql, re.I)
    if matchObj:
        tableName = matchObj.group(1)
        if not Check.checkGrant(username, tableName, 'insert'):  # 判断权限
            return (False, '权限不足')
        if os.path.exists(r'./Data/' + tableName + '.type'):  # 判断是否存在该表
            tableKeys = (matchObj.group(2)[1:-1]).split(',')
            values = (matchObj.group(3)[1:-1]).split(',')
            for i in range(len(values)):  # 去除引号
                values[i] = values[i].lstrip().rstrip()
                try:
                    values[i]=int(values[i])
                except:
                    pass
            keyType = pd.read_pickle('./Data/' + tableName + '.type')

            not_null_key = []  # 获取不可空元素列表
            for row in keyType.itertuples():
                if getattr(row, 'isNull') == False:
                    not_null_key.append(getattr(row, 'key'))
            if not_null_key is not None:
                for items in not_null_key:
                    if items not in tableKeys:
                        return (False, ''.join(items) + ' IS NOT NULL')
            print(values)
            return writeData(tableName, tableKeys, values, keyType)  # 写入
        else:
            return (False, '不存在' + tableName + '表')
    else:
        return (False, 'SQL语句格式错误：INSERT')
