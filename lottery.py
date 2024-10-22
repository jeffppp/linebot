import random, traceback
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

def getResponse(content):
    try:
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
            
        if mes == '給我樂透':
            buttons_template = TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    title='Pick a Game',
                    text='Select a game',
                    actions=[
                        MessageTemplateAction(
                            label='大樂透',
                            text='不負責任的大樂透'
                            ),
                        MessageTemplateAction(
                            label='威力彩',
                            text='不負責任的威力彩'
                            ),
                        MessageTemplateAction(
                            label='限10個的Bingo Bingo',
                            text='不負責任的Bingo'
                            ),
                        MessageTemplateAction(
                            label='今彩539',
                            text='不負責任的539',
                            )
                        ]
                    )
                )
            return [buttons_template]
        if mes == '不負責任的大樂透':
            data = random.sample(range(1,50), 6)
            return [TextMessage(text=str(data))]
        if mes == '不負責任的威力彩':
            data = random.sample(range(1,39), 6)
            data2 = random.sample(range(1,9), 1)
            return [TextMessage(text=str(data) + str(data2))]
        if mes == '不負責任的Bingo':
            data = random.sample(range(1,81), 10)
            return [TextMessage(text=str(data))]
        if mes == '不負責任的539':
            data = random.sample(range(1,40), 5)
            return [TextMessage(text=str(data))]
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        return modifySTR(content, error)
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        return modifySTR(content, error)
        
def modifySTR(content, response):
    if type(content) == str:
        return response
    else:
        return [TextMessage(text=response)]
