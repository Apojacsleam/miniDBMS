import re
import pandas as pd

import UserOperation


def get_value(operator: str, op1, op2):
    '''
    :参数 operator:运算符
    :参数 op1:左边的操作数
    :参数 op2:右边的操作数
    '''
    if operator == '+':
        return op1 + op2
    elif operator == '-':
        return op1 - op2
    elif operator == '*':
        return op1 * op2
    elif operator == '/':
        return op1 / op2
    elif operator == '<':
        return op1 < op2
    elif operator == '_leq':
        return op1 <= op2
    elif operator == '>':
        return op1 > op2
    elif operator == '_geq':
        return op1 >= op2
    elif operator == '=':
        return op1 == op2
    elif operator == '_neq':
        return op1 != op2
    elif operator == 'AND' or operator == 'and':
        return op1 and op2
    elif operator == 'OR' or operator == 'or':
        return op1 or op2


def infix_evaluator(df, infix_expression: str):
    '''这是中缀表达式求值的函数
    :参数 df: Series, Dataframe中的一行, 即需要判断的对象
    :参数 infix_expression: 中缀表达式
    '''
    df = pd.DataFrame([df.to_dict()])
    if infix_expression == "":
        return True

    replace_dict = {'>=': '_geq', '<=': '_leq', '!=': '_neq', '<>': '_neq',}
    for rep in replace_dict.items():
        infix_expression = infix_expression.replace(rep[0], rep[1])

    # 运算符优先级字典
    pre_dict = {'*': 7, '/': 7, '+': 6, '-': 6, '<': 5, '>': 5, '_geq': 5, '_leq': 5, '=': 4, '_neq': 4, 'AND': 3,
                'and': 3, 'OR': 2, 'or': 2, '(': 1, ')': 1}
    for operator in pre_dict.keys():
        if (operator == 'and' or operator == 'AND' or operator == 'OR' or operator == 'or') : continue
        infix_expression = infix_expression.split(operator)
        infix_expression = (' ' + operator + ' ').join(infix_expression)
    token_list = infix_expression.split()
    # print(token_list)
    # 运算符栈
    operator_stack = []
    # 操作数栈
    operand_stack = []
    for token in token_list:
        # 数字进操作数栈
        if token.isdecimal() or token[1:].isdecimal():
            operand_stack.append(int(token))
        # 左括号进运算符栈
        elif token == '(':
            operator_stack.append(token)
        # 碰到右括号，就要把栈顶的左括号上面的运算符都弹出求值
        elif token == ')':
            top = operator_stack.pop()
            while top != '(':
                op2 = operand_stack.pop()
                op1 = operand_stack.pop()
                # 求出的值要压回操作数栈
                operand_stack.append(get_value(top, op1, op2))
                top = operator_stack.pop()
        # 碰到运算符，就要把栈顶优先级不低于它的都弹出求值
        elif token in pre_dict.keys():
            while operator_stack and pre_dict[operator_stack[-1]] >= pre_dict[token]:
                top = operator_stack.pop()
                op2 = operand_stack.pop()
                op1 = operand_stack.pop()
                operand_stack.append(get_value(top, op1, op2))
            operator_stack.append(token)
        # 字符串常量
        elif token.startswith("\'") or token.startswith('\"'):
            operand_stack.append(str(token[1:-1]))
        # 只能是某个表的列名，查询取值 student.id
        else:
            if '.' not in token:
                for col in df.columns.values.tolist():
                    if str(col).split('.')[1] == token:
                        token = col
                        break
            operand_stack.append(str(df.loc[0, token]))

    # 表达式遍历完成后，栈里剩下的操作符也都要求值   
    while operator_stack:
        top = operator_stack.pop()
        op2 = operand_stack.pop()
        op1 = operand_stack.pop()
        operand_stack.append(get_value(top, op1, op2))
    # 最后栈里只剩下一个数字，这个数字就是整个表达式最终的结果
    return operand_stack[0]


def selectData(username, sql):
    if 'where' not in sql:
        matchObj = re.search(r'^select (.*) from (.*);$', sql)
        if matchObj:
            tableNames = matchObj.group(2).split(',')
            tableNames = [tableName.lstrip().rstrip() for tableName in tableNames]
            #        for tableName in tableNames:
            #            if not UserOperation.hasGrant(username, tableName, 'select'):
            #                print('权限不足')
            #                return
            values = matchObj.group(1).split(',')
            values = [value.lstrip().rstrip() for value in values]
            print(values)
            conditions = ""
        else:
            return (False, 'SQL 解析错误')
    else:
        matchObj = re.match(r'^select (.*) from (.*) where (.*);$', sql)
        if matchObj:
            tableNames = matchObj.group(2).split(',')
            tableNames = [tableName.lstrip().rstrip() for tableName in tableNames]
            #        for tableName in tableNames:
            #            if not UserOperation.hasGrant(username, tableName, 'select'):
            #                print('权限不足')
            #                return
            values = matchObj.group(1).split(',')
            values = [value.lstrip().rstrip() for value in values]
            conditions = matchObj.group(3)
            conditions.lstrip().rstrip(';')
        else:
            return (False, 'SQL 解析错误')

    df = pd.DataFrame()
    for tableName in tableNames:
        newdf = pd.read_pickle(r'./Data/' + tableName + '.data')
        newdf_columns = newdf.columns.values.tolist()
        for i in range(len(values)):
            if values[i] in newdf_columns:
                values[i] = tableName + '.' + values[i]
        for col in newdf_columns:
            newdf.rename(columns={col: tableName + '.' + col}, inplace=True)
        if df.empty:
            df = newdf
        else:
            df = pd.merge(df, newdf, how="cross")

    result = pd.DataFrame(columns=df.columns.values.tolist())
    for i in range(len(df)):
        if infix_evaluator(df.iloc[i, :], conditions):
            result.loc[result.index.size] = df.iloc[i, :]

    if values[0] == '*':
        return (True, result)
    else:
        return (True, result[values])