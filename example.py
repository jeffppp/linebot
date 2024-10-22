import os, random
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

def sample_rwtext(word):
    #讀寫檔案範例#####################################################
    #寫  
    messagesFile = open('messages.txt', 'a')
    messagesFile.write(word + "\n")
    messagesFile.close()
    #讀
    messagesFile = open('messages.txt', 'r')
    messages = messagesFile.readlines()
    messagesFile.close()
        
    #整理
    allMes = ""
    for s in messages:
        allMes += s
            
    if word.find('#') >= 0:
        return allMes
    ##################################################################
