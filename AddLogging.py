import time


def AddLog(user, result, sql):
    Time = '[Time]\t\t\t' + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    with open('Loggings/SystemLogging.log', 'a', encoding='UTF-8') as f:
        f.write(Time + '\n')
        f.write('[User]\t\t\t' + user + '\n')
        f.write('[Operation]\t\t' + sql + '\n')
        if result[0]:
            if sql.lstrip().startswith('help table ') or sql.lstrip().startswith('select '):
                f.write('[Result]\t\tSuccessful operation.\n\n')
            else:
                f.write('[Result]\t\tSuccessful operation.' + result[1] + '\n\n')
        else:
            f.write('[Result]\t\tOperation failure.' + result[1] + '\n\n')
