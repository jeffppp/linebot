from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import threading

# If modifying these scopes, delete the file token.pickle.
# read only
#SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# read write
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a spreadsheet.
SPREADSHEET_ID = '1rgxQJRH4xTMhuM2kWUr7-ZLJGpZwdwxzd8ex3xIwMOo'
RANGE_NAME = 'foods!A1:A'

def main():

    values = __getSheetValue(SPREADSHEET_ID, RANGE_NAME)

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row[0])
            
def getFoodList():
    return __getSheetValue(SPREADSHEET_ID, RANGE_NAME)            

def getVersion(table):
   '''
   Get version of this table from remote.
   
   Args:
       table: Str that the table's name.
       
   Returns:
       An integer of the tables's version from remote. Return -1 if there's no
       this sheet name in Version sheet from remote.
   '''
   versions = getVersionAll()
   try:
       return versions[table]
   except:
       return -1
    
def getVersionAll():
   '''
   Get version of all the tables from remote.
       
   Returns:
       A dictionary of the tables's name(str) and version(int) from remote.
   '''
   versions = __getSheetValue(SPREADSHEET_ID, 'Version!A2:Z')
   versions = dict(versions)
   for v in versions:
       versions[v] = int(versions[v])
   return dict(versions)

    
def getSheet(table):
   '''
   Get sheet of this table from remote.
   
   Args:
       table: Str that the table's name.
       
   Returns:
       A list of the sheet. The length of columns are the same as the table.
   '''
   return __getSheetValue(SPREADSHEET_ID, table + '!A2:Z')

def getSpecifiedRow(table, column, key):
   '''
   Get specified row from the remote sheet of this table where the key in specified column.
   
   Args:
       table: Str that the table's name.
       column: Str that the column(column A, B, C, ...)
       key: Str that be searched for spectified row
       
   Returns:
       A number of the specified row. Number -1 if no such key or table, column wrong.
   '''
   # 建立 Google Sheet API 連線
   credentials = __getCredentials()
   service = build('sheets', 'v4', credentials=credentials)
   
   range_ = 'LOOKUP_SHEET!A1'
   value_input_option = 'USER_ENTERED'
   value_range_body = {
       "range": "LOOKUP_SHEET!A1",
       "values": [
            [
                '=MATCH("'+key+'", '+table+'!'+column+':'+column+', 0)'
            ]
        ]
   }
   request = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=range_
            , valueInputOption=value_input_option, body=value_range_body, includeValuesInResponse=True)
   response = request.execute()
   
   if response['updatedData']['values'][0][0].isnumeric():
       return int(response['updatedData']['values'][0][0])
   else:
       return -1

def updatePlayerScore(userID, userName, score, level, timeStamp):
   '''
   Update player's name, score, level to the remote.
   
   Args:
       userID: Str of the user's ID.
       userName: Str of the user's name.
       score: Int of the user's score.
       level: Int of the user's level.
       timeStamp: Str of the timestamp
   '''
   # 建立 Google Sheet API 連線
   credentials = __getCredentials()
   service = build('sheets', 'v4', credentials=credentials)
   
   row = getSpecifiedRow("PlayerStatus", "A", str(userID))
   if row == -1: return
   
   range_ = 'PlayerStatus!A' + str(row) + ':D' + str(row)
   batch_update_values_request_body = {
    'value_input_option': 'USER_ENTERED',

    'data': [
        {
           "range": range_,
           "majorDimension": "ROWS",
           "values": [
                [userID, userName, score, level]
            ]        
        },
        {
          "range": "Version!B11:B11",
          "majorDimension": "ROWS",
          "values": [
            [timeStamp]
          ]
        }
    ]
    }
   request = service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=batch_update_values_request_body)
   request.execute()

def createPlayer(userID, userName, score, level, timeStamp):
   '''
   Create player's name, score, level to the remote.
   
   Args:
       userID: Str of the user's ID.
       userName: Str of the user's name.
       score: Int of the user's score.
       level: Int of the user's level.
   '''
   # 建立 Google Sheet API 連線
   credentials = __getCredentials()
   service = build('sheets', 'v4', credentials=credentials)
   #建立新Player
   range_ = 'PlayerStatus!A1:D1'
   value_input_option = 'USER_ENTERED'
   value_range_body = {
       "range": range_,
       "majorDimension": "ROWS",
       "values": [
            [userID, userName, score, level]
        ]
   }
   request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=range_
        , valueInputOption=value_input_option, body=value_range_body, includeValuesInResponse=False)
   request.execute()
   #更新remote的PlayerStatus時戳
   value_input_option = 'USER_ENTERED'
   value_range_body = {
       "range": "Version!B11:B11",
       "values": [
            [timeStamp]
        ]
   }
   request = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="Version!B11:B11"
        , valueInputOption=value_input_option, body=value_range_body, includeValuesInResponse=False)
   request.execute()

def addDialog(dialogs, timeStamp):
    '''
    Add new data of dialog to the remote.
   
    Args:
       dialogs: List of [keyword, dataType, keywordValue] and type is str, int, str
    '''
    def _addDialog(dialogs, timeStamp):
        for i in range(len(dialogs)):
            dialogs[i][1] = str(dialogs[i][1])
        # 建立 Google Sheet API 連線
        credentials = __getCredentials()
        service = build('sheets', 'v4', credentials=credentials)
        # 上傳要新增的資料
        value_input_option = 'USER_ENTERED'
        value_range_body = {
            "range": 'Dialog!A1:C1',
            "majorDimension": "ROWS",
            "values": dialogs
        }
        request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Dialog!A1:C1'
            , valueInputOption=value_input_option, body=value_range_body, includeValuesInResponse=False)
        request.execute()
        # 更新Version
        update_values_request_body = {
              "range": "Version!B3:B3",
              "majorDimension": "ROWS",
              "values": [
                [timeStamp]
              ]
        }
        request = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="Version!B3:B3"
            , valueInputOption=value_input_option, body=update_values_request_body, includeValuesInResponse=False)
        request.execute()
    threading.Thread(target=_addDialog, args=(dialogs, timeStamp)).start()

"""
取得 Sheet 資料
    Shows basic usage of the Sheets API.
 
    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
"""
def __getSheetValue(spreadsheetId, rangeName):
    
    # 建立 Google Sheet API 連線
    credentials = __getCredentials()
    service = build('sheets', 'v4', credentials=credentials)

    # 取得 Sheet 資料
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    return values

"""
取得授權
    Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
"""
def __getCredentials():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds   
   
def uploadException(mes):
    '''
    Upload the exception message to the remote.
   
    Args:
       mes: Str of exception message.
    '''
    def _uploadException(mes):
        # 建立 Google Sheet API 連線
        credentials = __getCredentials()
        service = build('sheets', 'v4', credentials=credentials)
    
        import time, datetime, pytz
        localtime = datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        range_ = 'Exception!A1:B1'
        value_input_option = 'USER_ENTERED'
        value_range_body = {
            "range": range_,
            "majorDimension": "ROWS",
            "values": [
                 [localtime, str(mes)]
            ]
        }
        request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range=range_
            , valueInputOption=value_input_option, body=value_range_body, includeValuesInResponse=False)
        request.execute()
    threading.Thread(target=_uploadException, args=(mes,)).start()
    
if __name__ == '__main__':
    main()
