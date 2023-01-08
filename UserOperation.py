import hashlib
import re
import os
import pandas as pd
import csv


def GetUserData():
    Data = pd.read_pickle('./Data/userdata.user')
    return Data


def SaveUserData(Data):
    Data.to_pickle('./Data/userdata.user')


def GetGrant():
    Data = pd.read_pickle('./Data/grantdata.user')
    return Data


def SaveGrantData(Data):
    Data.to_pickle('./Data/grantdata.user')


def login(username, password):
    UserData = GetUserData()
    if username in list(UserData['UserName']):
        passcode = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
        code = UserData[UserData['UserName'] == username]['Password'].values[0]
        if code == passcode:
            return (True, '登录成功！')
        else:
            return (False, '登录失败！密码错误！')
    else:
        return (False, '登录失败！没有该用户！')


def CreateUser(sql):
    matObj = re.search('^create user (.*) with password (.*);$', sql)
    if matObj:
        username = matObj.group(1)
        password = matObj.group(2)
        UserData = GetUserData()
        if username in list(UserData['UserName']):
            return (False, '用户已存在！')
        else:
            UserData.loc[len(UserData.index)] = [username, hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()]
            SaveUserData(UserData)
            return (True, '成功添加用户！')
    else:
        return (False, '操作失败！SQL语句不正确！')


def tableGrant(tableName, username):
    with open('Data/grants.txt', 'r') as f:
        for line in f.readlines():
            if line.strip().split('#')[0] == username:
                if line.strip().split('#')[1] == '*' or tableName == line.strip().split('#')[1]:
                    return True
    return False


def hasGrant(username, grant):
    with open('Data/grants.txt', 'r') as f:
        for line in f.readlines():
            if grant in line.split('#')[2]:
                return True
    return False


def RevokeGrant(sql, username):
    matchObj = re.match(r'^revoke (.*) on (.*) from (.*);$', sql)
    if matchObj:
        grants = matchObj.group(1).split(',')
        tableNames = matchObj.group(2)
        user = matchObj.group(3)
        UserData = GetUserData()
        if username not in list(UserData['UserName']):
            return (False, '用户不存在')
        if username == user:
            return (False, '无法收回自己的权限')
        else:
            tableName = tableNames.split(',')
            for table in tableName:
                if not tableGrant(table, username):
                    return (False, '本用户没有操作' + table + '的权限，无法收回')
            grants = [grant.strip() for grant in grants]
            for grant in grants:
                if not hasGrant(user, grant):
                    return (False, '该用户没有该项权限')
            try:
                with open('Data/grants.txt', 'r') as f:
                    lines = f.readlines()
                new_lines = list()
                for line in lines:
                    if line.split('#')[0] == user and line.split('#')[1] in tableName:
                        old_grant = line.split('#')[2].split(',')
                        old_grant = [grant.replace('\n', '') for grant in old_grant]
                        new_grant = [grant for grant in old_grant if grant not in grants]
                        new_lines.append(user + '#' + line.split('#')[1] + '#' + ','.join(new_grant) + '\n')
                    else:
                        new_lines.append(line)
                with open('Data/grants.txt', 'w') as f:
                    for line in new_lines:
                        f.write(line)
                return (True, '修改权限成功')
            except Exception as e:
                return (False, '错误！原因：' + e)

    else:
        return (False, 'SQL 解析失败')


def GrantUser(sql, username):
    matchObj = re.match(r'^grant (.*) on (.*) to (.*);$', sql)
    if matchObj:
        grants = matchObj.group(1).split(',')
        tableName = matchObj.group(2)
        user = matchObj.group(3)
        UserData = GetUserData()
        if username not in list(UserData['UserName']):
            return (False, '用户不存在')
        if user.strip() == username:
            return (False, '无法授予本用户权限')
        else:
            new_grants = list()
            tableNames = tableName.split(',')
            for table in tableNames:
                if not tableGrant(table, username):
                    return (False, '本用户没有操作' + table + '的权限')
            grants = [grant.strip() for grant in grants]
            for grant in grants:
                if hasGrant(username, grant):
                    new_grants.append(grant)
                else:
                    return (False, '本用户没有该项权限')
            try:
                for tableName in tableNames:
                    with open('Data/grants.txt', 'a') as f:
                        f.write('\n' + user + '#' + tableName + '#' + ','.join(new_grants))
                    return (True, '用户权限授予成功')
            except Exception as e:
                return (False, '错误！原因：' + e)
    else:
        return (False, '用户授予权限失败')


def HelpTable(sql):
    matchObj = re.search(r'^help table (.*);$', sql)
    if matchObj:
        tableName = matchObj.group(1)
        if os.path.exists(r'./Data/' + tableName + '.type'):
            Data = pd.read_pickle(r'./Data/' + tableName + '.type')
            return (True, Data)
        else:
            return (False, '数据表不存在')
    else:
        return (False, 'SQL语句解析失败')
