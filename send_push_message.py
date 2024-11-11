import random, traceback, os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
#import database, googleSheet
import re
import pygsheets
import time, datetime, pytz
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def getResponse(content, line_bot_api, sh):

    try:
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)

        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(
                content.source.room_id, content.source.user_id)

        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(
                content.source.group_id, content.source.user_id)

        
        
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
        learntxt = re.split('[,，]', mes)

        if learntxt[0] == '給我課程':
            ws = sh.worksheet_by_title('課程')
            headers = {
                "Authorization": "Bearer aJC2bjm4oW1IrcqXt2B83wWMJYt10ykHdrIe3xQCPdZHZog4QvCxWotOqcyk2gUz1EmXVylUWpIasRGg8yXjGXFIZDTmZK9VqDiQMFMfZgZy9JlM9PMMBoTwmsQGnhga94T7aEOfHcbSxCrYaiygNwdB04t89/1O/w1cDnyilFU=",
                "Content-Type": "application/json"
                }
            event_list=[]
            event_list6=[]
            message6=''
            message=''
            numbers_as_strings = list(map(str, range(1, 7+1)))
            keywords = ["自閉","情緒","過動","以家庭為中心","早期療育"]
            ws.cell((1,10)).set_value(", ".join(keywords))
            for i in numbers_as_strings:
                res = requests.get('https://www.beclass.com/default.php?name=ShowList&op=ShowRegist&od=&page='+i)
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find_all('tr')
                for row in rows:
                    # 提取<a>标签的信息
                    a_tag = row.find('a', class_='listlink')
                    if a_tag:
                        title = a_tag.get('title')
                        href = a_tag.get('href')
            
                        # 提取日期信息
                        date_span = row.find('span', style="color:#999999;")
                        if date_span:
                            date = date_span.get_text()
                            if title and href and any(keyword in title for keyword in keywords):
                                if(datetime.strptime(date,'(%Y-%m-%d)').weekday()==6):
                                    message6 = {'Title': title,'URL': href}
                                    event_list6.append(message6)
                                else:
                                    message = {'Title': title,'URL': href}
                                    event_list.append(message)
            ws.cell((2,10)).set_value("爬第一段成功")         
            keywords = ["學齡前","以家庭為中心","早期療育","發展遲緩","自閉症","ADHD","情緒","社交"]
            ws.cell((3,10)).set_value(", ".join(keywords))  
            for i in numbers_as_strings:
                
                res = requests.get('https://special.moe.gov.tw/study.php?&_p='+i)
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find_all('tr')
                ws.cell((4,10)).set_value(i) 
                for row in rows:
                    # 提取<a>标签的信息
                    a_tag = row.find('td', {'data-label': '研習日期'})
                    if a_tag:
                        date = a_tag.get_text()[0:10]
                        #print(date)
                        contentstr = row.select('td div a')
                        title = contentstr[0].get('title')
                        href = contentstr[0].get('href')
                        if title and href and any(keyword in title for keyword in keywords):
                            if(datetime.strptime(date,'%Y-%m-%d').weekday()==6):
                                ws.cell((6,10)).set_value(i) 
                                message6 = {'Title': title,'URL': 'https://special.moe.gov.tw/'+href}
                                event_list6.append(message6)
                            else:
                                ws.cell((7,10)).set_value(i) 
                                message = {'Title': title,'URL': 'https://special.moe.gov.tw/'+href}
                                event_list.append(message)
            ws.cell((8,10)).set_value(i) 
            numbers_as_strings5 = list(map(str, range(1, 4+1)))
            
            for i in numbers_as_strings5:
                res = requests.get('https://www.pmr.org.tw/active_news/active.asp?/'+i+'.html')
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, "html.parser")
                events = soup.find_all('ul')

                for event in events:
                    # 提取活动日期
                    date = event.find('li', class_='text-dateO')
                    if date:
                        date_text = date.get_text(strip=True).replace('日期：', '')

                        # 提取活动标题和链接
                        title_link = event.find('a')
                        if title_link:
                            title = title_link.get_text(strip=True)
                            href = title_link['href']
                            if title and href and any(keyword in title for keyword in keywords):
                                if(datetime.strptime(date_text,'%Y/%m/%d').weekday()==6):
                                    message6 = {'Title': title,'URL': 'https://www.pmr.org.tw/active_news/'+href}
                                    event_list6.append(message6)
                                else:
                                    message = {'Title': title,'URL': 'https://www.pmr.org.tw/active_news/'+href}
                                    event_list.append(message)

            
            
            nevent_list=[]
            nevent_list6=[]
            ws.cell((5,3)).set_value("爬第3段成功") 
            for c,event in enumerate(event_list):
                ws.cell((1,5)).set_value('=MATCH("'+event["Title"]+'",A:A,0)')
                ws.refresh()
                if(ws.cell((1,5)).value=='#N/A'):
                    ws.add_rows(1)
                    L=len(ws.get_col(1,include_tailing_empty=False))
                    ws.cell((L+1,1)).set_value(event["Title"])
                    ws.cell((L+1,2)).set_value(event["URL"])
                    nevent_list.append(event)
                
            for c,event in enumerate(event_list6):
                ws.cell((1,5)).set_value('=MATCH("'+event["Title"]+'",C:C,0)')
                ws.refresh()
                if(ws.cell((1,5)).value=='#N/A'):
                    ws.add_rows(1)
                    L=len(ws.get_col(3,include_tailing_empty=False))
                    ws.cell((L+1,3)).set_value(event["Title"])
                    ws.cell((L+1,4)).set_value(event["URL"])
                    nevent_list6.append(event)
            
            #麻token = 'jwHaTd1H8rqIKZBOKnD6intpw45ZZ2PkahfOn96Y5S7'
            #token = 'r3ZsARd1C95quZmEA1qN7IR4KGrcabaUOYq46AUFeox'
            if(False):
                data = {
                            "to": "Cd4c3c686c9a00e4878ff69c8eee0d96b",
                            'message': "\n其他時間的活動為:\n" + m    # 設定要發送的訊息
                        }
                response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
                #data = requests.post(url, headers=headers, data=data)
            else:
                count=0
                m6=''
                m=''
                for i in nevent_list6:
                    m6 = m6 + f'\nTitle: {i["Title"]}\nURL: {i["URL"]}\n'
                    count = count+1
                    if(count==6 or i ==nevent_list6[len(nevent_list6)-1]):
                        data = {
                            "to": "Cd4c3c686c9a00e4878ff69c8eee0d96b",
                            "messages": [
                                {
                                    "type": "text",
                                    "text": "\n星期天的活動為:\n" + m6    # 設定要發送的訊息
                                    }
                                ]
                            }
                        response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
                        #data = requests.post(url, headers=headers, data=data)
                        count=0
                        m6=''
                for i in nevent_list:
                    m = m + f'\nTitle: {i["Title"]}\nURL: {i["URL"]}\n'
                    count = count+1
                    if(count==6 or i ==nevent_list[len(nevent_list)-1]):
                        data = {
                            "to": "Cd4c3c686c9a00e4878ff69c8eee0d96b",
                            "messages": [
                                {
                                    "type": "text",
                                    "text": "\n其他時間的活動為:\n" + m    # 設定要發送的訊息
                                    }
                                ]
                            }

                        response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
                        #data = requests.post(url, headers=headers, data=data)
                        count=0
                        m=''        
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        ws = sh.worksheet_by_title('log')
        ws.add_rows(1)
        L=len(ws.get_col(1,include_tailing_empty=False))
        localtime = datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        ws.cell((L+1,1)).set_value(localtime)
        ws.cell((L+1,2)).set_value(error)

        #googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        ws = sh.worksheet_by_title('log')
        ws.add_rows(1)
        L=len(ws.get_col(1,include_tailing_empty=False))
        localtime = datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        ws.cell((L+1,1)).set_value(localtime)
        ws.cell((L+1,2)).set_value(error)
        #googleSheet.uploadException(error)
        return []


def getResponsePostback(content, line_bot_api):
    try:
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)

        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(
                content.source.room_id, content.source.user_id)

        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(
                content.source.group_id, content.source.user_id)

        if os.path.isfile(room_id + 'vote.txt'):
            string = re.split('[,，]', content.postback.data)
            num = string[1]
            vote = string[0]
            gameFile = open(room_id + 'vote.txt', 'a')
            gameFile.write(content.source.user_id + ',' + vote + ',' +
                           profile.display_name + ',' + "\n")
            gameFile.close()
        else:
            return [TextMessage(text="你來晚了，投票已過期了，滾~")]

        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return []


def modifySTR(content, response):
    if type(content) == str:
        return response
    else:
        return [TextMessage(text=response)]
