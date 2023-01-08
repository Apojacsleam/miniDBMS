import re

import pandas as pd
import Select


def deleteData(username, sql):
    if 'where' not in sql:
        matchObj = re.search(r'^delete from (.*);$', sql)
        if matchObj:
            tableName = matchObj.group(1)
            conditions = ""
        else:
            return (False, 'sql 解析错误')
    else:
        matchObj = re.search(r'delete from (.*) where (.*);$', sql)
        if matchObj:
            tableName = matchObj.group(1)
            conditions = matchObj.group(2)
        else:
            return (False, 'sql 解析错误')
    df = pd.read_pickle(r'./Data/' + tableName + '.data')
    df_columns = df.columns.values.tolist()
    for col in df_columns:
        df.rename(columns={col: tableName + '.' + col}, inplace=True)

    result = pd.DataFrame(columns=df.columns.values.tolist())
    for i in range(len(df)):
        if not Select.infix_evaluator(df.iloc[i, :], conditions):
            result.loc[result.index.size] = df.iloc[i, :]

    for col in df_columns:
        result.rename(columns={tableName + '.' + col: col}, inplace=True)

    result.to_pickle(r'./Data/' + tableName + '.data')
    return (True, "修改成功")