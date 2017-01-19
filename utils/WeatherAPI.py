# -*- coding: UTF-8 -*- 
'''
utils.WeatherAPI is a part of the project bangu.
bangu is an open-source project which follows MVC design pattern mainly based on python.

Copyright (C) 2014 - 2017, Vlon Jang(WeChat:wangqingbaidu)
Institute of Computing Technology, Chinese Academy of Sciences, Beijing, China.

The codes are mainly developed by Zhiwei Zhang.
As an open-source project, your can use or modify it as you want.

Contact Info: you can send an email to 564326047@qq.com(Vlon) 
  or visit my website www.wangqingbaidu.cn

Note: Please keep the above information whenever or wherever the codes are used.
'''
from datetime import datetime
import urllib2
from bs4 import BeautifulSoup
from utils.obj2dict import obj2dict

class weather:
    __attrs_map = {'humidity':'湿度:',
                   'temperature':'温度:',
                   'wind':'风力:',
                   'condition':'天气:',
                   'pm25':'pm25:',
                   'pm25_desc':'空气质量:',
                   'tmp_max':'最高气温:',
                   'tmp_min':'最低气温:'}
    humidity = None
    temperature = None
    wind = None
    condition = None
    pm25 = None
    pm25_desc = None
    
    tmp_max = None
    tmp_min = None
    
    def __init__(self, t = None, h = None, w = None, c = None, p = None, pd = None, tmax = None, tmin = None):
        self.temperature = t
        self.humidity = h
        self.wind = w
        self.condition = c
        self.pm25 = p
        self.pm25_desc = pd
        self.tmp_max = tmax
        self.tmp_min = tmin
        
    def __str__(self):
        attrs_dict = obj2dict(self)
        attrs_list = ['{key}{value}'.format(key=self.__attrs_map[k],
                                            value=attrs_dict[k].encode('utf8'))
                      for k in attrs_dict if attrs_dict[k]]
          
        return '\t'.join(sorted(attrs_list))

        
class WeatherAPI:
    urlmap = {'moji':'http://tianqi.moji.com/'}
    last_update = None
    suggestion = None
    now = weather()
    forecast = []
    month = []
    
    def __init__(self, api_type='moji', debug=False):
        self.type = api_type
        self.debug = debug
        if self.urlmap.has_key(api_type):
            self.content = urllib2.urlopen(self.urlmap[api_type]).read()
        else:
            raise Exception("API type not found! Now tianqi.moji.com api supports only.")
        self.__parser_content()
        
    def refresh(self):
        try:
            self.content = urllib2.urlopen(self.urlmap[self.api_type]).read()
            self.last_update = datetime.now()
        except:
            raise Exception('Web connection error.')
        
    def __parser_content(self):
        soup = BeautifulSoup(self.content, 'html5lib')
        now_block = soup.select('div[class="wrap clearfix wea_info"]')
        forecast_block = soup.select('div[class="forecast clearfix"]')
        month_block = soup.find_all(attrs={'class':"grid clearfix",'id':"calendar_grid"})
        
        self.suggestion = soup.select(
            'meta[name="description"]')[0]['content'].replace('墨迹天气'.decode('utf8'),'Bangu')
        if self.debug:
            print self.suggestion
        self.__parser_now_block(now_block[0])
        self.__parser_forecast_block(forecast_block[0])
        self.__parser_month_block(month_block[0])

    def __parser_now_block(self, now_block=None):
        s = now_block.select('div[class="left"] div[class="wea_alert clearfix"] ul li a em')[0].string.split()
        self.now.pm25 = s[0]
        self.now.pm25_desc = s[1]
        self.now.temperature = now_block.select(
            'div[class="left"] div[class="wea_weather clearfix"] em')[0].string + '℃'.decode('utf8')
        self.now.condition = now_block.select(
            'div[class="left"] div[class="wea_weather clearfix"] b')[0].string
        
        self.now.humidity = now_block.select(
            'div[class="left"] div[class="wea_about clearfix"] span')[0].string.split()[-1]
        self.now.wind = now_block.select(
            'div[class="left"] div[class="wea_about clearfix"] em')[0].string
        if self.debug:
            print self.now
        
    def __parser_forecast_block(self, forecast_block = None):
        days = forecast_block.find_all(class_="days clearfix")
        for d in days:
            w = weather()
            item = d.select('li')
            w.condition = item[1].get_text().lstrip()
            w.tmp_min = item[2].string.split()[0][:-1] + '℃'.decode('utf8')
            w.tmp_max = item[2].string.split()[-1][:-1] + '℃'.decode('utf8')
            w.wind = item[3].em.string + item[3].b.string 
            w.pm25 = item[4].strong.string.split()[0]
            w.pm25_desc = item[4].strong.string.split()[-1]
            self.forecast.append(w)
            if self.debug:
                print w
                
    def __parser_month_block(self, month_block = None):
        days = month_block.select('ul li')
        for d in days:
            w = weather()
            try:
                w.condition = d.img['alt']
                w.tmp_min = str(int(d.p.string.split('/')[0])) + '℃'.decode('utf8')
                w.tmp_max = str(int(d.p.string.split('/')[1][:-1])) + '℃'.decode('utf8')
                self.month.append(w)
                if self.debug:
                    print w
            except:
                pass
        
if __name__ == '__main__':
    w = WeatherAPI(debug=True, api_type='moji')
    