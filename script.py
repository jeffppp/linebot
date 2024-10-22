import os, random, traceback, re
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import database, googleSheet

keyQuiz = '玩心理測驗'
keyStory = '聽故事'

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
        
        #心理測驗和故事的觸發詞
        if mes == keyQuiz:
            names = database.getAllScriptName(database.getScriptTypeID('Quiz'))
            actions = []
            for name in names:
                actions += [PostbackTemplateAction(
                    label=name[1],
                    data='Script#' + str(name[0]) + "#1")]
            return [TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    text='有好多好玩的測驗你挑一個',
                    actions=actions))]
        elif mes == keyStory:
            names = database.getAllScriptName(database.getScriptTypeID('Story'))
            actions = []
            for name in names:
                actions += [PostbackTemplateAction(
                    label=name[1],
                    data='Script#' + str(name[0]) + "#1")]
            return [TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    text='來選一個想聽的故事八~',
                    actions=actions))]
                        
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
            
        splitMes = re.split('#', mes)
        if not splitMes[0] == 'Script': return []
        if not splitMes[1].isnumeric(): return []
        if not splitMes[2].isnumeric(): return []
        #分解資訊
        scriptID = int(splitMes[1])
        lineID = int(splitMes[2])
        more = False
        if len(splitMes) == 4 and splitMes[3] == 'more':
            more = True
            
        #根據劇本型態導向對應func
        scriptTypeID = database.getScriptName(scriptID)[0]
        scriptType = database.getScriptType(scriptTypeID)
        if scriptType == 'Story':
            return getReplyStoryMessage(scriptID, lineID, more)    
        elif scriptType == 'Quiz':
            return getReplyQuizMessage(scriptID, lineID)
        
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []

def getReplyQuizMessage(scriptID, lineID):
    content = database.getScript(scriptID, lineID)
    #將type由小到大排列
    content.sort(key=lambda e:sortDataType(e[2]))
    contentType = database.getDataType(content[0][2])
    if contentType == 'text':
        if content[0][3] == '': return [TextMessage(text=content[0][4])]
        else: return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=content[0][4],
                actions=[PostbackTemplateAction(
                    label='next',
                    data='Script#' + str(scriptID) + "#" + str(content[0][3]))]))]
    elif contentType == 'button_title':
        buttons = []
        for q in content[1:]:
            buttons += [PostbackTemplateAction(
                label=q[4],
                data='Script#' + str(scriptID) + "#" + str(q[3]))]
        return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=content[0][4],
                actions=buttons))]
    else: return []

def getReplyStoryMessage(scriptID, lineID, more):
    content = database.getScript(scriptID, lineID)
    # 將type由小到大排列
    content.sort(key=lambda e:sortDataType(e[2]))
    contentType = database.getDataType(content[0][2])
    if contentType == 'text':
        if content[0][3] == '': return [TextMessage(text=content[0][4])]
        else: 
            if not more:
                return [TemplateSendMessage(
                    alt_text='Buttons Template',
                    template=ButtonsTemplate(
                        text=content[0][4],
                        actions=[
                            PostbackTemplateAction(
                                label='下一行',
                                data='Script#' + str(scriptID) + "#" + str(content[0][3]))
                            ,PostbackTemplateAction(
                                label='翻頁',
                                data='Script#' + str(scriptID) + "#" + str(content[0][3]) + "#more")]))]
            else:
                reply = [TextMessage(text=content[0][4])]
                for i in range(3):
                    content = database.getScript(scriptID, content[0][3])
                    content.sort(key=lambda e:e[2])
                    contentType = database.getDataType(content[0][2])
                    if contentType == 'text': reply += [TextMessage(text=content[0][4])]
                    else: break
                    if content[0][3] == '': break
                if content[0][3] != '':
                    reply += [TemplateSendMessage(
                        alt_text='Buttons Template',
                        template=ButtonsTemplate(
                            text='...',
                            actions=[
                                PostbackTemplateAction(
                                    label='下一行',
                                    data='Script#' + str(scriptID) + "#" + str(content[0][3]))
                                ,PostbackTemplateAction(
                                    label='翻頁',
                                    data='Script#' + str(scriptID) + "#" + str(content[0][3]) + "#more")]))]
                return reply
    elif contentType == 'button_title':
        buttons = []
        for q in content[1:]:
            buttons += [PostbackTemplateAction(
                label=q[4],
                data='Script#' + str(scriptID) + "#" + str(q[3]))]
        return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=content[0][4],
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
        