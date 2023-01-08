import pandas as pd
import re, os


def drop(username, sql):
    matchObj = re.search(r'^drop table (.*);$', sql, re.I)
    if matchObj:
        tableName = matchObj.group(1)
        if os.path.exists(r'./Data/' + tableName + '.type'):
            try:
                os.remove(r'./Data/' + tableName + '.type')
                os.remove(r'./Data/' + tableName + '.data')
                # 删除权限to be done
                return (True, '成功删除表格：' + tableName)
            except Exception as e:
                return (False, '操作未成功，原因：' + e)
        else:
            return (False, '表格：' + tableName + '不存在')
    else:
        return (False, 'SQL语句格式错误：DROP TABLE')


def rename(username, sql):
    matchObj = re.search(r'^rename table (.*) as (.*);$', sql, re.I)  # sql server 是以存储过程实现重命名表，这里不管了
    if matchObj:
        tableName_pre = matchObj.group(1)
        tableName_now = matchObj.group(2)
        if os.path.exists(r'./Data/' + tableName_pre + '.type'):
            try:
                type = pd.read_pickle(r'./Data/' + tableName_pre + '.type')
                type.to_pickle(r'./Data/' + tableName_now + '.type')
                os.remove(r'./Data/' + tableName_pre + '.type')
                type = pd.read_pickle(r'./Data/' + tableName_pre + '.data')
                type.to_pickle(r'./Data/' + tableName_now + '.data')
                os.remove(r'./Data/' + tableName_pre + '.data')
                # 修改权限
                with open('Data/grants.txt', 'r') as f:
                    lines = f.readlines()
                new_lines = list()
                for line in lines:
                    if line.split('#')[1] in tableName_pre:
                        new_lines.append(line.split('#')[0] + '#' + tableName_now + '#' + line.split('#')[2] + '\n')
                    else:
                        new_lines.append(line)
                with open('Data/grants.txt', 'w') as f:
                    for line in new_lines:
                        f.write(line)
                return (True, '成功重命名 表' + tableName_pre + '为' + tableName_now)
            except Exception as e:
                return (False, '操作未成功，原因：' + e)
        else:
            return (False, '表格：' + tableName_pre + '不存在')
    else:
        return (False, 'SQL语句格式错误：RENAME TABLE')
