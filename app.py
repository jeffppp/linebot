from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import re, tempfile
from imgurpython import ImgurClient
import schedule, time
import random, traceback
import game, lottery
import talk, script, eat
import json
from datetime import datetime
import sys
import pygsheets
import os
import pytz

app = Flask(__name__)

creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDS"))
with open('creds.json', 'w') as json_file:
    json.dump(creds_json, json_file, indent=4)  # indent 用於美化格式
    
gc = pygsheets.authorize(service_account_file="creds.json")
survey_url = 'https://https://docs.google.com/spreadsheets/d/1ijhJM1adyzYj6YBnv0wD37-cy69NKubpP1LXhQgtHDY/edit?gid=0#gid=0'
sh = gc.open_by_url(survey_url)


#import database, googleSheet
'''
# Channel Access Token
line_bot_api = LineBotApi('N6auYEaF/2FjOkvLUGPZk31wz8HvrxRSv0dRnDYvlh8vV+JwZJVOdh/2Y10LWlBY5u/lSaRKy1FfEcFwKShMson03Te60PiUpWmAUEB/fNnWHAwDZrCzlp6JV+6b1sArj8kL/b52vDHXT/3KXlthqAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('b5f09601f13baf753a08b025c318f5c2')
'''
#ma_bot
# Channel Access Token
line_bot_api = LineBotApi(
    'aJC2bjm4oW1IrcqXt2B83wWMJYt10ykHdrIe3xQCPdZHZog4QvCxWotOqcyk2gUz1EmXVylUWpIasRGg8yXjGXFIZDTmZK9VqDiQMFMfZgZy9JlM9PMMBoTwmsQGnhga94T7aEOfHcbSxCrYaiygNwdB04t89/1O/w1cDnyilFU='
)
# Channel Secret
handler = WebhookHandler('b601eca685bf17acd4cea1d40415822e')

# imgur key
client_id = 'fa56d6b6417a3a4'
client_secret = '40a9335c64c2e50749927978663103e3a9cbd0f9'
album_id = 'DkD9rDb'
access_token = '5dc739693a8e98feccaebbb68084003c2e0cc280'
refresh_token = '663b65e5cc94cc3126b488cec5cde02510b97ae5'

static_tmp_path = '.'


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理Postback
@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        replyMessageList = []
        if len(replyMessageList) == 0:
            replyMessageList += script.getResponsePostback(event)
        if len(replyMessageList) == 0:
            replyMessageList += game.getResponsePostback(event, line_bot_api)
        if len(replyMessageList) != 0:
            #print(replyMessageList)
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        ws = sh.worksheet_by_title('聊天室資料')
        ws.cell((1,10)).set_value('=MATCH("'+room_id+'",A:A,0)')
        ws.refresh()
        if(ws.cell((1,10)).value=='#N/A'):
            ws.add_rows(1)
            L=len(ws.get_col(1,include_tailing_empty=False))
            ws.cell((L+1,1)).set_value(room_id)
            ws.cell((L+1,2)).set_value(profile.display_name)
            message = TextSendMessage(text="已記錄視窗ID")
            line_bot_api.push_message(room_id, message)
        else:
            members = ws.cell((int(ws.cell((1,10)).value),2)).value.split(", ")
            if(profile.display_name not in members):
                members.append(profile.display_name)
                members = list(set(members))
                members_string = ", ".join(members)
                message = TextSendMessage(text="已記錄你的暱稱")
                line_bot_api.push_message(room_id, message)
                ws.cell((int(ws.cell((1,10)).value),2)).set_value(members_string)
        

        replyMessageList = []

        #if len(replyMessageList) == 0:
        #    replyMessageList += eat.getResponse(event)
        #if len(replyMessageList) == 0:
        #    replyMessageList += script.getResponse(event)
        if len(replyMessageList) == 0:
            #print(replyMessageList)
            replyMessageList += game.getResponse(event, line_bot_api)
            #print(replyMessageList)
        if len(replyMessageList) == 0:
            replyMessageList += lottery.getResponse(event)
        #if len(replyMessageList) == 0:
        #    replyMessageList += talk.getResponse(event)
        if len(replyMessageList) != 0:
            #print(replyMessageList)
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        line_bot_api.reply_message(event.reply_token,
                                   TextMessage(text="error1"))
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        line_bot_api.reply_message(event.reply_token,
                                   TextMessage(text="error2"))
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    try:
        # replymes = 'Type:' + str(event.message.type)
        # replymes += '\nId:' + str(event.message.id)
        # replymes += '\nTitle:' + str(event.message.title)
        # replymes += '\nAddress:\n' + str(event.message.address)
        # replymes += '\nLatitude:' + str(event.message.latitude)
        # replymes += '\nLongitude:' + str(event.message.longitude)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

        replyMessageList = []

        if len(replyMessageList) == 0:
            replyMessageList += eat.getResponseLocation(event)
        if len(replyMessageList) != 0:
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\npackage_id:' + str(event.message.package_id)
        replymes += '\nsticker_id:\n' + str(event.message.sticker_id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        message_content = line_bot_api.get_message_content(event.message.id)

        ### ma
        '''
        ext = 'jpg'
        with tempfile.NamedTemporaryFile(dir=static_tmp_path,
                                         prefix=ext + '-',
                                         delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        try:
            client = ImgurClient(client_id, client_secret, access_token,
                                 refresh_token)
            config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': 'Cute kitten being cute on '
            }
            path = os.path.join('.', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='上傳成功'))
        except:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='上傳失敗'))
        return 0
        '''
        #line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nDuration:' + str(event.message.duration)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nDuration:' + str(event.message.duration)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nfile_size:' + str(event.message.file_size)
        replymes += '\nfile_name:' + str(event.message.file_name)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
