from lexical import Lexical
from semantic2 import Pro
from syntax import  Parser
from vm import VM
import os


def main():
    # 新建词法分析器
    lexical = Lexical()

    # 载入源代码
    lexical.load_source(open('3.txt', encoding="utf-8").read())

    # 执行词法分析
    lexical_success = lexical.execute()

    # 将结果保存在tokens文件中
    with open('lexical_result.txt', 'w+') as f:
        lexical_result = lexical.get_result()
        for i in lexical_result:
            f.write(i.type + '\t' + i.str + '\t' + str(i.line) + '\n')

    # 打印结果
    print('词法分析是否成功:\t', lexical_success)
    if lexical_success:
        # lexical_result = lexical.get_result()
        print()
        print('词法分析结果:')
        for i in lexical_result:
            print(i.type, i.str, i.line)
        print()
    else:
        print('错误原因:\t', lexical.get_error().info)

    # 语法分析
    parser = Parser()

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

                _flag = False
            table.append(list(parser.pretable[key1].values()))

    else:
        print("\33[不是LL1文法")

    # 保存ll(1)预测表
    if os.path.exists('LL(1).txt'):
        os.remove('LL(1).txt')
    with open("LL(1).txt", 'a+') as f:
        f.write("\t")
        for i in list(parser.pretable.keys()):
            f.write(str(i) + "\t")
        f.write("\n")
        for i in range(0, len(table[0])):
            for array in table:
                if str(array[i]) == "error":
                    f.write("\t")
                else:
                    f.write(str(array[i]) + "\t")
            f.write("\n")

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

    p = Pro()

    # input str 标识符 map-lsit 字符 map-line 行数
    p.createSymbolList(input_str, map_list, map_line)
    # 语义分析得到chart 符号表 temp_list 临时变量表 seq_list四元式表
    p.analysis('LL(1).txt')  # 生成的的ll1规则表LL(1)

if __name__ == '__main__':
    main()

