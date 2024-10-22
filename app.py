from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import re, tempfile
from imgurpython import ImgurClient

app = Flask(__name__)

import random, traceback
import game, lottery

import talk, script, eat
import database, googleSheet
'''
# Channel Access Token
line_bot_api = LineBotApi('N6auYEaF/2FjOkvLUGPZk31wz8HvrxRSv0dRnDYvlh8vV+JwZJVOdh/2Y10LWlBY5u/lSaRKy1FfEcFwKShMson03Te60PiUpWmAUEB/fNnWHAwDZrCzlp6JV+6b1sArj8kL/b52vDHXT/3KXlthqAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('b5f09601f13baf753a08b025c318f5c2')
'''
#ma_bot
# Channel Access Token
line_bot_api = LineBotApi('aJC2bjm4oW1IrcqXt2B83wWMJYt10ykHdrIe3xQCPdZHZog4QvCxWotOqcyk2gUz1EmXVylUWpIasRGg8yXjGXFIZDTmZK9VqDiQMFMfZgZy9JlM9PMMBoTwmsQGnhga94T7aEOfHcbSxCrYaiygNwdB04t89/1O/w1cDnyilFU=')
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
            replyMessageList += game.getResponsePostback(event,line_bot_api)
        if len(replyMessageList) != 0:
            line_bot_api.reply_message(event.reply_token, replyMessageList) 
    
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        #讀取資料庫狀態
        dbStatusFile = open('dbStatus', 'r')
        dbStatusTxt = dbStatusFile.readlines()[-1]
        dbStatusFile.close()
        import re
        split = re.split('/', dbStatusTxt)
        dbStatus = {'new':split[0] == 'True', 'updating':split[1] == 'True'}
        
        #如果是初始狀態
        if dbStatus['new']:
            #修改資料庫狀態True/True
            dbStatusFile = open('dbStatus', 'a')
            dbStatusFile.write('\nTrue/True')
            dbStatusFile.close()
            #回覆訊息'忙線'
            line_bot_api.reply_message(event.reply_token
               , TextMessage(text="dbStatusFile")) 
            #如果是非更新中
            if not dbStatus['updating']:
                #更新資料庫
                database.updateTablesAll()
                #修改資料庫狀態False/False
                dbStatusFile = open('dbStatus', 'a')
                dbStatusFile.write('\nFalse/False')
                dbStatusFile.close()
                #直接結束
                return
            #如果是更新中
            else:
                #直接結束
                return
        
        replyMessageList = []
        
        if len(replyMessageList) == 0:
            replyMessageList += eat.getResponse(event)
        if len(replyMessageList) == 0:
            replyMessageList += script.getResponse(event)
        if len(replyMessageList) == 0:
            replyMessageList += game.getResponse(event,line_bot_api)
        if len(replyMessageList) == 0:
            replyMessageList += lottery.getResponse(event)
        if len(replyMessageList) == 0:
            replyMessageList += talk.getResponse(event)
        if len(replyMessageList) != 0:
            line_bot_api.reply_message(event.reply_token, replyMessageList) 
            
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
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
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
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
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return
    
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:        
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        message_content = line_bot_api.get_message_content(event.message.id)
        
        ### ma
        ext = 'jpg'
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        try:
            client = ImgurClient(client_id, client_secret, access_token, refresh_token)
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
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳成功'))
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳失敗'))
        return 0
        
        #line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))
        
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
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
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
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
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
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
        googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return
                
    
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
