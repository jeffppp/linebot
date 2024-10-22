import os, random, traceback
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import googleSheet, googleplaapi

keyList = ['吃', '餓', 'ㄘ']

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
            
        if any(key in mes for key in keyList) > 0:
            # 如果local端沒有清單，就向google sheet取得
            if not os.path.isfile("foods.txt"):
                foods = googleSheet.getFoodList()
                file = open('foods.txt', 'w')
                for food in foods:
                    file.write(food[0] + "\n")
                file.close()
            # 取得食物清單
            file = open('foods.txt', 'r')
            foods = file.readlines()
            file.close()
            # 從清單中擇一回應
            m = random.randint(0, len(foods) - 1)
            return modifySTR(content, '吃'+foods[m].strip('\n'))

        #故意埋BUG測試錯誤回傳機制
        if mes == '滷肉飯滷肉飯':
            bug = int(mes)
            
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []
        
def getResponseLocation(content):
    try:
        location = str(content.message.latitude) + ", " + str(content.message.longitude)
        inform = ['name','vicinity','rating','opening_hours']
        nex = 0
        
        restaurants = googleplaapi.findplacenb(location, inform, nex, keyword = '')
        m = random.randint(0, len(restaurants) - 1)
        #持續找到現在有營業的店
        while not restaurants['opening_hours'][m]['open_now']:
            m = random.randint(0, len(restaurants) - 1)
        rest = "恐龍推薦\n" +\
            restaurants['name'][m] + "\n" +\
            "評價 " + str(restaurants['rating'][m]) + "\n" +\
            "地址 " + restaurants['vicinity'][m]
        return modifySTR(content, rest)
        
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []    
    
def modifySTR(content, response):
    if type(content) == str:
        return response
    else:
        return [TextMessage(text=response)]
        