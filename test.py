
def main():

    with open("LL(1).txt", encoding='UTF-8') as f:
        # 去掉最后的 '\n'
        # print(f.readline())
        ter_list = f.readline()[:-1].split('\t')
        # print(ter_list)
        dic = dict()
        for line in f.readlines():
            line_list = line[:-1].split('\t')
            line_dic = dict()
            for index, rule in enumerate(line_list):
                if rule != '' and index != 0:
                    line_dic[ter_list[index]] = rule
            dic[line_list[0]] = line_dic
        print(dic)
        return dic

main()