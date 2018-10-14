#!/usr/local/python3/bin/python3
import re,os
a={}
from functools import reduce
import time,datetime,sys
import geoip2.database
import pymysql
import shutil


mysql_host = '172.16.1.23'
mysql_user = 'root'
mysql_passwd = 'wkl123'
mysql_port = 3306
mysql_database = 'ueeshop-test'


def my_connect():
    global connection, con_cur
    try:
        connection = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_passwd,
                                     charset='utf8mb4', port=mysql_port, autocommit=True, database=mysql_database)
    except pymysql.err.MySQLError as err:
        print('Error: ' + str(err))
        exit(20)
    con_cur = connection.cursor()







def time_str(log_time):
    day = log_time.split()[0].split('/')[0]
    month = log_time.split()[0].split('/')[1]
    year = log_time.split()[0].split('/')[2].split(':')[0]
    format = '%d/%b/%Y:%H:%M:%S'
    Time = datetime.datetime.strptime(log_time.split()[0], format)
    month = Time.month
    timeArray = time.strptime(str(Time), "%Y-%m-%d %H:%M:%S")
    #print(Time)
    #print(timeArray)
    timeStamp = int(time.mktime(timeArray))
    return(Time,timeStamp,day,month,year)



def agent_str(agent):
    if  re.findall(r'(phone | pad | pod | iPhone | iPod | ios | iPad | Android | Mobile | BlackBerry | IEMobile | MQQBrowser | JUC | Fennec | wOSBrowser | BrowserNG | WebOS | Symbian |Phone |SAMSUNG)',agent):
        agent_d='mobile'
        if re.findall(r'(Googlebot|Baiduspider|AhrefsBot|YandexBot|python-requests|YisouSpider|bingbot|Sogou|SemrushBot|Go-http-client|MJ12bot|SurdotlyBot|ia_archiver|curl|Scrapy|LightspeedSystemsCrawler|MauiBot|MJ12bot|Python-urllib|pyspider|DotBot)',agent):
            agent_s='spider-mobile'
            agent_name = re.findall(r'(Googlebot|Baiduspider|AhrefsBot|YandexBot|python-requests|YisouSpider|bingbot|Sogou|SemrushBot|Go-http-client|MJ12bot|SurdotlyBot|ia_archiver|curl|Scrapy|LightspeedSystemsCrawler|MauiBot|MJ12bot|Python-urllib|pyspider|DotBot)',agent)[0]
        elif re.findall(r'(UCWEB)',agent):
            agent_name = 'ucbew'
            agent_s = 'm-web'
        elif re.findall(r'(Firefox)',agent):
            agent_name = 'Firefox'
            agent_s = 'm-web'
        elif re.findall(r'(Opera)',agent):
            agent_name = 'Opera'
            agent_s = 'm-web'
        elif re.findall(r'(MicroMessenger)', agent):
            agent_name = 'WeiXin'
            agent_s = 'm-web'
        elif re.findall(r'(AppleWebKi)', agent):

            if re.findall(r'(Mac OS)', agent):
                agent_name = 'Safari Uiwebview'
                agent_s = 'm-web'
            elif re.findall(r'(Android)', agent):
                agent_name='Android Webview'
                agent_s = 'm-web'
            else:
                agent_name='Android Webview'
                agent_s = 'm-web'

        elif re.findall(r'(Chrome)', agent):
            agent_name = 'Chrome'
            agent_s = 'm-web'
        else :
            agent_name = 'other'
            agent_s = 'm-web'
    else:
        agent_d = 'pc'
        if re.findall(r'(Googlebot|Baiduspider|AhrefsBot|YandexBot|python-requests|YisouSpider|bingbot|Sogou|SemrushBot|Go-http-client|MJ12bot|SurdotlyBot|ia_archiver|curl|Scrapy|LightspeedSystemsCrawler|MauiBot|MJ12bot|Python-urllib|pyspider|DotBot)',agent):
            agent_s='spider'
            agent_name = re.findall(r'(Googlebot|Baiduspider|AhrefsBot|YandexBot|python-requests|YisouSpider|bingbot|Sogou|SemrushBot|Go-http-client|MJ12bot|SurdotlyBot|ia_archiver|curl|Scrapy|LightspeedSystemsCrawler|MauiBot|MJ12bot|Python-urllib|pyspider|DotBot)',agent)[0]
        elif re.findall(r'(Firefox)',agent):
            agent_name='Firefox'
            agent_s='web'
        elif re.findall(r'(Chrome)',agent):
            agent_name='Chrom'
            agent_s='web'
        elif re.findall(r'(Safari)',agent):
            agent_name='Safari'
            agent_s = 'web'
        elif re.findall(r'(Trident)',agent):
            agent_name='IE'
            agent_s = 'web'
        elif re.findall(r'(OPR)',agent):
            agent_name='Opera'
            agent_s = 'web'
        elif re.findall(r'(Edge)',agent):
            agent_name='Edge'
            agent_s = 'web'
        else:
            agent_name='other'
            agent_s='web'
    return(agent_d,agent_s,agent_name)



