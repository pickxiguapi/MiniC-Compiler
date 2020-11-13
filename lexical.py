"""
词法分析
"""
import re
import os
class Error:
    """
    错误
    """
    def __init__(self, error_info):
        """
        构造
        :param error_info: 错误信息
        """
        self.info = error_info

class LexicalError(Error):
    """
    词法错误
    """
    def __init__(self, error_info, error_line,error_value=None):
        """
        构造
        :param error_info: 错误信息
        :param error_line: 错误行数
        :param error_value:错误数据
        """
        super().__init__(error_info)
        self.line = error_line
        self.values=error_value
        
# 所有的 token 的类型,顺序为匹配先后顺序
dic = {'num':'a',
       'id':'b',
       'if':'c',
       'else':'d',
       'for':'e',
       'while':'f',

       'int':'g',
       'float':'r',
       'char':'s',

       'write':'h',
       'read':'i',

       'and': '5',
       'or': '6',

       'left-parentheses':'(',
       'right-parentheses':')',
       'semicolon':';',#l
       'left-brace':'{',#m
       'right-brace':'}',#n
       'comma':',',#o
       'addition':'+',#p
       'subtraction':'-',#q
       'multiplication':'*',#r
       'division':'/',#s
       'evaluate':'=',#t
       'bigger':'>',#u
       'smaller':'<',#v

       'bigger-equal':'w',
       'smaller-equal':'x',
       'not-equal':'y',
       'equal':'z',
       'self-increasing':'1',
       'self-reduction':'2',
       'main':'3',
       'return':'4'
}

token_type = [
    'else',
    'if',
    'int',
    'char',
    'float',
    'return',
    'void',
    'while',
    'for',
    'write',
    'read',
    'main',
    'self-increasing',
    'self-reduction',
    'addition',
    'subtraction',
    'multiplication',
    'division',
    'bigger-equal',
    'bigger',
    'smaller-equal',
    'smaller',
    'not-equal',
    'equal',
    'evaluate',
    'semicolon',
    'comma',
    'left-parentheses',
    'right-parentheses',
    'left-bracket',
    'right-bracket',
    'left-brace',
    'right-brace',
    'id',
    'num',
    'and',
    'or'
]

# 分隔符号
split_char_type = [
    'space'
]

# 注释
note_char_type = [
    'note-start',
    'note-end'
]

# 正则表达式字典
regex_dict = {
    'space': r' +',# 分隔符号
    'note-start': r'/\*',# 注释
    'note-end': r'\*/',
    'else': r'else',# 控制
    'if': r'if',

    'int': r'int',
    'char':r'char',
    'float':r'float',

    'return': r'return',
    'void': r'void',
    'while': r'while',
    'for': r'for',
    'write':r'write',
    'read':r'read',
    'main':r'main',
    'addition': r'\+',# 运算符
    'subtraction': r'-',
    'self-increasing': r'\+\+',
    'self-reduction': r'--',
    'multiplication': r'\*',
    'division': r'/',
    'bigger': r'>',
    'bigger-equal': r'>=',
    'smaller': r'<',
    'smaller-equal': r'<=',
    'equal': r'==',
    'not-equal': r'!=',
    'evaluate': r'=',
    'semicolon': r';',# 其他符号
    'comma': r',',
    'left-parentheses': r'\(',
    'right-parentheses': r'\)',
    'left-bracket': r'\[',
    'right-bracket': r'\]',
    'left-brace': r'\{',
    'right-brace': r'\}',
    'id': r'[a-zA-Z][a-zA-Z_0-9]*',# 变量名
    'num': r'[1-9][0-9]*|0',# 数字

    'and': r'&&',
    'or': r'\|\|',
}


class Token:
    """
    Token
    """
    def __init__(self, token_type='', token_str='', token_line=-1):
        """
        构造
        :param token_type: Token 的类型
        :param token_str: Token 的内容
        :param token_line: Token 所在行数
        """
        self.type = token_type
        self.str = token_str
        self.line = token_line


