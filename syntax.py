from collections import OrderedDict as odict
import os
'''
用@代替ε
'''
class Parser:
    '解析文法文件'

    lines = []
    terminal = set()  # 终结符
    nonterminal = set()  # 非终结符
    follow = odict() # follow集
    first = odict()
    start = ''
    pretable = odict() # 预测分析表
    can_be_empty = [] # 能推导出空串的非终
    iserror = False

    def open(self, path):
        with open(path) as f:
            for line in f:
                self.lines.append(line.strip('\n').replace(' ',''))
                self.nonterminal.add(line[0])
            # 分割一遍
            _tosplit = []
            for line in self.lines:
                if '|' in line:
                    _tosplit.append(line)
            for _line in _tosplit:
                self._split(_line)

            # 初始化终结符和非终结符集
            for line in self.lines:
                for char in line.split('->')[1]:
                    if char not in self.nonterminal:
                        self.terminal.add(char)
            self.terminal.add('#')
            # 初始化可推导出空串的非终结符集合，两次扫描
            for line in self.lines:
                left, right = line.split('->')
                if right=='@':
                    self.can_be_empty.append(left)
            for line in self.lines:
                left, right = line.split('->')
                _flag = True
                for char in right:
                    if char not in self.can_be_empty:
                        _flag = False
                if _flag:
                    self.can_be_empty.append(left)




            left,right = self.lines[0].split('->')
            self.start = left

        for non in self.nonterminal:
            self.first[non] = [set(), set()]
            self.follow[non] = [set(), set(), set()] # 三个集合分别为，终结符集合，非终结符First集,非终结符Follow集
        for ter in self.terminal:
            if ter != '@':
                self.pretable[ter] = odict()
            for non in self.nonterminal:
                if ter!='@':
                    self.pretable[ter][non] = 'error'######################################3


    def make_first(self):
        # 终结符直接放到第一个set，非终结符暂时放到第二个set
        for line in self.lines:
            left,right = line.split('->')
            if right[0] in self.terminal:
                assert isinstance(self.first[left][0], set)
                self.first[left][0].add(right[0])
            elif right[0] in self.nonterminal:
                # 如果第一个非终结符能推导出空串的情况
                if right[0] in self.can_be_empty:
                    self.first[left][1].add(right[1])
                self.first[left][1].add(right[0])
        '''        
        for line in self.nonterminal:
            print("@@@@@@@@@@@@@@@@@@")
            print(line)
            print(self.first[line][0])
            print(list(self.first[line]))
        '''    
        #处理第二个set，将非终结符的first集合添加倒第一个set，移除非终结符，直到第二个set为空
        for item in self.nonterminal:
            while(len(self.first[item][1])>0):
                for _non in self.first[item][1].copy():#_on为first集中的非终结符
                    if len((self.first[_non][0]-{'@'}))!=0:
                        #如果含有的非终结符的first____既有非终结符又有终结符
                        if len((self.first[_non][1]))!=0:       
                            self.first[item][0] |= (self.first[_non][0]-{'@'})
                            self.first[item][0] |= (self.first[_non][1])
                        else:
                        #如果含有的非终结符的first____只有终结符
                            self.first[item][0]|= (self.first[_non][0]-{'@'})
                    else:
                        #如果含有的非终结符的first____只有非终结符
                        self.first[item][0].add(_non)
                        #print("*******************")
                        #print(self.first[item][0])
                        #print(_non)
                        #print("*******************")
                    # self.first[item][1] |= self.first[_non][1]
                    self.first[item][1].remove(_non)
        for item in self.can_be_empty:
            self.first[item][0].add('@')
        for item in self.nonterminal:
            del self.first[item][1]
            
        #第二次转化，进一步将firtst中的非终结符转化成终结符
        for line in self.nonterminal:
            for temp in list(self.first[line][0]):
                for item in self.nonterminal:
                    if(temp==item):
                        self.first[line][0] |= (self.first[temp][0]-{'@'})
                        self.first[line][0].remove(temp)
        '''            
        for line in self.nonterminal:
            print("@@@@@@@@@@@@@@@@@@")
            print(line)
            print(self.first[line][0])
            print(list(self.first[line]))  
        '''
               
    def make_follow(self):
        # 把#放入开始符号的follow集中
        self.follow[self.start][0].add('#')
        # 非终结符直接放到第一个set,非终结符的first集和follow集暂时放到第2和第3个set
        for production in self.lines:
            left,right = production.split('->')
            for i in range(len(right)-1):
                # print("debug:current nonterminal{}".format(right[i]))
                if right[i] in self.nonterminal:
                    # 非终结符紧跟一个终结符的情况
                    if right[i+1] in self.terminal:
                        self.follow[right[i]][0].add(right[i+1])
                    # 非终结符紧跟一个非终结符的情况
                    elif right[i+1] in self.nonterminal:
                        self.follow[right[i]][1].add(right[i+1])
                        # 如果后跟的非终结符含有空串@,就把其follow集也加入
                        if right[i+1] in self.can_be_empty:
                            self.follow[right[i]][2].add(right[i+1])
            # 对形如U－>…P的产生式的情况，把Follow(U)添加倒Follow（P)
            _tmp = right[len(right)-1]
            if _tmp in self.nonterminal:
                if _tmp is not left:
                    # print("1.add {}'s follow to {}".format(left, _tmp))
                    self.follow[_tmp][2].add(left)
            # 对形如U->…PB的产生式，且B可以为空的情况，把Follow(U)添加倒Follow（P)
            if _tmp in self.can_be_empty:
                _tmp2 = right[len(right)-2]
                if _tmp2 in self.nonterminal:
                    self.follow[_tmp2][2].add(left)
                    # print("2.add {}'s follow to {}".format(left, _tmp2))

        # 处理第2，3个集合直到为空
        notempty = 1
        while(notempty>0):
            for item in self.follow:
                if len(self.follow[item][2])>0:
                    _toremove = []
                    tmp_set = set()
                    for ans in self.follow[item][2]:
                        self.follow[item][0] |= self.follow[ans][0]
                        self.follow[item][1] |= self.follow[ans][1]
                        tmp_set |= self.follow[ans][2]
                        _toremove.append(ans)
                    self.follow[item][2] |= tmp_set
                    # 移除第3个集合中非终结符
                    for i in _toremove:
                        self.follow[item][2].remove(i)

            for item in self.follow:
                if len(self.follow[item][1])>0:
                    _toremove = []
                    for ans in self.follow[item][1]:
                        self.follow[item][0] |= (self.first[ans][0]-{'@'})
                        _toremove.append(ans)
                    # 移除第2个集合中非终结符
                    for i in _toremove:
                        self.follow[item][1].remove(i)
            for item in self.follow:
                if self.follow[item][1]!=set() or (self.follow[item][2]!=set()):
                    notempty += 1
                    break
            notempty -= 1


    def make_pretable(self):
        '''
        (1)对First(A)中的每一个终结符a，把A->XXX加入M[A,a]中。
        (2)若产生式的右部可以为空，则把产生式加入左部的follow集中的每个元素的对应位置
        '''
        # 执行步骤(1)
        for line in self.lines:
            # left和x作为坐标确定分析表中的位置
            #print("$$$$$$$$$$$$$$")
            #print(line)
            left, right = line.split('->')
            #print(left,right)
            # (1) 如果右部是终结符开头，直接把右部加入开头的终结符
            if right[0] in self.terminal:
                self._set_tableitem(right[0], left, right)
                #print("##########333")
                #print(right[0], left, right)
            # (2) 如果右部是非终结符开头，则把右部加入此非终结符的first集的每个元素
            elif right[0] in self.nonterminal:
                for i in self.first[right[0]][0]:
                    self._set_tableitem(i, left, right)
            # (3) 如果右部可以为空
            m_canbeempty = True
            for ch in right:
                if ch in self.terminal and ch != '@':
                    m_canbeempty = False
                elif ch in self.nonterminal and ch not in self.can_be_empty:
                    m_canbeempty = False
            if m_canbeempty:
                for element in self.follow[left][0]:
                    self._set_tableitem(element, left, right)
                    print("we taking {} into {}'s ".format(line, element))

            # isempty_exist = False
            # for x in self.first[left][0]:
            #     if x == '@':
            #         isempty_exist = True
            #     self._set_tableitem(x, left, line)
            # # 执行步骤(2)
            # if isempty_exist:
            #     for x in self.follow[left][0]:
            #         self._set_tableitem(x, left, line)



    def ll1(self, _str):
        symstack = ['#', self.start]
        print(symstack)
        inputstack = list(_str)
        print(inputstack)
        current_sym_top = symstack.pop()
        current_in_top = inputstack.pop(0)
        counter = 0
        try:
            while(current_sym_top != '#' ):
                counter += 1
                print("第{}步   ,\33[4m符号栈\33[0m:{}\33[4m输入栈\33[0m{}"
                      .format(str(counter).ljust(3),
                              (str(symstack)[:-1]+','+current_sym_top+']').ljust(20),
                              ('['+current_in_top+','+str(inputstack)[1:]).ljust(10)))
                if current_sym_top in self.nonterminal:
                    m_production = self.pretable[current_in_top][current_sym_top].strip('->')
                    if m_production == 'error':
                        print('\33[35merror,分析停止')
                        break
                    elif m_production == '@':
                        current_sym_top = symstack.pop()
                    else:
                        # 把产生式的每个非终结符入栈
                        tmp = list(m_production)
                        for i in range(len(m_production)):
                            symstack.append(tmp.pop())
                        current_sym_top = symstack.pop()
                        # print("产生式:->{}".format(m_production))
                elif current_sym_top in self.terminal:
                    current_sym_top = symstack.pop()
                    current_in_top = inputstack.pop(0)
            if current_sym_top == current_in_top == '#':
                print("\33[35;1m分析成功\33[4m")
        except:
            print('\33[35merror,分析停止')




    def _split(self, line):
        # 分割带有 '|' 的产生式
        left, right = line.split('->')
        factions = right.split('|')
        for faction in factions:
            self.lines.append(left + '->' + faction)
        # 删除被分割的产生式
        self.lines.remove(line)


    def _set_tableitem(self, x, y, content):
        try:
            if self.pretable[x][y] == 'error' or self.pretable[x][y] == content:
                self.pretable[x][y] = y + '->' + content
                #print("############3")
                #print(y)
                #print(self.pretable[x][y] )
            else:
            #    print("{}将被替换为{}".format(self.pretable[x][y], content))
                self._error(self.pretable[x][y], content, x, y)
        except:
            print("x:{}y:{}content:{}".format(x, y, content))
    def _error(self, str1, str2, x, y):
        print("不是LL1文法,冲突为{},{},位置为{}，{}".format(str1, str2, x, y))
        self.iserror = True



