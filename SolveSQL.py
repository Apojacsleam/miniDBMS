import Select, Update, Insert, Delete, CreateTable, DropAndRename
from UserOperation import *
from AddLogging import AddLog


def Solve(sql, username):
    if sql.lstrip().startswith('create table '):
        result = CreateTable.createTable(username, sql)
    elif sql.lstrip().startswith('drop table '):
        result = DropAndRename.drop(username, sql)
    elif sql.lstrip().startswith('rename table '):
        result = DropAndRename.rename(username, sql)
    elif sql.lstrip().startswith('select '):
        result = Select.selectData(username, sql)
    elif sql.lstrip().startswith('update '):
        result = Update.updateData(username, sql)
    elif sql.lstrip().startswith('delete from'):
        result = Delete.deleteData(username, sql)
    elif sql.lstrip().startswith('insert into '):
        result = Insert.insertData(username, sql)
    elif sql.lstrip().startswith('create user '):
        result = CreateUser(sql)
    elif sql.lstrip().startswith('grant '):
        result = GrantUser(sql, username)
    elif sql.lstrip().startswith('revoke '):
        result = RevokeGrant(sql, username)
    elif sql.lstrip().startswith('help table '):
        result = HelpTable(sql)
    else:
        result = (False, 'SQL语言错误！无法解析SQL语言！')
    AddLog(username, result, sql)
    return result
