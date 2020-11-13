from semantic import Pro
import os

def find_value(name):
    value = 0
    if name in p.temp_list:
        for i, t in enumerate(p.temp_list):
            if t.name == str(name):
                value = t.value
    elif name in p.chart:
        value = p.chart[name]
    else:
        value = int(name)
    return value


def _op(op, P1, P2):
    p1 = find_value(P1)
    p2 = find_value(P2)

    if op == '+':
        return p1 + p2
    elif op == '-':
        return p1 - p2
    elif op == '*':
        return p1 * p2
    elif op == '/':
        return p1 // p2
    elif op == '>':
        if p1 > p2:
            return 1
        return 0
    elif op == '<':
        if p1 < p2:
            return 1
        return 0
    elif op == '==':
        if p1 == p2:
            return 1
        return 0
    elif op == '>=':
        if p1 >= p2:
            return 1
        return 0
    elif op == '<=':
        if p1 <= p2:
            return 1
        return 0
    elif op == '!=':
        if p1 != p2:
            return 1
        return 0
    elif op == '&&':
        if p1 == 1 and p2 == 1:
            return 1
        return 0
    elif op == '||':
        if p1 == 0 and p2 == 0:
            return 0
        return 1    


def VM(chart,newT,sequence,seq_index):

    if os.path.exists('Result.txt'):
        os.remove('Result.txt')



    global p
    p = Pro()
    p.chart = chart  # 符号表  类型：dict
    p.temp_list = newT  # 临时变量表  类型：NewT
    p.seq_list = sequence  # 四元式表  类型：Sequence
    p.seq_index=seq_index #主函数四元式开始的位置
    # 测试使用，将符号表与临时变量表的value置为0
    for i in p.chart.keys():
        p.chart[i] = 0
    for i in range(p.temp_list.__len__()):
        p.temp_list[i].value = 0

    print('-------------------------------------')
    #index = 3
    #print(seq_index)
    index=int(p.seq_index)
    while index < len(p.seq_list):
        item = p.seq_list[int(index)]
        if item.action == '=':
            index += 1
            if item.p1 in p.temp_list:
                for i, t in enumerate(p.temp_list):
                    if t.name == str(item.p1):
                        p.chart[item.result] = p.temp_list[i].value
            else:
                p.chart[item.result] = item.p1
        elif item.action == 'j=':
            flag = find_value(item.p2)
            if flag == item.p1:
                index = item.result.value
            else:
                index += 1
        elif item.action == 'j':
            index = item.result.value
        elif item.action == 'out':
            index += 1
            t = find_value(item.p1)
            with open('Result.txt', 'a+') as f:
                print('输出：', t)
                f.write('{:2}\n'.format(t))
        elif item.action == 'in':
            index += 1
            if item.p1 in p.chart:
                t = eval(input('输入：'))
                p.chart[item.p1] = t
            else:
                print("变量未定义")
        else:
            index += 1
            if item.result in p.chart:
                p.chart[item.result] = _op(item.action, item.p1, item.p2)
            elif item.result in p.temp_list:
                for i,t in enumerate(p.temp_list):
                    if t.name == str(item.result):
                        p.temp_list[i].value = _op(item.action, item.p1, item.p2)

    # print('将抽象机结果赋给了符号表与临时变量表')
    print(p.chart)
    print(p.temp_list)
    #对符号表进行管理，重新赋值
    if os.path.exists('Parameters.txt'):
        os.remove('Parameters.txt')
    with open('Parameters.txt','a+') as f:
        for i in p.chart.keys():
            f.write('name:{:2}  value:{}\n'.format(i,p.chart.get(i)))
        for i in p.temp_list:
            f.write('name:{:2}  value:{}\n'.format(i.name,i.value))

if __name__ == '__main__':
    VM()