if __name__ == '__main__':
    parser = Parser()
    parser.open('grammar.txt')
    print(parser.lines)
    print(parser.nonterminal)
    print(parser.terminal)
    print("start symbol:{}".format(parser.start))

    parser.make_first()
    parser.make_follow()
    parser.make_pretable()
    table=list()
    if not parser.iserror:
        _flag = True
        for key1 in parser.pretable.keys():
            if _flag:
                table.append(list(parser.pretable[key1]))
                #print("####################") 
                #print(list(parser.pretable[key1]))
                #print(parser.follow)
                _flag = False
            table.append(list(parser.pretable[key1].values()))
            #print(key1,list(parser.pretable[key1].values()))
        

    else:
        print("\33[不是LL1文法")
        
    #print(table)
    #print(len(table[0]))
    #print(list(parser.pretable.keys()))
    if os.path.exists('LL(1).txt'):
        os.remove('LL(1).txt')
    with open("LL(1).txt",'a+') as f:
        f.write("\t")
        for i in list(parser.pretable.keys()):
            f.write(str(i) + "\t" )
        f.write("\n")
        for i in range(0,len(table[0])):
            for array in table:
                if(str(array[i])=="error"):
                    f.write("\t")
                else:     
                    f.write(str(array[i])+"\t")
            f.write("\n")       