class Lexical:
    """
    词法分析器
    """
    def __init__(self):
        """
        构造
        """
        # 错误
        self.__error = None

        # 源代码
        self.__source = ''
        
        #记录是否保存成功
        self._flag=0
        
        # 分隔出来的每一行
        self.__lines = list()

        # 结果
        self.__tokens = list()
        
        #-_-
        if os.path.exists('lexical_error.txt'):
            os.remove('lexical_error.txt')

    def load_source(self, source):
        """
        装载源代码
        :param source: 源代码
        """
        self.__source = source

    def execute(self):
        """
        执行词法分析
        :return: 词法分析是否成功
        """
        self.__replace_useless_chars()
        if self.__del_notes():
            self.__split_lines()
            if self.__split_tokens():
                self.__del_spaces()
                if self._flag==0:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_result(self):
        """
        获取结果
        :return: token 列表,将状态符号转化为字母便于分析
        
        """
        for i in self.__tokens:     
            i.type=dic[i.type]
        return self.__tokens

    def get_error(self):
        """
        获取错误
        :return: 错误原因
        """
        return self.__error

    def __replace_useless_chars(self):
        """
        替换无用的字符
        """
        self.__source = self.__source.replace('--', '=c-1')
        self.__source = self.__source.replace('++', '=i+1')
        self.__source = self.__source.replace('\r', '\n')
        self.__source = self.__source.replace('\t', '    ')

    def __del_notes(self):
        """
        删除注释
        :return: 是否删除成功
        """
        # 计数器，用来确认注释开始符和注释结束符的数量是否相等
        note_count = 0
        # 缓冲区
        buffer = self.__source
        # 结果
        result = self.__source

        # 判断是否匹配到了末尾
        while True:
            # 尝试匹配 */
            match = re.compile(regex_dict[note_char_type[0]]).search(buffer)
            # 如果匹配到了
            if match:
                left_note_start = match.start()
                # 开始匹配 */
                match2 = re.compile(regex_dict[note_char_type[1]]).search(buffer)
                # 如果匹配到了
                if match2:
                    right_note_end = match2.end()
                    # 判断匹配到的区间中有几行
                    line_count = result[left_note_start:right_note_end].count('\n')
                    # 执行删除
                    result = result.replace(result[left_note_start:right_note_end], '\n' * line_count)
                    # 删除完毕之后进入下一次循环
                    buffer = result
                    continue
                # 如果没有匹配到，说明两者数量不匹配，报错
                else:
                    # 判断错误所在的行数
                    enter_location = list()
                    enter_location.append(0)
                    for i in range(0, len(result)):
                        if result[i] == '\n':
                            enter_location.append(i)
                    find = False

                    error_line = 0
                    for i in range(0, len(enter_location) - 1):
                        if enter_location[i] < left_note_start < enter_location[i + 1]:
                            error_line = i + 1
                            find = True
                            break
                    if not find:
                        error_line = len(enter_location)

                    # 报错
                    self.__error = LexicalError('/* 没有相匹配的 */', error_line)
                    #return False
                    with open('lexical_error.txt', 'a+') as f:
                        f.write('错误行数为:'+str(error_line )+'\t'+'错误原因:  '+ '/* 没有相匹配的 */  '  + '\n') 
                    buffer=''
                    self._flag=1
                    continue
            # 如果没有匹配到
            else:
                # 尝试寻找有没有落单的 */
                match2 = re.compile(regex_dict[note_char_type[1]]).search(buffer)
                # 如果找到了说明错误了
                if match2:
                    right_note_start = match2.start()
                    # 判断错误所在的行数
                    enter_location = list()
                    enter_location.append(0)
                    for i in range(0, len(result)):
                        if result[i] == '\n':
                            enter_location.append(i)
                    find = False

                    error_line = 0
                    for i in range(0, len(enter_location) - 1):
                        if enter_location[i] < right_note_start < enter_location[i + 1]:
                            error_line = i + 1
                            find = True
                            break
                    if not find:
                        error_line = len(enter_location)

                    # 报错
                    self.__error = LexicalError('多余的 */', error_line)
                    #return False
                    with open('lexical_error.txt', 'a+') as f:
                        f.write('错误行数为:'+'\t'+str(error_line )+'错误原因:  '+ '多余的 */  '  + '\n') 
                    buffer=''
                    self._flag=1
                    continue
                # 如果没有找到那就说明已经找完了，跳出
                else:
                    break

        # 将 result 保存到 __source 中
        self.__source = result
        return True

    def __split_lines(self):
        """
        将完成源代码分割成行序列
        """
        # 清空 __tokens
        self.__tokens.clear()
        # 按行分割
        temp = self.__source.split('\n')
        # 将分割出来的行序列添加到 __tokens 中
        for t in temp:
            self.__lines.append(' ' + t)

    def __split_tokens(self):
        """
        从行序列中分割出 token
        :return: 是否分割成功
        """
        # 先将 __lines 拷贝一份到临时变量中
        lines = list()
        for line in self.__lines:
            lines.append(line)
        # 缓冲区
        buffer = ''
        # 当前所在行数
        current_line_num = 0
        # 结果
        tokens = list()
        types=split_char_type+token_type

        while len(lines) > 0:
            # 当前循环中是否匹配成功
            match_this_time = False

            # 如果缓冲区中没有数据了，就填充一行到缓冲区
            if buffer == '':
                buffer = lines[0]
                lines = lines[1:]
                # 行号自增
                current_line_num += 1

            # 开始匹配
            # 尝试用所有的正则表达式来匹配
            for t in types:
                match = re.compile(regex_dict[t]).match(buffer)
                # 如果匹配到了
                if match:
                    # 将其添加到 tokens 中
                    tokens.append(Token(t, buffer[match.start():match.end()], current_line_num))
                    # buffer 去除已经匹配的部分
                    buffer = buffer[match.end():]
                    match_this_time = True
                    break
            # 如果匹配完所有的正则表达式都不成功
            if not match_this_time:
                # 报错
                self.__error = LexicalError('单词不符合词法', current_line_num,buffer)
                with open('lexical_error.txt', 'a+') as f:
                    f.write('错误行数为:'+str(current_line_num )+'\t' +'错误原因:  '+ '不符合词法'  '\t错误数据为:'+buffer+'\n') 
                # 返回失败
                #return False
                # 删除buffer中的数据
                buffer=''
                self._flag=1
                continue
                
        # 循环正常结束则说明完全匹配成功，将结果保存到 __tokens 中，返回成功
        for token in tokens:
            self.__tokens.append(token)
        return True

    def __del_spaces(self):
        """
        删除 __tokens 中的空格
        """
        # 新建临时变量
        tokens = list()
        # 将 __tokens 中的内容拷贝到 tokens 中
        for token in self.__tokens:
            tokens.append(token)
        # 清空 __tokens
        self.__tokens.clear()
        # 如果不是空格就添加进原来的 __tokens，相当于从原来的列表中去除了空格
        for token in tokens:
            if token.type != split_char_type[0]:
                self.__tokens.append(token)

if __name__ == '__main__':

    # 新建词法分析器
    lexical = Lexical()
    # 载入源代码
    lexical.load_source(open('3.txt',encoding="utf-8").read())
    # 执行词法分析
    lexical_success = lexical.execute()
    #将结果保存在tokens文件中
    with open('lexical_result.txt', 'w+') as f:
        lexical_result = lexical.get_result()
        for i in lexical_result:     
            f.write(i.type+ '\t' + i.str+ '\t' + str(i.line) +'\n')# 
    # 打印结果
    print('词法分析是否成功:\t', lexical_success)

    if lexical._flag:
        print('错误原因:\t', lexical.get_error().info,'\t错误数据为:\t',lexical.get_error().values,
              '\t错误行数为:\t',lexical.get_error().line)
    else:
        #lexical_result = lexical.get_result()
        print()
        print('词法分析结果:')
        for i in lexical_result:
            print(i.type, i.str, i.line)
            print()















