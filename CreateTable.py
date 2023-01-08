import os
import re
import pandas as pd


def createTable(username, sql):
    matchObj = re.search(r'^create table (.*) \(.*\);$', sql, re.I)
    if matchObj:
        tableName = matchObj.group(1)
        index = sql.find('(')
        tableKeys = sql[index + 1:-2]
        tableKeys = tableKeys.split(',')
        if not os.path.exists(r'./Data/' + tableName + '.type'):
            try:
                key, keytype, isPrimary, isNull, Primarykey = [], [], [], [], []
                for item in tableKeys:
                    if len(item.split(' ')) > 2:
                        item = ' '.join(item.split(' '))
                        splitlist = []
                        for x in item.split(' '):
                            if x != '':
                                splitlist.append(x)
                        key.append(splitlist[0])
                        keytype.append(splitlist[1])
                        if 'NOT NULL' in item:
                            isPrimary.append(True)
                            Primarykey.append(splitlist[0])
                        else:
                            isPrimary.append(False)
                        isNull.append(('NOT NULL' not in item))
                TypeData = pd.DataFrame({'key': key, 'type': keytype, 'isPrimary': isPrimary, 'isNull': isNull})
                TypeData.to_pickle(r'./Data/' + tableName + '.type')
                Data = pd.DataFrame()
                Data = Data.reindex(columns=key, fill_value=True)
                Data.to_pickle(r'./Data/' + tableName + '.data')
                return (True, '成功创建表格：' + tableName)
            except Exception as e:
                return (False, '操作未成功，原因：' + str(e))
        else:
            return (False, '表格：' + tableName + '已经存在')
    else:
        return (False, 'SQL语句格式错误：CREATE TABLE')
