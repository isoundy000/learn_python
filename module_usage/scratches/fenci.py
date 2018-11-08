# -*- encoding: utf-8 -*-
'''
Created on 2018年10月19日

@author: houguangdong
'''

import jieba

seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
print("Full Mode:", "/ ".join(seg_list))                # 全模式

seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
print ("Default Mode:", "/ ".join(seg_list))            # 精确模式

seg_list = jieba.cut("他来到了网易杭研大厦")               # 默认是精确模式
print (", ".join(seg_list))

seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")   # 搜索引擎模式
print (", ".join(seg_list))

# 获取词性
import jieba.posseg as psg
# 每个词都有其词性，比如名词、动词、代词等，结巴分词的结果也可以带上每个词的词性，要用到jieba.posseg
s = u'我想和女朋友一起去北京故宫博物院参观和闲逛。'
print [(x.word, x.flag) for x in psg.cut(s)]
# 可以看到成功获取到每个词的词性，这对于我们对分词结果做进一步处理很有帮助，比如只想获取分词结果列表中的名词，那么就可以这样过滤：
print [(x.word, x.flag) for x in psg.cut(s) if x.flag.startswith('n')]
# 并行分词
# 开启并行分词模式，参数为并发执行的进程数
jieba.enable_parallel(5)
# 关闭并行分词模式
jieba.disable_parallel()

# 举例：开启并行分词模式对三体全集文本进行分词
santi_text = open('./santi.txt').read()
print len(santi_text)
# 可以看到三体全集的数据量还是非常大的，有260多万字节的长度。
jieba.enable_parallel(100)
santi_words = [x for x in jieba.cut(santi_text) if len(x) >= 2]
jieba.disable_parallel()

# 获取出现频率Top n的词
# 还是以上面的三体全集文本为例，假如想要获取分词结果中出现频率前20的词列表，可以这样获取：
from collections import Counter
c = Counter(santi_words).most_common(20)
print c
# 可以看到结果中'\r\n'居然是出现频率最高的词，还有'一个'、'没有'、'这个'等这种我们并不想要的无实际意义的词，那么就可以根据前面说的词性来进行过滤，这个以后细讲。

# 使用用户字典提高分词准确性
# 不使用用户字典的分词结果：
txt = u'欧阳建国是创新办主任也是欢聚时代公司云计算方面的专家'
print ','.join(jieba.cut(txt))
# 使用用户字典的分词结果：
jieba.load_userdict('user_dict.txt')
print ','.join(jieba.cut(txt))
# 可以看出使用用户字典后分词准确性大大提高。
# 注：其中user_dict.txt的内容如下：
# 欧阳建国 5
# 创新办 5 i
# 欢聚时代 5
# 云计算 5
# 用户字典每行一个词，格式为：
# 词语 词频 词性
# 其中词频是一个数字，词性为自定义的词性，要注意的是词频数字和空格都要是半角的。