import random, traceback, os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import database, googleSheet
import re

def getResponse(content,line_bot_api):
    

    try:
        check_game = ['剪刀', '石頭', '布']
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)
            
        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(content.source.room_id,content.source.user_id)
            
        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(content.source.group_id,content.source.user_id)


        
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text

        learntxt = re.split('[,，]',mes)

        if learntxt[0]=='恐龍學說話':
            database.addDialog([[learntxt[1],1,learntxt[2]]])
            return [TextMessage(text="我學會囉")]

        
        if learntxt[0]=='我要開票':
            if os.path.isfile(room_id+'vote.txt'):
                gameFile = open(room_id + 'vote.txt', 'r')
                tmp = gameFile.readlines()
                gameFile.close()
                oristr = re.split('[,，]',tmp[0])
                if tmp[0][0:32] == content.source.user_id[0:32]:
                    ID=['0']
                    Item =['0']
                    Name = ['0']
                    for s in reversed(tmp[1:]):
                        string = re.split('[,，]',s)
                        if string[0] != ID[-1]:
                            ID.append(string[0])
                            Item.append(string[1])
                            Name.append(string[2])
                    allMes = ''
                    if oristr[5] != '1':
                        for N in range(1,len(Name)):
                            allMes = allMes + Name[N] + '投了' + Item[N] + '一票' + '\n'
                        allMes = allMes + '\n'
                    for Itemcount in oristr[1:-2]:
                        allMes = allMes + Itemcount + '共' + str(Item.count(Itemcount)) + '票' + '\n'
                                  
                    os.remove(room_id + 'vote.txt')
                    return [TextMessage(text=allMes)]
                else:
                    return [TextMessage(text="你有辦投票嗎??")]
            else:
                return [TextMessage(text="你有辦投票嗎?")]

        elif learntxt[0]=='我要辦投票' and len(learntxt)==7:
            gameFile = open(room_id + 'vote.txt', 'w')
            gameFile.write(content.source.user_id+','+learntxt[1]+','+learntxt[2]+','+learntxt[3]+','+learntxt[4]+','+learntxt[5]+','+'\n')
            gameFile.close()
            if learntxt[5] == '0':
                anon = '非匿名投票'
            else:
                anon = '匿名投票'
                
            buttons_template = TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    title=anon,
                    text=learntxt[6],
                    actions=[
                        PostbackTemplateAction(
                            label=learntxt[1],
                            text= '已投票',
                            data= learntxt[1]+',1,'+learntxt[5]
                        ),
                        PostbackTemplateAction(
                            label=learntxt[2],
                            text= '已投票',
                            data= learntxt[2]+',2,'+learntxt[5]
                        ),
                        PostbackTemplateAction(
                            label=learntxt[3],
                            text= '已投票',
                            data= learntxt[3]+',3,'+learntxt[5]
                        ),                    
                        PostbackTemplateAction(
                            label=learntxt[4],
                            text= '已投票',
                            data= learntxt[4]+',4,'+learntxt[5],
                            )
                        ]
                    )
                )
            

            return [buttons_template]


        if database.checkUserID(content.source.user_id)==0:
            database.createUser(content.source.user_id, profile.display_name)
        
        if mes == '玩遊戲':
            
            buttons_template = TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    title='Pick a Game',
                    text='Select a game to play with members',
                    actions=[
                        MessageTemplateAction(
                            label='猜數字',
                            text='我要玩猜數字'
                        ),
                        MessageTemplateAction(
                            label='終極密碼',
                            text='我要玩終極密碼'
                        ),
                        MessageTemplateAction(
                            label='比大小',
                            text='來比大小啦'
                        ),                    
                        MessageTemplateAction(
                            label='猜拳',
                            text= '來猜拳',
                            )
                        ]
                    )
                )
            return [buttons_template]
        
        elif mes=='我要玩終極密碼' :
            ans1 = random.randint(0,99999)
            numa=2
            gameFile = open(room_id + 'gameans.txt', 'w')
            gameFile.write(room_id + "\n")
            gameFile.write(str(ans1) + "\n")
            gameFile.write(str(2) + "\n")
            gameFile.write(str(1) + "\n")
            gameFile.write(str(99999) + "\n")
            gameFile.close()
            return [TextMessage(text="請輸入1~99999")]
        elif mes=='我要玩猜數字' :
            allnum=range(0,10)
            ans2 = random.sample(allnum, 5)
            numa=1
            gameFile = open(room_id + 'gameans.txt', 'w')
            gameFile.write(room_id + "\n")
            gameFile.write(str(ans2) + "\n")
            gameFile.write(str(1) + "\n")
            gameFile.close()
            gameFile = open(room_id + 'gamerecord.txt', 'w')
            gameFile.write('')
            gameFile.close()
            gameFile = open(room_id + 'gameans.txt', 'r')
            tmp = gameFile.readlines()
            gameFile.close()
            return [TextMessage(text="請輸入五位數")]
                
        elif mes=='來比大小啦' :
            gameFile = open(room_id + 'gameans.txt', 'w')
            gameFile.write(room_id + "\n")
            gameFile.write(str(12345) + "\n")
            gameFile.write(str(3) + "\n")
            gameFile.close()
            return [TextMessage(text="你先出，我再來決定要比大還比小")]
        elif mes == '來猜拳':
            buttons_template = TemplateSendMessage(
                alt_text='Buttons Template',
                template=ButtonsTemplate(
                    title='你要出甚麼',
                    text='輸了不要哭',
                    #thumbnail_image_url='',
                    actions=[
                        MessageTemplateAction(
                            label='剪刀',
                            text='剪刀'
                        ),
                        MessageTemplateAction(
                            label='石頭',
                            text='石頭'
                        ),
                        MessageTemplateAction(
                            label='布',
                            text='布'
                        )
                    ]
                )
            )
            return [buttons_template]
        elif any(mes in s for s in check_game):
            bb=check_game[random.randint(0, 2)]
            if bb==mes:
                bb = bb + '\n平手再來一次'
            elif bb=='剪刀' and mes =='布':
                bb = bb + '\n你輸惹\n小廢物哈哈哈哈'
            elif bb=='剪刀' and mes =='石頭':
                bb = bb + '\n你贏惹\nQAQ'
                database.updateUserScore(content.source.user_id, profile.display_name,1)
            elif bb=='布' and mes =='石頭':
                bb = bb + '\n你輸惹\n小廢物哈哈哈哈'
            elif bb=='布' and mes =='剪刀':
                bb = bb + '\n你贏惹\nQAQ'
                database.updateUserScore(content.source.user_id, profile.display_name,1)
            elif bb=='石頭' and mes =='剪刀':
                bb = bb + '\n你輸惹\n小廢物哈哈哈哈'
            elif bb=='石頭' and mes =='布':
                bb = bb + '\n你贏惹\nQAQ'
                database.updateUserScore(content.source.user_id, profile.display_name,1)
            #userdata = database.getUserStatus(content.source.user_id)
            return [TextMessage(text=bb)]  #+':'+str(userdata[0][1])+'共'+str(userdata[0][2]))]
        elif mes == '!level!':
            userdata = database.getUserStatus(content.source.user_id)
            if len(userdata)!=0:
                return [TextMessage(text= userdata[0][1] +'目前'+str(userdata[0][2])+'分'+',等級為'+str(userdata[0][3])+'級')]
            else:
                return []
            
        elif mes == '!猜數字作弊!':
            gameFile = open(room_id + 'gameans.txt', 'r')
            tmp = gameFile.readlines()
            gameFile.close()
            if eval(tmp[2])==1:
                ansc = random.randint(0,4)
                database.updateUserScore(content.source.user_id, profile.display_name,-5)
                userdata = database.getUserStatus(content.source.user_id)
                ans2 = eval(tmp[1])
                return [TextMessage(text= userdata[0][1]+'作弊扣5分,剩下'+str(userdata[0][2])+'分，獲得第'+str(ansc+1)+'個數字為'+str(ans2[ansc]))]
            else:
                return []
        elif mes == '!record!':
            gameFile = open(room_id + 'gamerecord.txt', 'r')
            tmp = gameFile.readlines()
            gameFile.close()
            allMes = ""
            for s in tmp:
                allMes += s       
            return [TextMessage(text=allMes)]
        elif os.path.exists(room_id + 'gameans.txt'):
            
            gameFile = open(room_id + 'gameans.txt', 'r')
            tmp = gameFile.readlines()
            gameFile.close()
            
            if eval(tmp[2])==1 and mes.isdigit():
                ans2 = eval(tmp[1])
                b=list(map(int,list(mes)))
                if len(b)==5:
                    c = [ans2[i] - b[i] for i in range(len(ans2))]
                    numa = c.count(0)
                    d = set(ans2) & set(b)
                    numb = len(d)-numa
                    if numa==5:
                        gameFile = open(room_id + 'gameans.txt', 'w')
                        gameFile.write(room_id + "\n")
                        gameFile.write(str(0) + "\n")
                        gameFile.write(str(0) + "\n")
                        gameFile.write(str(0) + "\n")
                        gameFile.close()
                        gameFile = open(room_id + 'gamerecord.txt', 'w')
                        gameFile.write('')
                        gameFile.close()
                        
                        gameFile = open(room_id + 'gamerecord.txt', 'r')
                        tmp = gameFile.readlines()
                        gameFile.close()
                        allMes = ""
                        for s in tmp:
                            allMes += s
                        if (len(allMes)/15)<=6:
                            score = 10*2
                        elif (len(allMes)/15)<=12:
                            score = 10
                        else:
                            score = 5

                        database.updateUserScore(content.source.user_id, profile.display_name,score)
                        return [TextMessage(text='結束囉，獲勝者得'+str(score)+'分')]
                        
                    else:
                        if len(set(b))<5:
                            return [TextMessage(text='不要想作弊!!')]
                        else:
                            gameFile = open(room_id + 'gamerecord.txt', 'a')
                            gameFile.write(mes  +"_____"+  str(numa)+'A'+str(numb)+'B'  + "\n")
                            gameFile.close()
                            return [TextMessage(text=str(numa)+'A'+str(numb)+'B')]
                            
                else:
                    return [TextMessage(text='傻了嘛! 請打五個數字')]
                    
            elif eval(tmp[2])==2 and mes.isdigit():
                startnum = eval(tmp[3])
                endnum = eval(tmp[4])
                ans1 = eval(tmp[1])
                a=int(mes)
                if a>ans1 and a<endnum and a>startnum:
                    gameFile = open(room_id + 'gameans.txt', 'w')
                    gameFile.write(room_id + "\n")
                    gameFile.write(str(ans1) + "\n")
                    gameFile.write(str(2) + "\n")
                    gameFile.write(str(startnum) + "\n")
                    gameFile.write(str(a) + "\n")
                    gameFile.close()
                    return [TextMessage(text=str(startnum)+' to '+str(a))]
                    
                elif a<ans1 and a<endnum and a>startnum:
                    gameFile = open(room_id + 'gameans.txt', 'w')
                    gameFile.write(room_id + "\n")
                    gameFile.write(str(ans1) + "\n")
                    gameFile.write(str(2) + "\n")
                    gameFile.write(str(a) + "\n")
                    gameFile.write(str(endnum) + "\n")
                    gameFile.close()
                    return [TextMessage(text=str(a)+' to '+str(endnum))]
                    
                elif a==ans1:
                    gameFile = open(room_id + 'gameans.txt', 'w')
                    gameFile.write(str(0) + "\n")
                    gameFile.write(str(0) + "\n")
                    gameFile.write(str(0) + "\n")
                    gameFile.close()
                    database.updateUserScore(content.source.user_id, profile.display_name,1)
                    return [TextMessage(text='恭喜你得分!繼續努力')]
                    
                else:
                    return [TextMessage(text='超出範圍啦~~~傻B')]
                    
            elif eval(tmp[2])==3 and mes.isdigit():
                i=int(mes)
                bs = ['比大', '比小']
                n=random.randint(1, 10**len(mes))
                m = random.randint(0, 1)
                if n==i:
                    aa = bs[m] + ', ' + str(n) + '\n剛剛好一樣哈哈哈哈'
                elif m==0 and n>i:
                    aa = bs[m] + ', ' + str(n) + '\n你輸惹小廢物'
                elif m==1 and n<i:
                    aa = bs[m] + ', ' + str(n) + '\n你輸惹小費物'
                else:
                    aa = bs[m] + ', ' + str(n) + '\n你贏惹QAQ，得一分'
                    database.updateUserScore(content.source.user_id, profile.display_name,1)
                gameFile = open(room_id + 'gameans.txt', 'w')
                gameFile.write(str(0) + "\n")
                gameFile.write(str(0) + "\n")
                gameFile.write(str(0) + "\n")
                gameFile.close()
                return [TextMessage(text=aa)]
            else:
                return []
                 
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        googleSheet.uploadException(error)
        return []

def getResponsePostback(content,line_bot_api):
    try:
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)
                
        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(content.source.room_id,content.source.user_id)
                
        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(content.source.group_id,content.source.user_id)
    
        if os.path.isfile(room_id+'vote.txt'):
            string = re.split('[,，]',content.postback.data)
            num = string[1]
            vote = string[0]
            gameFile = open(room_id + 'vote.txt', 'a')    
            gameFile.write(content.source.user_id+','+vote+','+profile.display_name+',' + "\n")
            gameFile.close()
        else:
            return [TextMessage(text="你來晚了，投票已過期了，滾~")]
        
        return []
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
