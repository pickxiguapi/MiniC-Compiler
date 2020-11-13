import os


class NewT():
    # 申请临时变量
    def __init__(self, value):
        global newT_num
        self.value = value
        self.name = 'T' + str(newT_num)
        newT_num += 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return '\nname:{:10}value:{:5}'.format(self.name, self.value)

    def isdigit(self):
        return False


class label():
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class Sequence():
    # 四元式类
    def __init__(self, action, p1='_', p2='_', result='_'):
        self.action = action
        self.p1 = p1
        self.p2 = p2
        self.result = result

    def __str__(self):
        return '{:5}{:10}{:10}{:10}'.format(str(self.action), str(self.p1), str(self.p2), str(self.result))

    def __repr__(self):
        return '{:5}{:10}{:10}{:10}'.format(str(self.action), str(self.p1), str(self.p2), str(self.result))


class element():
    # 每个符号的一些信息
    def __init__(self, symbol, value, line):
        self.symbol = symbol
        self.value = value
        self.line = line

        # get each key by value
        dic = {'NUM': 'a', 'ID': 'b', 'if': 'c', 'else': 'd', 'for': 'e', 'while': 'f', 'int': 'g', 'write': 'h',
               'read': 'i', '(': '(', ')': ')', ';': ';', '{': '{', '}': '}', ',': ',', '+': '+', '-': '-', '*': '*',
               '/': '/', '=': '=', '>': '>', '<': '<', '>=': 'w', '<=': 'x', '!=': 'y', '==': 'z', '++': '1',
               '--': '2', '#': '#', 'main': '3', 'return': '4', '&&': '5', '||': '6', 'char': 's', 'float': 'r'}

        dic = dict(zip(dic.values(), dic.keys()))
        self.type = dic[symbol]

    def __str__(self):
        return '\n符号:' + self.symbol + '\t值:' + self.value + '\t行数:' + str(self.line) + '\t类型:' + self.type

    def __repr__(self):
        return '\n符号:' + self.symbol + '\t值:' + self.value + '\t行数:' + str(self.line) + '\t类型:' + self.type


class MyException(Exception):
    def __init__(self, line, type, content):
        Exception.__init__(self)
        error = '{}ERROR  Line:{}  {}'.format(type, line, content)
        print(error)

        with open('Error.txt', 'a+') as f:
            f.write('{}\n'.format(error))


