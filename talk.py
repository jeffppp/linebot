import random, traceback, math
import database, googleSheet
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
        
        isDbExist = database.checkTables(['Dialog', 'Synonym'])
        if not(isDbExist[0] and isDbExist[1]): return []
        value = database.getKeywordValues(mes)
        if len(value) == 0 : 
            return []
        else:
            value.sort(key=lambda e:sortDataType(e[0]))
            contentType = database.getDataType(value[0][0])
            if contentType == 'text':
                m = random.randint(0, len(value) - 1)
                return modifySTR(content, value[m][1])
            elif contentType == 'button_title':
                buttons = []
                for v in value[1:]:
                    if not math.floor(v[0] / 10) == 2: break
                    contentType = database.getDataType(v[0])
                    if contentType == "button_item":
                        buttons += [MessageTemplateAction(
                            label=v[1],
                            text=v[1])]
                    elif contentType == "button_location":
                        buttons += [URIAction(
                            label=v[1],
                            uri='line://nv/location')]
                return [TemplateSendMessage(
                    alt_text='Buttons Template',
                    template=ButtonsTemplate(
                        text=value[0][1],
                        actions=buttons))]
            else: return []
            
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

def sortDataType(index):
    import math
    digit = math.pow(10,len(str(index))-1)
    head = -index / digit
    body = index % digit
    return head + body