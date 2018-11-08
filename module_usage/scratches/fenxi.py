# -*- encoding: utf-8 -*-
'''
Created on 2018年10月19日

@author: houguangdong
'''

import jieba
from scipy.misc import imread
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

def readDocument():
    text = open("./pachong1/comm1.txt", "rb").read()
    return text


def segment(doc):
    seg_list = " ".join(jieba.cut(doc, cut_all=False))  # seg_list为str类型
    document_after_segment = open('分词结果.txt', 'w+')
    document_after_segment.write(str(seg_list))
    document_after_segment.close()
    return seg_list

def wordCount(segment_list):
    word_list = []
    word_dict = {}
    with open('./去停用词的词频统计.txt','w') as xr:
        word_list.append(segment_list.split(' '))
        #print(word_list)
        for item in word_list:
            for item2 in item:
                if item2 not in word_dict:
                    word_dict[item2] = 1
                else:
                    word_dict[item2] += 1
        print(word_dict)
        #print(dict(zip(word_dict_sorted)))
        #print(type(word_dict_sorted))
        #for (K, V) in sorted(word_dict_sorted.items(), key=lambda x: x[1]):
            #print(K, '=>', V)
        l = len(word_dict)
        count = 0
        out = open('./词频统计.txt','w')
        for (K, V) in sorted(word_dict.items(), key=lambda x: x[1], reverse=True):
            out.write(K+' '+str(V)+'\n')
            count += 1
            if count >= l/2:
                break
        out.close()
    xr.close()

def drawWordCloud(seg_list):
    '''
    制作词云
    设置词云参数
    '''
    color_mask = imread("./satimg.jpg") # 读取背景图片,注意路径
    wc = WordCloud(
        # 设置字体，不指定就会出现乱码，注意字体路径
        font_path = "./simheittf.ttf",
        #font_path=path.join(d,'simsun.ttc'),
        #设置背景色
        background_color = 'white',
        stopwords = [u"哈哈哈"],
        mask = color_mask,
        # 允许最大词汇
        max_words = 2000,
        # 最大号字体
        max_font_size = 60
    )
    print seg_list, '11111111'
    wc.generate(seg_list)       # 产生词云
    image_colors = ImageColorGenerator(color_mask)
    wc.to_file("doubanpl.jpg")  # 保存图片
    # 显示词云图片
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    plt.figure()
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    plt.show()

def removeStopWords(seg_list):
    wordlist_stopwords_removed = []
    stop_words = open('./chineseStopWords.txt')    # 需要下载停用词表
    stop_words_text = stop_words.read()
    stop_words.close()
    stop_words_text_list = stop_words_text.split('\n')
    after_seg_text_list = seg_list.split(' ')
    for word in after_seg_text_list:
        if word not in stop_words_text_list:
            wordlist_stopwords_removed.append(word)
    without_stopwords = open('./去停用词的分词结果.txt', 'w')
    without_stopwords.write(' '.join(wordlist_stopwords_removed))
    return ' '.join(wordlist_stopwords_removed)

if __name__ == "__main__":
    doc = readDocument()
    segment_list = segment(doc)
    segment_list_remove_stopwords = removeStopWords(segment_list)
    drawWordCloud(segment_list_remove_stopwords)
    wordCount(segment_list_remove_stopwords)