class Pro():
    # 这里用于错误分析
    def __init__(self):
        self.flag = False
        if os.path.exists('Error.txt'):
            os.remove('Error.txt')

    def _err(self, line, type, content):
        MyException(line, type, content)
        self.flag = True

    def __readRules(self, filename):
        with open(filename, encoding='UTF-8') as f:
            # 去掉最后的 '\n'
            ter_list = f.readline()[:-1].split('\t')
            dic = dict()
            for line in f.readlines():
                line_list = line[:-1].split('\t')
                line_dic = dict()
                for index, rule in enumerate(line_list):
                    if rule != '' and index != 0:
                        line_dic[ter_list[index]] = rule
                dic[line_list[0]] = line_dic
            return dic

    def createSymbolList(self, input_str, map_list, map_line):
        # 建立符号表
        # 词法分析给出的所有元素
        self.list = []

        for i, ch in enumerate(input_str):
            self.list.append(element(ch, map_list[i], map_line[i]))

        # 符号表
        self.chart = dict()
        # 函数名表
        self.function = dict()

        # 四元式表
        self.seq_list = list()
        self.seq_num = 0
        self.seq_index = 0
        self.val = 0
        global newT_num
        newT_num = 0
        # 临时变量表
        self.temp_list = list()

    def analysis(self, filename):
        # 读取规则获得规则表
        # 这里打开的是LL1.txt，为了获取规则
        # 大致读取内容如下： {'F': {'f': 'F->f(M)D'}, 'H': {'h': 'H->hN;'}, '9': {')': '9->@', ',': '9->,V'}, 'I': {'i': 'I->ib;'}, 'J': {'{': 'J->{C}'}
        self.rule = self.__readRules(filename)
        # self.ch为当前的字符
        self.ch = self.list.pop(0)

        # Z开始文法
        self._Z()

    def FIRST(self, symbol, ch):
        # ch在不在symbol的first集
        if ch in self.rule[symbol]:
            return True
        return False

    def FOLLOW(self, symbol, ch):
        # ch在不在symbol的follow集
        if ch in self.rule[symbol] and self.rule[symbol][ch].split('->')[1] == '@':
            return True
        return False

    def getNextch(self):
        self.ch = self.list.pop(0)

    def _Write(self):
        if os.path.exists('Sequence.txt'):
            os.remove('Sequence.txt')
        with open('Sequence.txt', 'a+') as f:
            for i, seq in enumerate(self.seq_list):
                f.write('{:2}[{}]\n'.format(i, seq))

        if os.path.exists('Parameters.txt'):
            os.remove('Parameters.txt')
        with open('Parameters.txt', 'a+') as f:
            for i in self.chart.keys():
                f.write('name:{:2}  value:0\n'.format(i))
            for i in self.temp_list:
                f.write('name:{:2}  value:0\n'.format(i.name))

        if os.path.exists('seq_index.txt'):
            os.remove('seq_index.txt')
        with open('seq_index.txt', 'w') as f:
            f.write(str(self.seq_index))

    def _op(self, op, p1, p2):
        '''

        :param op: 运算符
        :param p1: 运算数1
        :param p2: 运算数2
        :return: 
        '''
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

    def __VALUE(self, op, p1, p2):
        p1_t = 0
        p2_t = 0
        t0 = 0
        if isinstance(p1, NewT):
            p1_t = p1.value
        elif isinstance(p1, int):
            p1_t = p1
        else:
            p1_t = self.chart[p1]

        if isinstance(p2, NewT):
            p2_t = p2.value
        elif isinstance(p2, int):
            p2_t = p2
        else:
            p2_t = self.chart[p2]
        if isinstance(p1, int) and isinstance(p2, int):
            t0 = self._op(op, p1_t, p2_t)
        else:
            t0 = NewT(self._op(op, p1_t, p2_t))
            self.temp_list.append(t0)
        self.seq_list.append(Sequence(action=op, p1=p1, p2=p2, result=t0))
        self.seq_num += 1
        return t0

    def _Z(self):
        if self.ch.symbol == 'g':
            self.getNextch()
            self._Y()
            print('')
            self._Write()
        else:
            # 抛出缺少int
            self._err(self.ch.line, 'TYPE-', 'Wrong type define')  # line type content

    def _Y(self):

        f_name = self.ch.value
        self.function[f_name] = label()
        self.function[f_name + "_main"] = label()

        if self.ch.symbol == 'b':
            self.getNextch()
            if self.ch.symbol == '(':
                self.getNextch()
                self._X()
                if self.ch.symbol == ')':
                    self.getNextch()

                    self.function[f_name].value = self.seq_num

                    self._S()

                    self.seq_list.append(Sequence(action='j', result=self.function[f_name + "_main"]))
                    self.seq_num += 1
                    self.seq_index = self.seq_num

                    self.getNextch()

                    if self.ch.symbol == 'g':
                        self.getNextch()
                        self._Y()
                    else:
                        self._err(self.ch.line, 'DECLARATION-', 'Incorrect function / variable declaration')
                        print('1')
                        # 不正确的函数定义
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost )')
                    # 缺少 )
            else:
                self._err(self.ch.line, 'LOST-', 'Lost (')
                # 缺少(


        elif self.ch.symbol == '3':  # 主函数
            self.getNextch()
            if self.ch.symbol == '(':
                self.getNextch()
                if self.ch.symbol == ')':
                    self.getNextch()
                    self._S()

                else:
                    self._err(self.ch.line, 'LOST-', 'Lost )')
                    # print("缺少)")
            else:
                self._err(self.ch.line, 'LOST-', 'Lost )')
                # print("缺少(")
        else:
            # 错误的变量名或函数定义
            self._err(self.ch.line, 'DECLARATION-', 'Incorrect function / variable declaration')
            if(self.ch.symbol!='('):
                self.getNextch()
            if self.ch.symbol == '(':
                self.getNextch()
                self._X()
                if self.ch.symbol == ')':
                    self.getNextch()

                    self.function[f_name].value = self.seq_num

                    self._S()

                    self.seq_list.append(Sequence(action='j', result=self.function[f_name + "_main"]))
                    self.seq_num += 1
                    self.seq_index = self.seq_num

                    self.getNextch()

                    if self.ch.symbol == 'g':
                        self.getNextch()
                        self._Y()
                    else:
                        self._err(self.ch.line, 'DECLARATION-', 'Incorrect function / variable declaration')
                        print('1')
                        # 不正确的函数定义
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost )')
                    # 缺少 )
            else:
                self._err(3, 'GRAMMAR-', 'Undefined variable name used')
                # 缺少(


    def _X(self):
        if self.ch.symbol == 'g':
            self.getNextch()
            name = self.ch.value
            if self.ch.symbol == 'b':
                self.chart[name] = 0  # 应该是传过来的参数值
                self.getNextch()
                self._W()
            else:
                self._err(self.ch.line, 'DECLARATION-', 'Incorrect function / variable declaration')
                print('3')
        else:
            self._err(self.ch.line, 'TYPE-', 'Wrong type define')

    def _W(self):
        if self.ch.symbol == ',':
            self.getNextch()
            self._X()
        elif self.FOLLOW('W', self.ch.symbol):
            return

    def _V(self):
        if self.ch.symbol == 'b':
            self.getNextch()
            self._9()
        else:
            self._err(self.ch.line, 'DECLARATION-', 'Incorrect function / variable declaration')
            print('4')

    def _9(self):
        if self.ch.symbol == ',':
            self.getNextch()
            self._V()
        elif self.FOLLOW('9', self.ch.symbol):
            return

    def _S(self):
        print(self.ch)
        if self.ch.symbol == '{':
            self.getNextch()
            self._A()
            self._C()
            if self.ch.symbol == '4':
                self.getNextch()
                if self.ch.symbol == 'b':
                    self.val = self.ch.value
                    self.getNextch()
                    if self.ch.symbol == ';':
                        self.getNextch()
                        if self.ch.symbol == '}':
                            # 栈空，不读取下一个字符
                            pass
                        else:
                            # print("lose }")
                            self._err(self.ch.line, 'LOST-', 'Lost }')
                    else:
                        # print("lose ;")
                        self._err(self.ch.line, 'LOST-', 'Lost ;')
                else:
                    # print("lose variable")
                    self._err(self.ch.line, 'TYPE-', 'Wrong return type')
            else:
                # print("lose return")
                self._err(self.ch.line, 'LOST-', 'Lost return')

        elif self.FOLLOW('S', self.ch.symbol):
            return
        else:
            # print("lose {")
            self._err(self.ch.line, 'LOST-', 'Lost {')

    def _A(self):
        # First
        if self.FIRST('B', self.ch.symbol):
            self._B()
            self._A()

        elif self.FOLLOW('A', self.ch.symbol):
            return

        else:
            self._err(self.ch.line, 'TYPE-', 'Wrong type declaration')

    def _B(self):
        if self.ch.symbol == 'g':
            self.getNextch()
            if self.ch.symbol == 'b':
                # 获得名字添加符号表
                name = self.ch.value
                self.getNextch()
                if self.ch.symbol == ';':
                    self.chart[name] = 0
                    self.getNextch()
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost ;')
            else:
                self._err(self.ch.line, 'DECLARATION-', 'Wrong type declaration')
        else:
            self._err(self.ch.line, 'DECLARATION-', 'Wrong type declaration')

    def _C(self):
        if self.FIRST('D', self.ch.symbol):
            self._D()
            self._C()
        elif self.FOLLOW('C', self.ch.symbol):
            return
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Expression')

    def _D(self):
        if self.FIRST('E', self.ch.symbol):
            self._E()
        elif self.FIRST('F', self.ch.symbol):
            self._F()
        elif self.FIRST('G', self.ch.symbol):
            self._G()
        elif self.FIRST('I', self.ch.symbol):
            self._I()
        elif self.FIRST('H', self.ch.symbol):
            self._H()
        elif self.FIRST('J', self.ch.symbol):
            self._J()
        elif self.FIRST('L', self.ch.symbol):
            self._L()
        elif self.ch.symbol == ';':
            self.getNextch()
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Expression')

    def _E(self):
        if self.ch.symbol == 'c':
            self.getNextch()
            if self.ch.symbol == '(':
                self.getNextch()
                r = self._M()
                if self.ch.symbol == ')':
                    label1 = label()
                    label2 = label()
                    self.seq_list.append(Sequence(action='j=', p1=0, p2=r, result=label1))
                    self.seq_num += 1
                    self.getNextch()
                    self._D()
                    self.seq_list.append(Sequence(action='j', result=label2))
                    self.seq_num += 1
                    label1.value = self.seq_num
                    self._Q()
                    label2.value = self.seq_num
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost )')
            else:
                self._err(self.ch.line, 'LOST-', 'Lost (')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong if expression')

    def _Q(self):
        if self.ch.symbol == 'd':
            self.getNextch()
            self._D()

        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong else expression')

    def _F(self):
        if self.ch.symbol == 'f':
            label1 = label()
            label2 = label()
            self.getNextch()
            label1.value = self.seq_num
            if self.ch.symbol == '(':
                self.getNextch()
                r = self._M()
                if self.ch.symbol == ')':
                    self.getNextch()
                    self.seq_list.append(Sequence(action='j=', p1=0, p2=r, result=label2))
                    self.seq_num += 1
                    self._D()
                    self.seq_list.append(Sequence(action='j', result=label1))
                    self.seq_num += 1
                    label2.value = self.seq_num
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost )')
            else:
                self._err(self.ch.line, 'LOST-', 'Lost (')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong while expression')

    def _G(self):
        if self.ch.symbol == 'e':
            self.getNextch()
            label1 = label()
            label2 = label()
            label3 = label()
            label4 = label()
            if self.ch.symbol == '(':
                self.getNextch()
                self._K()
                if self.ch.symbol == ';':
                    self.getNextch()
                    label1.value = self.seq_num
                    r = self._M()
                    if self.ch.symbol == ';':
                        self.getNextch()
                        self.seq_list.append(Sequence(action='j=', p1=0, p2=r, result=label2))
                        self.seq_num += 1
                        self.seq_list.append(Sequence(action='j', result=label3))
                        self.seq_num += 1
                        label4.value = self.seq_num
                        self._K()
                        self.seq_list.append(Sequence(action='j', result=label1))
                        self.seq_num += 1
                        if self.ch.symbol == ')':
                            self.getNextch()
                            label3.value = self.seq_num
                            self._D()
                            self.seq_list.append(Sequence(action='j', result=label4))
                            self.seq_num += 1
                            label2.value = self.seq_num
                        else:
                            self._err(self.ch.line, 'LOST-', 'Lost )')
                    else:
                        self._err(self.ch.line, 'LOST-', 'Lost ;')
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost ;')
            else:
                self._err(self.ch.line, 'LOST-', 'Lost (')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong for expression')

    def _H(self):
        if self.ch.symbol == 'h':
            self.getNextch()
            t = self._N()
            if self.ch.symbol == ';':
                self.seq_list.append(Sequence(action='out', p1=t))
                self.seq_num += 1
                self.getNextch()
            else:
                self._err(self.ch.line, 'LOST-', 'Lost ;')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong write expression')

    def _I(self):
        if self.ch.symbol == 'i':
            self.getNextch()
            if self.ch.symbol == 'b':
                name = self.ch.value
                self.getNextch()
                if self.ch.symbol == ';':
                    self.seq_list.append(Sequence(action='in', p1=name))
                    self.seq_num += 1
                    self.getNextch()
                else:
                    self._err(self.ch.line, 'LOST-', 'Lost ;')
            else:
                self._err(self.ch.line, 'GRAMMAR-', 'Wrong write expression')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong read expression')

    def _J(self):
        if self.ch.symbol == '{':
            self.getNextch()
            self._C()
            if self.ch.symbol == '}':
                self.getNextch()
            else:
                self._err(self.ch.line, 'LOST-', 'Lost }')
        else:
            self._err(self.ch.line, 'LOST-', 'Lost {')

    def _K(self):
        if self.ch.symbol == 'b':
            name = self.ch.value
            self.getNextch()
            if self.ch.symbol == '=':
                self.getNextch()
                t = self._N()
                value = t
                if isinstance(value, NewT):
                    value = t.value
                if name in self.chart:
                    self.chart[name] = value
                    self.seq_list.append(Sequence(action='=', p1=t, result=name))
                    self.seq_num += 1
                    if t in self.function:
                        self.seq_list.append(Sequence(action='j', result=self.function[t]))
                        self.seq_num += 1
                else:
                    self._err(self.ch.line, 'GRAMMAR-', 'Undefined variable name used')
                    print('1')
            else:
                self._err(self.ch.line, 'GRAMMAR-', 'Wrong operation expression')
                print('2')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong expression')

    def _L(self):
        if self.FIRST('K', self.ch.symbol):
            self._K()
            if self.ch.symbol == ';':
                self.getNextch()
            else:
                self._err(self.ch.line, 'LOST-', 'Lost ;')
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong expression')

    def _j(self):
        if self.FIRST('N', self.ch.symbol):  # 注意  j k为非终结符
            r = self._N()
            t = self._R(r)  # t 存储条件运算后的临时变量值
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Logic expression')

    def _k(self, t):  # 注意  j k为非终结符
        if self.ch.symbol == '6':
            self.getNextch()
            r = self._j()
            t1 = self.__VALUE('||', t, r)
            return t1
        elif self.ch.symbol == '5':
            self.getNextch()
            r = self._j()
            # tmp = self._k(r)
            t1 = self.__VALUE('&&', t, r)
            return t1
        elif self.FOLLOW('k', self.ch.symbol):
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Logic expression')

    def _M(self):
        if self.FIRST('j', self.ch.symbol):  # 注意  j k为非终结符
            t = self._j()
            if self.FIRST('k', self.ch.symbol):
                res = self._k(t)
                return res
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Logic expression')

    def _N(self):
        if self.FIRST('O', self.ch.symbol):
            p = self._O()
            t = self._T(p)
            return t

        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong Logic expression')

    def _R(self, r):
        if self.ch.symbol == '>':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('>', r, p)
            return t
        elif self.ch.symbol == '<':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('<', r, p)
            return t
        elif self.ch.symbol == 'w':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('>=', r, p)
            return t
        elif self.ch.symbol == 'x':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('<=', r, p)
            return t
        elif self.ch.symbol == 'z':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('==', r, p)
            # print("####3333333")
            # print(r)
            # print(p)
            # print(t)
            return t
        elif self.ch.symbol == 'y':
            self.getNextch()
            p = self._N()
            t = self.__VALUE('!=', r, p)
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong operation expression')
            print('3')

    def _T(self, p):
        if self.ch.symbol == '+':
            self.getNextch()
            r = self._O()
            t0 = self.__VALUE('+', p, r)
            # t0 = p + r
            # print ('加法操作' + str(p) + '+' + str(r) +  '=' + str(t0))
            # self.seq_list.append(Sequence(action='+',p1=p,p2=r,result=t0))
            # self.seq_num += 1
            t = self._T(t0)
            return t
        elif self.ch.symbol == '-':
            self.getNextch()
            r = self._O()
            t0 = self.__VALUE('-', p, r)
            # t0 = p - r
            # print ('减法操作' + str(p) + '-' + str(r) +  '=' + str(t0))
            # self.seq_list.append(Sequence(action='-',p1=p,p2=r,result=t0))
            # self.seq_num += 1
            t = self._T(t0)
            return t
        elif self.FOLLOW('T', self.ch.symbol):
            t = p
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong operation expression')
            print('4')

    def _O(self):
        if self.FIRST('P', self.ch.symbol):
            p = self._P()
            t = self._U(p)
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong operation expression')
            print('5')

    def _U(self, p):
        if self.ch.symbol == '*':
            self.getNextch()
            r = self._P()
            t0 = self.__VALUE('*', p, r)
            # t0 = p * r
            # print ('乘法操作' + str(p) + '*' + str(r) +  '=' + str(t0))
            # self.seq_list.append(Sequence(action='*',p1=p,p2=r,result=t0))
            # self.seq_num += 1
            t = self._U(t0)
            return t
        elif self.ch.symbol == '/':
            self.getNextch()
            r = self._P()
            t0 = self.__VALUE('/', p, r)
            # t0 = p//r
            # print ('除法操作' + str(p) + '/' + str(r) +  '=' + str(t0))
            # self.seq_list.append(Sequence(action='/',p1=p,p2=r,result=t0))
            # self.seq_num += 1
            t = self._U(t0)
            return t
        elif self.FOLLOW('U', self.ch.symbol):
            t = p
            return t
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong operation expression')
            print('6')

    def _P(self):
        if self.ch.symbol == '(':
            self.getNextch()
            t = self._N()
            p = t
            if self.ch.symbol == ')':
                self.getNextch()
                return p
            else:
                self._err(self.ch.line, 'LOST-', 'Lost )')
        elif self.ch.symbol == 'a':
            p = int(self.ch.value)
            self.getNextch()
            return p
        elif self.ch.symbol == 'b':
            p = self.ch.value
            self.getNextch()
            p = self._8(p)
            return p
        else:
            self._err(self.ch.line, 'GRAMMAR-', 'Wrong expression')

    def _8(self, p):
        if self.ch.symbol == '(':
            self.getNextch()
            self._V()
            if self.ch.symbol == ')':
                self.getNextch()
                self.seq_list.append(Sequence(action='j', result=self.function[p]))
                self.function[p + "_main"].value = self.seq_num + 2
                return self.val

            else:
                self._err(self.ch.line, 'LOST-', 'Lost )')
        else:
            return p

