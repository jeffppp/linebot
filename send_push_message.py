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
        if(learntxt[0]=="給我星期天課程"):
            event6={}
            nevent_list6=[]
            ws = sh.worksheet_by_title('不重複課程')
            L=len(ws.get_col(3,include_tailing_empty=False))
            for i in range(1,L+1):
                event6["Title"] = ws.cell((i,1)).value
                event6["URL"] = ws.cell((i,2)).value
                nevent_list6.append(event6)
            m6=''
            count=0
            for i in nevent_list6:
                m6 = m6 + f'\nTitle: {i["Title"]}\nURL: {i["URL"]}\n'
            if(len(m6)==0):
                m6="目前星期天沒課程"
            line_bot_api.reply_message(content.reply_token, TextMessage(text=m6))

        if(learntxt[0]=="給我其他時間課程"):
            event={}
            nevent_list=[]
            ws = sh.worksheet_by_title('不重複課程')
            L=len(ws.get_col(1,include_tailing_empty=False))
            for i in range(1,L+1):
                
                event["Title"] = ws.cell((i,1)).value
                event["URL"] = ws.cell((i,2)).value
                nevent_list.append(event)
            m=''
            count=0
            for i in nevent_list:
                m = m + f'\nTitle: {i["Title"]}\nURL: {i["URL"]}\n'
            if(len(m)==0):
                m6="目前其他時間沒課程"
            line_bot_api.reply_message(content.reply_token, TextMessage(text=m))
             
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
