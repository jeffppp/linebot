import os, random, traceback, re
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import database, googleSheet

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
            
        allQuizName = database.getAllQuizName()
                  
        #判斷quiz的名字和內容ID
        quizName = ''
        contentID = 1
        for name in allQuizName:
            if name == mes:
                quizName = name
                break
        else:
            splitMes = re.split('#', mes)
            if len(splitMes) != 2 : return []
            for name in allQuizName:
                if name == splitMes[0]: quizName = name; break
            else: return []
            if splitMes[1].isnumeric(): contentID = int(splitMes[1])
            else: return []
        #取得quiz內容並回傳
        quizContent = database.getQuiz(quizName, contentID)
        if len(quizContent) == 0: return []
        return getReplyQuizMessage(quizName, quizContent)
            
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
            
        allQuizName = database.getAllQuizName()
                  
        #判斷quiz的名字和內容ID
        quizName = ''
        contentID = 1
        for name in allQuizName:
            if name == mes:
                quizName = name
                break
        else:
            splitMes = re.split('#', mes)
            if len(splitMes) != 2 : return []
            for name in allQuizName:
                if name == splitMes[0]: quizName = name; break
            else: return []
            if splitMes[1].isnumeric(): contentID = int(splitMes[1])
            else: return []
        #取得quiz內容並回傳
        quizContent = database.getQuiz(quizName, contentID)
        if len(quizContent) == 0: return []
        return getReplyQuizMessage(quizName, quizContent)
            
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []

def getReplyQuizMessage(quizName, quizContent):
    #將type由小到大排列
    quizContent.sort(key=lambda e:sortDataType(e[1]))
    quizContentType = database.getDataType(quizContent[0][1])
    if quizContentType == 'text':
        if quizContent[0][2] == '': return [TextMessage(text=quizContent[0][3])]
        else: return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=quizContent[0][3],
                actions=[PostbackTemplateAction(
                    label='next',
                    data=quizName + '#' + str(quizContent[0][2]))]))]
    elif quizContentType == 'button_title':
        buttons = []
        for q in quizContent[1:]:
            buttons += [PostbackTemplateAction(
                label=q[3],
                data=quizName + '#' + str(q[2]))]
        return [TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                text=quizContent[0][3],
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
        