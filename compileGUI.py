from tkinter import *
import tkinter.filedialog
from lexical import Lexical
from syntax import Parser
from semantic2 import Pro
from vm import VM
import os
import re


global file_name
global content
p = Pro()

def lexical_analysis():
    global content
    # 新建词法分析器
    lexical = Lexical()
    # 载入源代码
    # lexical.load_source(open('code.txt', encoding="utf-8").read())
    lexical.load_source(content)
    # 执行词法分析
    lexical_success = lexical.execute()
    # 将结果保存在tokens文件中
    with open('lexical_result.txt', 'w+') as f:
        lexical_result = lexical.get_result()
        for i in lexical_result:
            f.write(i.type + '\t' + i.str + '\t' + str(i.line) + '\n')
    # 打印结果  -> 结果全部保存在BUFFER字符串中
    buffer = []
    print('词法分析是否成功:\t', lexical_success)
    buffer.append('词法分析是否成功: ' + str(lexical_success) + '\n')

    if lexical._flag:
        with open('lexical_error.txt') as fp:
            for line in fp.readlines():
                buffer.append(line)
        #print('错误原因:\t', lexical.get_error().info,'\t错误数据为:\t',lexical.get_error().values,
        #      '\t错误行数为:\t',lexical.get_error().line)
    else:
        #lexical_result = lexical.get_result()
        print('词法分析结果:')
        buffer.append('词法分析结果: ')
        # print("type content line")
        for i in lexical_result:
            print(i.type, i.str, i.line)
            buffer.append('(%s, %s, %s)' % (i.type, i.str, i.line))


    return buffer


def syntax_analysis():
    # 语法分析
    parser = Parser()
    # 语法规则
    '''
    S->mACn|@
    A->BA|@
    B->gbl
    C->DC|@
    D->E|F|G|I|H|J|L|l
    E->cjMkDQ
    Q->dD
    F->fjMkD
    G->ejKlMlKkD
    H->hNl
    I->ibl
    J->mCn
    K->btN
    L->Kl
    M->NR
    N->OT
    R->uN|vN|wN|xN|yN|zN
    T->pOT|qOT|@
    O->PU
    U->rPU|sPU|@
    P->a|b|jNk
    '''
    parser.open('grammar1211.txt')  # 语法规则保存的地方

    parser.make_first()
    parser.make_follow()
    parser.make_pretable()
    table = list()

    if not parser.iserror:
        _flag = True
        for key1 in parser.pretable.keys():
            if _flag:
                table.append(list(parser.pretable[key1]))
                # print(list(parser.pretable[key1]))
                _flag = False
            table.append(list(parser.pretable[key1].values()))
            # print(key1,list(parser.pretable[key1].values()))
            # 此处可以得到字符串或者表达式是否满足语法规则，但要先转化成符合语义规则的形式
    else:
        print("\33[不是LL1文法")

    if os.path.exists('LL(1).txt'):
        os.remove('LL(1).txt')
    with open("LL(1).txt", 'a+') as f:
        f.write("\t")
        for i in list(parser.pretable.keys()):
            f.write(str(i) + "\t")
        f.write("\n\n")
        for i in range(0, len(table[0])):
            for array in table:
                if str(array[i]) == "error":
                    f.write("\t")
                else:
                    f.write(str(array[i]) + "\t")
            f.write("\n\n")


def semantic_analysis():
    global p
    # 语义分析
    map_list = list()
    input_str = ''
    map_line = list()
    with open('lexical_result.txt') as f:
        for line in f.readlines():
            line = line[:-1].split('\t')
            if line[0]:
                input_str += line[0]
                map_list.append(line[1])
                map_line.append(line[2])



    # input str 标识符 map-lsit 字符 map-line 行数
    p.createSymbolList(input_str, map_list, map_line)
    # 语义分析得到chart 符号表 temp_list 临时变量表 seq_list四元式表
    p.analysis('LL(1).txt')  # 生成的的ll1规则表LL(1)


