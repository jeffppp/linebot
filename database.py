# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 14:52:16 2019

@author: Yuan
"""
import sqlite3
import googleSheet
import time, datetime, pytz

def createTables():
    '''
    Create database's structure.
    '''
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute(
            '''CREATE TABLE Version(
            TableName VARCHAR(50) PRIMARY KEY NOT NULL,
            LatestTime INT NOT NULL);
            ''')
        c.execute(
            '''CREATE TABLE DataType(
            TypeID INT PRIMARY KEY NOT NULL,
            Type VARCHAR(50) NOT NULL);
            ''')
        c.execute(
            '''CREATE TABLE Dialog(
            Keyword VARCHAR(100) NOT NULL,
            DataType INT NOT NULL,
            KeywordValue VARCHAR(100) NOT NULL,
            CONSTRAINT pkey PRIMARY KEY (Keyword, KeywordValue),
            FOREIGN KEY(DataType) REFERENCES DataType(TypeID));
            ''')
        c.execute(
            '''CREATE TABLE Synonym(
            KeywordRef VARCHAR(100) PRIMARY KEY NOT NULL,
            Keyword VARCHAR(100) NOT NULL,
            FOREIGN KEY(Keyword) REFERENCES Dialog(Keyword));
            ''')
        c.execute(
            '''CREATE TABLE ScriptType(
            ScriptTypeID INT PRIMARY KEY NOT NULL,
            ScriptType VARCHAR(100) NOT NULL);
            ''')
        c.execute(
            '''CREATE TABLE ScriptIndex(
            ScriptID INT PRIMARY KEY NOT NULL,
            ScriptTypeID INT NOT NULL,
            ScriptName VARCHAR(100) NOT NULL,
            FOREIGN KEY(ScriptTypeID) REFERENCES ScriptType(ScriptTypeID));
            ''')
        c.execute(
            '''CREATE TABLE Script(
            ScriptID INT NOT NULL,
            LineID INT NOT NULL,
            DataType INT NOT NULL,
            LineIDNext INT,
            ScriptData VARCHAR(100),
            CONSTRAINT pkey PRIMARY KEY (ScriptID, LineID, DataType),
            FOREIGN KEY(ScriptID) REFERENCES ScriptIndex(ScriptID),
            FOREIGN KEY(DataType) REFERENCES DataType(TypeID),
            FOREIGN KEY(LineIDNext) REFERENCES Script(LineID));
            ''')       
        c.execute(
            '''CREATE TABLE PlayerStatus(
            UserID VARCHAR(50) NOT NULL primary key,
            UserName VARCHAR(20) NOT NULL,
            Score INT NOT NULL,
            Level INT NOT NULL);
            ''')
     
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('Dialog', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('Synonym', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('DataType', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('PlayerStatus', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('ScriptIndex', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('ScriptType', 0 )");
        c.execute("INSERT INTO Version (TableName,LatestTime) \
           VALUES ('Script', 0 )");
     
        db.commit()
        db.close()
    except:
        db.close()

def createUser(UserID, UserName):
    '''
    Create UserID and UserName to local database.
    
    Args:
       UserID: Str that the user's id.
       UserName: Str that the user's name.
       
    Returns:
       Bool that the creation is succeed or not.
    '''    
    if not checkUserID(UserID):
        try:
            db = sqlite3.connect('ba_ga_dino.sql')
            c = db.cursor()
            c.execute("INSERT INTO PlayerStatus (UserID,UserName,Score,Level) VALUES ('"+UserID.__str__()+"', '"+UserName.__str__()+"', 0, 1);")
            timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
            c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='PlayerStatus'")
            
            db.commit()
            db.close()
            googleSheet.createPlayer(UserID, UserName, 0, 1, timeStamp)
        except:
            db.close()
            return False
        return True
    else:
        return False
    
def checkTables(tables):
   '''
   Check tables if is exist.
   
   Args:
       tables: A list of str that the name of tables.
       
   Returns:
       A list of bool that the tables is exist or not. The list ordered by input tables.
   '''
   isExist = []
   for table in tables:
       isExist += [checkTable(table)]
   return isExist

def checkTable(table):
    '''
    Check table if is exist.
    
    Args:
        table: Str of the table's name.
        
    Returns:
        Bool that the table is exist or not.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='"+table+"';") 
    isExist = True if len(cursor.fetchall()) > 0 else False
    db.close()
    return isExist

def checkUserID(UserID):
    '''
    Check UserID if is exist.
   
    Args:
       UserID in UserID of Table(PlayerStatus)
       
    Returns:
        Bool that the UserID is exist or not.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT UserID FROM PlayerStatus WHERE UserID = '"+UserID+"';") 
    grabIDs = cursor.fetchall()
    isExist = True if len(grabIDs) > 0 else False
    db.close()
    return isExist

def getKeywordValues(keyword):
    '''
    Get the values from the dependent keyword.
    
    Args:
        keyword: Str of the keyword.
        
    Returns:
        A list of str that the dependent values from keyword.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT Keyword FROM Synonym WHERE KeywordRef='"+keyword+"';") 
    for k in cursor: keyword = k[0] 
    cursor = c.execute("SELECT DataType, KeywordValue FROM Dialog WHERE Keyword='"+keyword+"';") 
    keywordValue = c.fetchall()
    db.close()
    return keywordValue

def addDialog(data):
    '''
    Insert words to Dialog(Table).
    ''' 
    try:   
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        for d in data:
            c.execute("INSERT INTO Dialog (Keyword, DataType, KeywordValue) \
                VALUES ('"+d[0]+"', '"+str(d[1])+"', '"+d[2]+"' )");

        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='Dialog'")
        
        googleSheet.addDialog(data, timeStamp)
       
        db.commit()
        db.close()
    except:
        db.close()

def getAllScriptName(scriptTypeID):
    '''
    Get all of Script's name in scriptTypeID.
        
    Returns:
        A list of tuple. [(ScriptID, ScriptName), ...]
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT ScriptID, ScriptName FROM ScriptIndex WHERE ScriptTypeID = '" + str(scriptTypeID) + "';") 
    ScriptName = c.fetchall()
    db.close()
    return ScriptName

def getScriptName(scriptID):
    '''
    Get ScriptTypeID and ScriptName in scriptTypeID.
        
    Returns:
        A tuple. (ScriptID, ScriptName)
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT ScriptTypeID, ScriptName FROM ScriptIndex WHERE ScriptID = '" + str(scriptID) + "';") 
    ScriptName = c.fetchall()
    db.close()
    return ScriptName[0]

def getDataType(ID):
    '''
    Get data type with ID.
        
    Returns:
        A string of data type.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT Type FROM DataType WHERE TypeID='"+ID.__str__()+"';") 
    dataType = ''
    for t in cursor:
        dataType = t[0]
    db.close()
    return dataType

def getScriptType(scriptTypeID):
    '''
    Get script type with ID.
        
    Returns:
        A string of script type.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT ScriptType FROM ScriptType WHERE ScriptTypeID='"+scriptTypeID.__str__()+"';") 
    ScriptType = ''
    for t in cursor:
        ScriptType = t[0]
    db.close()
    return ScriptType

def getScriptTypeID(scriptType):
    '''
    Get script type ID by name.
        
    Returns:
        A int of script type ID. Get -1 when no such scriptType.
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT ScriptTypeID FROM ScriptType WHERE ScriptType='"+scriptType.__str__()+"';") 
    ScriptTypeID = -1
    for t in cursor:
        ScriptTypeID = int(t[0])
    db.close()
    return ScriptTypeID

def getScript(scriptID, LineID):
    '''
    Get script from Script's table and use LineID to find specified data.
        
    Returns:
        A list of data [ScriptID, LineID, DataType, LineIDNext, ScriptData].
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT ScriptID, LineID, DataType, LineIDNext, ScriptData FROM Script WHERE LineID='"+LineID.__str__()+"' AND ScriptID="+str(scriptID)+";") 
    data = []
    for d in cursor:
        data += [[d[0], d[1], d[2], d[3], d[4]]]
    db.close()
    return data

def getUserStatus(UserID):
    '''
    Get data from PlayerStatus table and use UserID to find specified data.
       
    Returns:
       A list of data [UserID, UserName, Score, level].
    '''
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    cursor = c.execute("SELECT UserID, UserName, Score, Level FROM PlayerStatus WHERE UserID='"+UserID.__str__()+"';") 
    data = []
    for d in cursor:
        data += [[d[0], d[1], d[2], d[3]]]
    db.close()
    return data

def updateDialog():
    '''
    Update Dialog(Table) and Synonym(Table) both.
    '''
    dialog = googleSheet.getSheet('Dialog')
    synonym = googleSheet.getSheet('Synonym')
 
    try:   
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from Synonym;")
        c.execute("DELETE from Dialog;")
        for d in dialog:
            c.execute("INSERT INTO Dialog (Keyword,DataType,KeywordValue) \
                VALUES ('"+d[0]+"', '"+d[1]+"', '"+d[2]+"' )");
        for s in synonym:
            c.execute("INSERT INTO Synonym (KeywordRef,Keyword) \
                VALUES ('"+s[0]+"', '"+s[1]+"' )");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='Dialog'")
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='Synonym'")
        db.commit()
        db.close()
    except:
        db.close() 

def updateScriptIndex():
    '''
    Update ScriptIndex(Table).
    '''
    scriptIndex = googleSheet.getSheet('ScriptIndex')
    
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from ScriptIndex;")
        for s in scriptIndex:
            c.execute("INSERT INTO ScriptIndex (ScriptID, ScriptTypeID, ScriptName) \
                VALUES ('"+s[0]+"', '"+s[1]+"', '"+s[2]+"' )");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='ScriptIndex'")
        db.commit()
        db.close()
    except:
        db.close()
        
def updateScriptType():
    '''
    Update ScriptType(Table).
    '''
    scriptType = googleSheet.getSheet('ScriptType')
    
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from ScriptType;")
        for s in scriptType:
            c.execute("INSERT INTO ScriptType (ScriptTypeID, ScriptType) \
                VALUES ('"+s[0]+"', '"+s[1]+"')");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='ScriptType'")
        db.commit()
        db.close()
    except:
        db.close()        
        
def updateScript():
    '''
    Update Script(Table).
    '''
    script = googleSheet.getSheet('Script')
    
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from Script;")
        for s in script:
            c.execute("INSERT INTO Script (ScriptID, LineID, DataType, LineIDNext, ScriptData) \
                VALUES ('"+s[0]+"', '"+s[1]+"', '"+s[2]+"', '"+s[3]+"', '"+s[4]+"' )");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='Script'")
        db.commit()
        db.close()
    except:
        db.close()                

def updateDataType():
    '''
    Update DataType(Table).
    '''
    dataType = googleSheet.getSheet('DataType')
    
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from DataType;")
        for d in dataType:
            c.execute("INSERT INTO DataType (TypeID,Type) \
                VALUES ('"+d[0]+"', '"+d[1]+"' )");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='DataType'")
        db.commit()
        db.close()
    except:
        db.close()

def updatePlayerStatus():
    '''
    Update PlayerStatus(Table).
    '''
    PlayerStatus = googleSheet.getSheet('PlayerStatus')
       
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("DELETE from PlayerStatus;")
        for g in PlayerStatus:
            c.execute("INSERT INTO PlayerStatus (UserID,UserName,Score,Level) VALUES ('"+g[0]+"', '"+g[1]+"', '"+g[2]+"', '"+g[3]+"' )");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='PlayerStatus'")
        db.commit()
        db.close()
    except:
        db.close()

def updateUserScore(UserID, UserName,deltaScore):
    '''
    Update UserScore in PlayerStatus(Table).
    '''
    try:
        db = sqlite3.connect('ba_ga_dino.sql')
        c = db.cursor()
        c.execute("select Score from PlayerStatus where UserID = '"+UserID.__str__()+"';")
        userScore = c.fetchall()[0][0]
        newScore = userScore + deltaScore
        
        c.execute("select Level from PlayerStatus where UserID = '"+UserID.__str__()+"';")
        userLevel = int(c.fetchall()[0][0])
        
        if newScore > 100:
            newScore = newScore - 100
            userLevel = userLevel + 1
        if newScore < 0:
            newScore = newScore + 100
            userLevel = userLevel - 1
        c.execute("update PlayerStatus set UserName ='"+UserName.__str__()+"',Score = "+newScore.__str__()+",Level = "+userLevel.__str__()+" where UserID ='"+UserID.__str__()+"';");
        timeStamp = str(int(datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).timestamp()))
    
        c.execute("UPDATE Version set LatestTime = "+timeStamp+" where TableName='PlayerStatus'")
        db.commit()
        db.close()
    
        googleSheet.updatePlayerScore(UserID, UserName, newScore, userLevel, str(int(timeStamp)))
    except:
        db.close()
    
def checkTablesNeedingUpdate():
    '''
    Check all the tables needing update between local and remote.
        
    Returns:
        A dictionary of table(str) and if need update(bool).
    '''
    #local
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    c.execute("SELECT * FROM Version;")
    local = c.fetchall()
    db.close()
    local = dict(local)
    #remote
    remote = googleSheet.getVersionAll()
    #compare
    for i in local:
        local[i] = local[i] < remote[i]
    
    return local

def updateTablesAll():
   '''
   Update all the each tables if the local version of table is older.
   '''
   tablesNeedingUpdate = checkTablesNeedingUpdate()
   if tablesNeedingUpdate['DataType']: updateDataType()
   if tablesNeedingUpdate['Dialog'] or tablesNeedingUpdate['Synonym'] : updateDialog()
   if tablesNeedingUpdate['PlayerStatus']: updatePlayerStatus()
   if tablesNeedingUpdate['ScriptIndex']: updateScriptIndex() 
   if tablesNeedingUpdate['ScriptType']: updateScriptType()
   if tablesNeedingUpdate['Script']: updateScript()

def getVersion(table):
   '''
   Get the local version of table from Version(Table).
   
   Args:
       table: Str of the table's name.
       
   Returns:
       An integer of the tables's version from local. Return -1 if there's no
       this sheet name in Version sheet from local.
   '''
   db = sqlite3.connect('ba_ga_dino.sql')
   c = db.cursor()
   cursor = c.execute("SELECT LatestTime FROM Version WHERE TableName='"+table+"';") 
   ver = -1
   for v in cursor: 
       ver = v[0] 
   db.close()
   return ver

def printDB():
    db = sqlite3.connect('ba_ga_dino.sql')
    c = db.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    for table in tables:
        c.execute("SELECT * FROM "+table[0]+";")
        datas = c.fetchall()
        print('\n['+table[0]+']*********************************************')
        for data in datas:
            print(data)
    db.close()