agent_str('"Mozilla/5.0 (SAMSUNG; SAMSUNG-GT-S8600/S8600XXLD1; U; Bada/2.0; ru-ru) AppleWebKit/534.20 (KHTML, like Gecko) Dolfin/3.0 Mobile WVGA SMM-MMS/1.2.0 OPN-B"')


def ip_into_int(ip):
# 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
# (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))
def is_internal_ip(ip):
    ip = ip_into_int(ip)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    return ip >> 24 == net_a or ip >>20 == net_b or ip >> 16 == net_c


def get_url(request):
    #print(request)
    r_mothod=request.split()[0]
    r_url=request.split()[1]
    return r_mothod,r_url

def ip_city(ip):
    if is_internal_ip(ip):
        ip_counter='内网'
        return  ip_counter
    else:
        try:
            reader = geoip2.database.Reader('/opt/log/GeoLite2-City.mmdb')
            response = reader.city(ip)
            #print(response)
            ip_counter=response.country.names["zh-CN"]
            #print("地区:{}({})".format(response.continent.names["es"], response.continent.names["zh-CN"]))
            #print("国家:{}({}) ,简称:{}".format(response.counter.name, response.counter.names["zh-CN"], response.counter.iso_code))
            #print("城市:{}({})".format(response.counter.names["es"], response.continent.names["zh-CN"]))
            return(ip_counter)

        except:
            ip_counter='未知地址'
            return (ip_counter)


line_file=r'/opt/log/linenum.txt'
def get_line_num(file):
    with open(file, 'r', encoding='utf8') as f:
        line = f.readline()
        return(int(line))

import codecs
def write_line_num(linenum,f):
    with codecs.open(f, 'w', encoding='utf-8')as file:
        file.write(str(linenum))



def get_referer2(referer):
    # rez=r'(google|bing|baidu)'
    # serach=re.findall(rez, referer)
    # if  serach:
    #     try:
    #         req=r'/(www.)?(\w+(\.)?)+'
    #         req2=re.compile(req)
    #         a=re.search(req2,referer)
    #         referer=a.group()
    #         return referer
    #     except Exception as e:
    #         referer='Unknow'
    #         return referer
    if  re.findall(r'(oinom|ueeshop|!google)',referer):
         referer='local'
         referer_s='local'
         return referer,referer_s
    else:
        try:
            req=r'/(www.)?(\w+(-)?(\.)?)+'
            req2=re.compile(req)
            a=re.search(req2,referer)
            b=a.group()
            print('-----------------------------')
            referer=b.split('/')[1]
            print(referer)
            if re.findall(r'(bing|baidu|google|yandex|sogou.com|so.com)',referer):
                referer_s= 'search'
            elif re.findall(r'(netcraft.com|facebook|twitter|linkedIn|pinterest|tumblr|instagram.com|flickr|mySpace|tagged|meetup|ask.fm|meetme|classmates|snapchat)',referer):
                referer_s='social'
            elif re.findall(r'(webkaka|updownchecker)',referer):
                referer_s='social'
            else:
                referer_s='other'
            return referer,referer_s
        except Exception as e:
            referer='oother'
            referer_s='other'
            return referer,referer_s


