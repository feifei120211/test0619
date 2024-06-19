import jieba
import requests
import streamlit as st
from streamlit_echarts import st_echarts
from collections import Counter
from streamlit.logger import get_logger
import re
import string
import pandas as pd
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt

LOGGER = get_logger(__name__)

# 定义数据清洗函数
def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace(' ', '')
    text = text.strip()
    return text

# 定义分词函数
def segment(text):
    stopwords = ['的', '了', '在', '是', '我', '你', '他', '她', '对','它', '们', '人','这', '仅','那', '之', '与', '和', '或','等','虽然','大','更','多', '但是', '然而', '因此','条','年']
    punctuation = "、，。！？；：　“”‘’~@#￥%……&*（）【】｛｝+-*/=《》<>「」『』【】〔〕｟｠«»“”‘’'':;,/\\|[]{}()$^↑"
    text = text.translate(str.maketrans("", "", punctuation)).replace('\n', '')
    words = jieba.lcut(text)
    words = [word for word in words if word not in stopwords]
    return words

# Removing punctuation, numbers
def remove_punctuation(text):
  punctuation = string.punctuation
  text = text.translate(str.maketrans('', '', punctuation))  
  return re.sub('\d+', '', text)

def extract_body_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find('body').get_text()
    return text

def generate_wordcloud(text):
    wordcloud = WordCloud(font_path='simhei.ttf',  # 设置字体路径，确保支持中文
                          width=800, height=400,
                          background_color='white').generate(text)
    return wordcloud

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="",
    )
    st.write("# 文本内容分析系统 ")
    url = st.text_input('输入你需要分析的网址:')
    if url:
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        text =extract_body_text(text)
        text = remove_punctuation(text)
        text = clean_text(text)
        words = segment(text)
        word_counts = Counter(words)
        # 打印最高词频的词，以检查是否被正确识别
        most_common_word, most_common_count = word_counts.most_common(1)[0]
        st.write(f"The most common word is '{most_common_word}' with a count of {most_common_count}")
        top_words = word_counts.most_common(20)
        wordcloud_options = {
          "tooltip": {
            "trigger": 'item',
            "formatter": '{b} : {c}'
          },
          "xAxis": [{
            "type": "category", 
            "data": [word for word, count in top_words],
            "axisLabel": {
              "interval": 0, 
              "rotate": 30
            }
          }],
          "yAxis": [{"type": "value"}],
          "series": [{
            "type": "bar",
            "data": [count for word, count in top_words]
          }]
        }
    
        st_echarts(wordcloud_options, height='500px')
        # 添加词频排名表格
        df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
        st.write(df)
        # 生成词云
        wordcloud = generate_wordcloud(' '.join(words))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)
if __name__ == "__main__":
    run()