def prelex(t2):
    t2.delete(0.0, END)
    buffer = lexical_analysis()
    str1 = '\n'.join(buffer)
    t2.insert(END, str1)


def prepars(t2):
    t2.delete(0.0, END)
    syntax_analysis()
    fp = open('LL(1).txt','r', encoding='UTF-8')
    buffer = fp.read()
    t2.insert(END, buffer)
    fp.close()
    # os.remove("LL(1).txt")


def preseman(t2):
    t2.delete(0.0, END)
    semantic_analysis()
    if p.flag:
        fp = open('ERROR.txt', 'r', encoding='UTF-8')
        buffer = fp.read()
        t2.insert(END, buffer)
        fp.close()
        # os.remove("Sequence.txt")
    else:

        fp = open('Sequence.txt', 'r', encoding='UTF-8')
        buffer = fp.read()
        t2.insert(END, buffer)
        fp.close()
        # os.remove("Sequence.txt")


def predo(t2):
    global p
    t2.delete(0.0, END)

    seq_index = ''
    with open("seq_index.txt", 'r') as f:
        for line in f.readlines():
            seq_index += line[0]
    p.seq_index = seq_index
    VM(p.chart, p.temp_list, p.seq_list, p.seq_index)


    buffer = '程序运行完成,下面是运行结果：\n'

    fp = open('Result.txt', 'r', encoding='UTF-8')
    buffer += fp.read()
    t2.insert(END, buffer)
    fp.close()


def openfile(t1):
    t1.delete(0.0, END)
    global content
    global file_name
    file_name = tkinter.filedialog.askopenfilename()
    print(file_name)
    source_file = open(file_name, 'r', encoding='UTF-8')
    content = source_file.read()
    t1.insert(END, content)


if __name__ == '__main__':

    # 定义一个顶级大窗口
    root = Tk()
    root.geometry('1200x450')
    root.iconbitmap('./icon.ico')
    root.title('Super_C_Compiler')
    # 在大窗口下定义一个顶级菜单实例
    menubar = Menu(root)

    # 打开文件菜单
    open_menu = Menu(menubar)
    open_menu.add_command(label="打开文件", command=lambda: openfile(t1))
    menubar.add_cascade(label='打开', menu=open_menu)

    ana_menu = Menu(menubar)
    ana_menu.add_command(label='词法分析', command=lambda: prelex(t2))
    ana_menu.add_command(label='语法分析', command=lambda: prepars(t2))
    ana_menu.add_command(label='语义分析', command=lambda: preseman(t2))
    menubar.add_cascade(label='分析', menu=ana_menu)

    do_menu = Menu(menubar)
    do_menu.add_command(label='解释执行', command=lambda: predo(t2))
    menubar.add_cascade(label='执行', menu=do_menu)

    # 顶级菜单实例应用到大窗口中
    root['menu'] = menubar
    s1 = tkinter.Scrollbar()
    s2 = tkinter.Scrollbar()
    s3 = tkinter.Scrollbar()
    t1 = Text(root, width=60, height=30)
    t2 = Text(root, width=100, height=30, wrap='none')
    t1.grid(column=0, row=0, padx=7)
    t2.grid(column=1, row=0, padx=20)
    s1.config(command=t1.yview)
    s2.config(command=t2.yview)
    s3.config(command=t2.xview)
    t1.config(yscrollcommand=s1.set)
    t2.config(yscrollcommand=s2.set)
    t2.config(xscrollcommand=s3.set)

    l1 = Label(root, text='代码区域')
    l2 = Label(root, text='输出区域')
    l1.grid()
    l2.grid(row=1, column=1, sticky=S, pady=0)

    s1.grid(row=0, column=0, padx=0)
    s2.grid(row=0, column=0, padx=0)
    s3.grid(row=0, column=1, padx=0, sticky=N+S+E)
    root.mainloop()