def get_referer(referer):

    if referer == 'blank' or referer == '':
        referer='none'
        referer_s='none'
        return referer,referer_s

    else:
        if referer == '-':
            referer = 'url'
            referer_s='url'
            return referer,referer_s
        else:
            referer,referer_s=get_referer2(referer)
            return referer,referer_s


with open('/var/log/nginx/ueeshop-test/ueeshop-test-access.log') as f:
        for count, b in enumerate(f,1):
            line_num=get_line_num(line_file)
            if int(count) > line_num:
                print(count)
                log_pattern = r'^(?P<remote_addr>.*?) - - \[(?P<time_local>.*?)\] "(?P<request>.*?)" (?P<status>.*?) (?P<body_bytes_sent>.*?) "(?P<http_referer>.*?)" "(?P<http_user_agent>.*?)"'
                #log_pattern = r'^(?P<remote_addr>.*?) - - \[(?P<time_local>.*?)\] "(?P<request>.*?)" (?P<status>.*?) (?P<body_bytes_sent>.*?) (?P<request_time>.*?) "(?P<http_referer>.*?)" "(?P<http_user_agent>.*?)" - (?P<http_x_forwarded_for>.*)$'
                log_pattern_obj = re.compile(log_pattern)
                remote=(log_pattern_obj.search(b).group('remote_addr'))
                request=(log_pattern_obj.search(b).group('request'))
                log_time=(log_pattern_obj.search(b).group('time_local'))
                status=(log_pattern_obj.search(b).group('status'))
                agent=(log_pattern_obj.search(b).group('http_user_agent'))
                bytes=(log_pattern_obj.search(b).group('body_bytes_sent'))
                referer=(log_pattern_obj.search(b).group('http_referer'))
                ip_counter=ip_city(remote)
                referer_str,referer_s=get_referer(referer)
                #if  referer_str != 'local' and  status != str(404):
                r_mothod, r_url=get_url(request)
                if  status == str(200) and r_mothod == str('GET'):
                    #url_pattern=r'^/manage/'
                    #url_obj=re.compile(url_pattern)
                    #manage_re=re.match(url_obj,r_url)
                    if not re.findall(r'(/manage/|/?check_login_status)',r_url):                  
                    	Time,timeStamp, day, month, year=time_str(log_time)
                    	#print(Time,timeStamp,day,month,year)
                    	agent_d, agent_s, agent_name=agent_str(agent)
                   	# r_mothod, r_url=get_url(request)
                    	print( timeStamp,Time,day,month,year,status,bytes,remote,r_mothod,r_url,referer,ip_counter,referer_str)
                    	connection = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_passwd,
                                                 charset='utf8', port=mysql_port, autocommit=True, database=mysql_database)
                    	con_cur = connection.cursor()
                    	insert_sql = 'insert into acc_log (server,Time,timeStamp,count,day,month,year,status,bytes,remote,r_mothod,r_url,referer,referer_str,referer_s,agent_d,agent_s,agent_name,counter) values ("%s","%s","%s","%s",%s,%s,%s,%s,%s,"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' %("oinom",Time,timeStamp,count,day,month,year,status,bytes,remote,r_mothod,r_url,referer,referer_str,referer_s,agent_d,agent,agent_name,ip_counter)
                    	print(insert_sql)
                    	con_cur.execute(insert_sql)

a= write_line_num(count,line_file)
#







