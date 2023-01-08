import re

import pandas as pd
import Select


def updateData(username, sql):
    if 'where' in sql:
        matchObj = re.search(r'^update (.*) set (.*) where (.*);$', sql)
        if matchObj:
            tableName = matchObj.group(1)
            values = matchObj.group(2)
            values = values.split(',')
            for value in values:
                value = value.lstrip().rstrip()
            conditions = matchObj.group(3)
        else:
            return (False, 'sql 解析错误')
    else:
        matchObj = re.search(r'^update (.*) set (.*);$', sql)
        if matchObj:
            tableName = matchObj.group(1)
            values = matchObj.group(2)
            values = values.split(',')
            for value in values:
                value = value.lstrip().rstrip()
            conditions = ""
        else:
            return (False, 'sql 解析错误')

    df = pd.read_pickle(r'./Data/' + tableName + '.data')
    df_columns = df.columns.values.tolist()
    for i in range(len(values)):
        if values[i].split('=')[0] in df_columns:
            values[i] = tableName + '.' + values[i]
    for col in df_columns:
        df.rename(columns={col: tableName + '.' + col}, inplace=True)
    for i in range(len(df)):
        if Select.infix_evaluator(df.iloc[i, :], conditions):
            for value in values:
                col = value.split('=')[0]
                val = value.split('=')[1]
                if (val.startswith('"') or val.startswith("'")):
                    df.loc[i, col] = str(val[1:-1])
                else:
                    df.loc[i, col] = float(val)
    for col in df_columns:
        df.rename(columns={tableName + '.' + col: col}, inplace=True)
    df.to_pickle(r'./Data/' + tableName + '.data')
    return (True, "修改成功")
