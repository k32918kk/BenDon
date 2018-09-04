
# coding: utf-8

# In[1]:


#!pip install selenium
#!pip install webdriver_manager
#!pip install beautifulsoup4
#!pip install hanziconv
#!pip install SpeechRecognition
#!pip install gTTS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager

from collections import defaultdict
#from hanziconv import HanziConv

from pygame import mixer
from gtts import gTTS

import time 
import random
import jieba
import re
import requests

import speech_recognition as sr
import tempfile
import re
import urllib3
import json

import urllib.parse, urllib.request
import hashlib
import base64

mixer.init()


# In[2]:


Gstring = '我要一份排骨飯兩個雞腿飯三個煎魚飯四個五穀飯'
Xstring = '我要一份排骨饭，两个鸡腿饭，三个监狱饭，四个五谷饭。'
Xlist = Xstring.replace('。','').split('，')
print(Xlist)
start = 0
end = len(Xlist[0])
sentence = []
for i in Xlist:
    end = start + len(i)
    sentence.append(Gstring[start:end])
    start = end
r = '，'.join(sentence)
print(r)


# In[3]:


#定義將字串轉語音的方法
def speak(sentence):
    """
    args:
          sentence<str> text to speak
    return:
          
    """ 
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=sentence, lang='zh-TW')
        tts.save("{}.mp3".format(fp.name))
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play()

def listen():
    try:
        Gresponse = ''
        Gresponse = rrr.recognize_google(audio, language='zh-TW')
        print("Google thinks what you say:" + Gresponse)

        f = open("Audio_.wav", 'rb')
        file_content = f.read()
        base64_audio = base64.b64encode(file_content)
        body = urllib.parse.urlencode({'audio': base64_audio})
        url = 'http://api.xfyun.cn/v1/service/v1/iat'
        api_key = 'd71a6745b5344d25d3d11bdaf9bbd948'
        param = {"engine_type": "sms16k", "aue": "raw"}
        x_appid = '5b742cf2'
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
        x_time = int(int(round(time.time() * 1000)) / 1000)
        x_checksum_content = api_key + str(x_time) + str(x_param, 'utf-8')
        x_checksum = hashlib.md5(x_checksum_content.encode('utf-8')).hexdigest()
        x_header = {'X-Appid': x_appid,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}

        req = urllib.request.Request(url = url, data = body.encode('utf-8'), headers = x_header, method = 'POST')

        result = urllib.request.urlopen(req)
        result = result.read().decode('utf-8', 'ignore')

        Xresponse = result.split('data":"')[1].split('","')[0]

        #simple to traditional
        #answer = HanziConv.toTraditional(result_text)
        #print('xfyun thinks what you say(traditional):', answer)
        Xresponse = Xresponse.replace('。','').split('，')
        print('xfyun thinks what you say(simple):', Xresponse)
        start = 0
        end = len(Xresponse[0])
        sentence = []
        for i in Xresponse:
            end = start + len(i)
            sentence.append(Gresponse[start:end])
            start = end
        r = '，'.join(sentence)
        return r
    
    except sr.UnknownValueError:
        print("could not understand audio")
    except sr.RequestError as e:
        print("Error raise; {0}".format(e))
    except:
        print(result.split('desc":"')[1].split('","')[0])

def storeName():
    request_url = 'http://113.196.59.103/MirleOrderingAPI/api/Schedule/today'
    store_name = requests.get(request_url)
    result = store_name.json()['categoryName']
    #print(result)
    speak('今天吃' + result)


# In[4]:


# constants for chinese_to_arabic
CN_NUM = {
    '〇' : 0, '一' : 1, '二' : 2, '三' : 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9, '零' : 0,
    '壹' : 1, '貳' : 2, '參' : 3, '肆' : 4, '伍' : 5, '陸' : 6, '柒' : 7, '捌' : 8, '玖' : 9, '貮' : 2, '兩' : 2,
}

CN_UNIT = {
    '十' : 10,
    '拾' : 10,
    '百' : 100,
    '佰' : 100,
    '千' : 1000,
    '仟' : 1000,
    '万' : 10000,
    '萬' : 10000,
    '亿' : 100000000,
    '億' : 100000000,
    '兆' : 1000000000000,
}

def chinese_to_arabic(cn:str) -> int:
    unit = 0   # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val

def fuzzyfinder(user_input, collection):
    suggestions = []
    pattern = '.*?'.join(user_input)	# Converts ‘djm‘ to ‘d.*?j.*?m‘
    regex = re.compile(pattern)		 # Compiles a regex.
    for item in collection:
        match = regex.search(item)	  # Checks if the current item matches the regex.
        if match:
            suggestions.append((len(match.group()), match.start(), item))
    return [x for _, _, x in sorted(suggestions)]


# In[5]:


# %load AppDynamicsJob.py

