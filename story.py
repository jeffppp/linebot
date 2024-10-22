import os, random, traceback, re
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import database, googleSheet

keyList = ['故事', 'story']

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
            
        allStoryName = database.getAllStoryName()
        
        #判斷story的名字和內容ID
        storyName = ''
        contentID = 1
        more = False
        for name in allStoryName:
            if name == mes:
                storyName = name
                break
        else:
            splitMes = re.split('#', mes)
            if len(splitMes) != 2 : return []
            for name in allStoryName:
                if name == splitMes[0]: storyName = name; break
            else: return []
            if '*' in splitMes[1]: 
                more = True
                splitMes[1] = splitMes[1].replace('*', '')
            if splitMes[1].isnumeric(): contentID = int(splitMes[1])
            else: return []
        #取得story內容並回傳
        storyContent = database.getStory(storyName, contentID)
        if len(storyContent) == 0: return []
        return getReplyStoryMessage(storyName, storyContent, more)
            
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []

def getResponsePostback(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.postback.data
            
        allStoryName = database.getAllStoryName()
        
        #判斷story的名字和內容ID
        storyName = ''
        contentID = 1
        more = False
        for name in allStoryName:
            if name == mes:
                storyName = name
                break
        else:
            splitMes = re.split('#', mes)
            if len(splitMes) != 2 : return []
            for name in allStoryName:
                if name == splitMes[0]: storyName = name; break
            else: return []
            if '*' in splitMes[1]: 
                more = True
                splitMes[1] = splitMes[1].replace('*', '')
            if splitMes[1].isnumeric(): contentID = int(splitMes[1])
            else: return []
        #取得story內容並回傳
        storyContent = database.getStory(storyName, contentID)
        if len(storyContent) == 0: return []
        return getReplyStoryMessage(storyName, storyContent, more)
        
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []

def getReplyStoryMessage(storyName, storyContent, more):
    #將type由小到大排列
    storyContent.sort(key=lambda e:sortDataType(e[1]))
    storyContentType = database.getDataType(storyContent[0][1])
    if storyContentType == 'text':
        if storyContent[0][2] == '': return [TextMessage(text=storyContent[0][3])]
        else: 
            if not more:
                return [TemplateSendMessage(
                    alt_text='Buttons Template',
                    template=ButtonsTemplate(
                        text=storyContent[0][3],
                        actions=[
                            PostbackTemplateAction(
                                label='下一行',
                                data=storyName + '#' + str(storyContent[0][2]))
                            ,PostbackTemplateAction(
                                label='翻頁',
                                data=storyName + '#' + str(storyContent[0][2]) + "*")]))]
            else:
                reply = [TextMessage(text=storyContent[0][3])]
                for i in range(3):
                    storyContent = database.getStory(storyName, storyContent[0][2])
                    storyContent.sort(key=lambda e:e[1])
                    storyContentType = database.getDataType(storyContent[0][1])
                    if storyContentType == 'text': reply += [TextMessage(text=storyContent[0][3])]
                    else: break
                    if storyContent[0][2] == '': break
                if storyContent[0][2] != '':
                    reply += [TemplateSendMessage(
                        alt_text='Buttons Template',
                        template=ButtonsTemplate(
                            text='...',
                            actions=[
                                PostbackTemplateAction(
                                    label='下一行',
                                    data=storyName + '#' + str(storyContent[0][2]))
                                ,PostbackTemplateAction(
                                    label='翻頁',
                                    data=storyName + '#' + str(storyContent[0][2]) + "*")]))]
                return reply
    elif storyContentType == 'button_title':
        buttons = []
        for q in storyContent[1:]:
            buttons += [PostbackTemplateAction(
                label=q[3],
                data=storyName + '#' + str(q[2]))]
        return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=storyContent[0][3],
                actions=buttons))]
    else: return []

def modifySTR(content, response):
    if type(content) == str:
        return response
    else:
        return [TextMessage(text=response)]

def sortDataType(index):
    '''
    Used to sort the data of datatype from database.
    e.g. 1 -> -1  20 -> -2  21 -> -1.9  22 -> -1.8 
    '''
    import math
    digit = math.pow(10,len(str(index))-1)
    head = -index / digit
    body = index % digit
    return head + body