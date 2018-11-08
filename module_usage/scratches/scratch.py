# -*- encoding: utf-8 -*-
'''
Created on 2018年10月19日

@author: houguangdong
'''

import re
import jieba
import pandas as p
import numpy
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
file1 = open("D:\\comm1.txt", 'r')
xt = file1.read()
pattern = re.compile(r'[\u4e00-\u9fa5]+')
filedata = re.findall(pattern, xt)
xx = ''.join(filedata)
file1.close()
# 读写文件
file2 = open("D:\\comm2.txt", 'r+')
file2.write(xx)
# 清洗数据
clear = jieba.lcut(xx)
cleared = p.DataFrame({'clear': clear})
# print(clear)
stopwords = p.read_csv("chineseStopWords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'], encoding='gbk')
cleared = cleared[~cleared.clear.isin(stopwords.stopword)]
# print(std)
count_words = cleared.groupby(by=['clear'])['clear'].agg({"num": numpy.size})
count_words = count_words.reset_index().sort_values(by=["num"], ascending=False)
# print(count_words)
# 词云展示
wordcloud = WordCloud(font_path="simhei.ttf", background_color="white", max_font_size=250, width=1300,
                      height=800)  # 指定字体类型、字体大小和字体颜色
word_frequence = {x[0]: x[1] for x in count_words.head(200).values}
wordcloud = wordcloud.fit_words(word_frequence)
plt.imshow(wordcloud)
plt.axis("off")
plt.colorbar()
plt.show()

# wctext = open('E:\\pachong1\\comm1.txt', 'r')
print("finish")