class AppDynamicsJob():
    
    def __init__(self, dictionary):
        self.dictionary = dictionary
    
    def setUp(self):
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
        #self.driver = webdriver.Chrome('C:/Users/Calvin/python_code/chromedriver.exe')
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        
    def MMOrder(self):
        driver = self.driver
        driver.get("http://113.196.59.103/MirleOrderingWeb")
        driver.find_element_by_link_text(u"登入").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Remember me'])[1]/following::button[1]").click()
        dictionary = self.dictionary
        if dictionary['排骨飯'] != 0:
            #訂排骨
            driver.find_element_by_link_text(u"訂購").click()
            for i in range(0, dictionary['排骨飯'] - 1):
                #排骨飯增加1
                driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='排骨'])[1]/following::i[1]").click()
            
        if dictionary['五穀飯'] != 0:
            #訂五穀
            driver.find_element_by_xpath(u"(//a[contains(text(),'訂購')])[4]").click()
            for i in range(0, dictionary['五穀飯'] - 1):
                #五穀+1
                driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='五穀'])[1]/following::button[1]").click()
                
        if dictionary['雞腿飯'] != 0:
            #訂雞腿飯
            driver.find_element_by_xpath(u"(//a[contains(text(),'訂購')])[2]").click()
            for i in range(0, dictionary['雞腿飯'] - 1):
                #雞腿飯增加1
                driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='雞腿'])[1]/following::i[1]").click()
                
        if dictionary['煎魚飯'] != 0:
            #訂煎魚飯
            driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='便當'])[1]/preceding::a[2]").click()
            for i in range(0, dictionary['煎魚飯'] - 1):
                #煎魚飯增加1
                driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='煎魚'])[1]/following::button[1]").click()
        
    def confirm(self):
        #確認總金額
        driver = self.driver
        dictionary = self.dictionary
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='總金額 ${}'])[1]/following::button[1]".format(dictionary['總價'])).click()
        return 'done'
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)


# In[6]:


def FillForm(response, **kwargs):
    #初始化填單dictionary
    MM_information_table = defaultdict(int)

    FuzzyCollection = []
    for i in kwargs.keys():
        #將品項能被截巴正確斷出
        jieba.suggest_freq(i, True)
        #設定模糊比對的collection
        FuzzyCollection.append(i)
        if '飯' in i:
            jieba.suggest_freq(i.split('飯')[0], True)
        if '麵' in i:
            jieba.suggest_freq(i.split('麵')[0], True)
    #print('FuzzyCollection is:', FuzzyCollection)
    #依據逗號拆解句子
    if response != None:
        global response_list
        if '，' in response:
            response_list = response.split('，')
        else:
            response_list = [response]

    seg = []
    for i in response_list:
        seg.append(jieba.lcut(i, cut_all=False))

    for sentence in seg:
        #print('sentence is:', sentence)
        for word in sentence:
            #print('word is:', word)
            options = fuzzyfinder(word, FuzzyCollection)
            #print('options is:', options)
            if len(options) > 1:
                optionString = '還是'.join(options)
                speak('您是要' + optionString)
            for item in kwargs.keys():
                if len(options) == 1 and options[0] == item:
                    for i, s in enumerate(sentence):
                        if '份' in s or '個' in s: 
                            mount = chinese_to_arabic(sentence[i][0])
                            MM_information_table[item] += mount
    
    accumulation = 0
    for k, v in kwargs.items():
        price_sum = lambda x: x*MM_information_table[k] if MM_information_table[k] else 0
        accumulation += price_sum(v)

    MM_information_table['總價'] = accumulation
    
    print(seg)
    print(MM_information_table)
    return MM_information_table


# In[ ]:


while True:
    rrr = sr.Recognizer()
    rrr.energy_threshold = 5000
    with sr.Microphone(sample_rate = 16000, chunk_size = 1024) as source:
        rrr.adjust_for_ambient_noise(source, duration=0.5)
        audio = rrr.listen(source, phrase_time_limit=60)
        with open("Audio_.wav", "wb") as f:
            try: 
                f.write(audio.get_wav_data())
                if '吃貨' in listen():
                    speak('沒問題')
                    time.sleep(0.4)
                    storeName()
                    time.sleep(2)
                    speak('想吃些甚麼呢')
                    while True:
                        rrr = sr.Recognizer()
                        rrr.energy_threshold = 5000
                        with sr.Microphone(sample_rate = 16000, chunk_size = 1024) as source:
                            rrr.adjust_for_ambient_noise(source, duration=0.5)
                            print("點餐嚕！")
                            audio = rrr.listen(source, phrase_time_limit=60)
                            #write audio to a WAV file
                            with open("Audio_.wav", "wb") as a:
                                a.write(audio.get_wav_data())
                                response = listen() #return response(str)
                                print(response)
                                info_table = None
                                info_table = FillForm(response, 排骨飯=60, 雞腿飯=65, 煎魚飯=55, 五穀飯=50)
                                #small change
                                if info_table != None:
                                    order = AppDynamicsJob(info_table)
                                    order.setUp()
                                    order.MMOrder()
                                    order_status = order.confirm()
                                    speak('請幫我確認一下訂單內容喔')
                                    time.sleep(2.5)
                                    if order_status == 'done':
                                        speak('有任何需要幫忙的地方再找我喔')
                                        break
            except NoSuchElementException:
                print('please confirm your order')
            
            except TypeError:
                print('TypeError raise, say that again')

