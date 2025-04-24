import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import smtplib
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import json
import pandas as pd
from datetime import datetime
import os
from time import sleep
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import keyboard
import time
import threading
import webbrowser
import sys
from kivy.utils import platform

import random
import string


def open_docs(urls):
    for url in urls:
        webbrowser.open(url)
def check_ctrl_e():
    while True:
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('e'):
            open_docs()
        time.sleep(0.1)

def right_path(file):
    if platform == 'android':
        return file
    elif getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = 'C:\\Users\\usher\\Desktop\\Apps\\Email_Sender\\KivyVersion\\data'
    file_path = os.path.join(bundle_dir, file)
    return file_path
def generate_random_sequence(length=8):
    characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    return ''.join(random.choice(characters) for _ in range(length))
def send_code(receiver,sender='ushermichele2002@gmail.com',complexity=4):
    code=generate_random_sequence(complexity)
    msg=MIMEText(f'Here is the code to reset your password to Email Sender: {code}')
    msg['From'] = formataddr(('Michele Usher', sender))
    msg['Subject']='Reset Email Sender Password'
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp_server:
        smtp_server.login(sender,'vpwt wnwn agrx fgud')
        smtp_server.sendmail(sender,receiver,msg.as_string())
    # print('Message sent')
    return code

def give_permission(doc_id,user_email,json_path):
    scope = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(right_path(json_path), scope)
    service_docs = build('docs', 'v1', credentials=credentials)
    service_drive = build('drive', 'v3', credentials=credentials)
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': user_email
    }

    service_drive.permissions().create(
        fileId=doc_id,
        body=permission
    ).execute()
def get_text(doc_idd,service_docs):
    check=True
    while check:
        try:
            document = service_docs.documents().get(documentId=doc_idd).execute()
            text_content = ''
            for content in document.get('body').get('content', []):
                if 'paragraph' in content:
                    for element in content['paragraph']['elements']:
                        if 'textRun' in element:
                            text_content += element['textRun']['content']
            check=False
        except:
            check=True
    return text_content


def get_groups(board,api_token,url,session):

    query = '''
    query {
      boards(ids: YOUR_BOARD_ID) {
          id
          name
        groups {
          id
          title
        }
      }
    }
    '''
    query = query.replace('YOUR_BOARD_ID', str(board))


    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json',
    }


    payload = json.dumps({'query': query})


    response = session.post(url, data=payload, headers=headers,timeout=20)

    if response.status_code == 200:
        data = response.json()
        board_data = data['data']['boards']
        board_name = {board['id']: board['name'] for board in board_data}
        group_data = data['data']['boards'][0]['groups']
        group_ids = [group['id'] for group in group_data]
        group_names = [group['title'] for group in group_data]
    else:
        x=1

    return group_ids,group_names,board_name

def get_group_items(board_id,group_id,api_token,url,session):
    query = '''
        {
          boards(ids: %s) {
          groups(ids: ["%s"]){
              items_page(limit:500) {
              cursor
              items {
              id
              name
              column_values {
              column{
              title
              
              }
              ... on BoardRelationValue {display_value}
              text
            }
                }
              }
            }
          }
          }
        ''' % (board_id,group_id)


    headers = {
    'Authorization': api_token,
    'Content-Type': 'application/json',
    }


    payload = json.dumps({'query': query})


    response = session.post(url, data=payload, headers=headers)


    if response.status_code == 200:
        data = response.json()

    else:
        x=1

    return data
def next_page(cursor,api_token,url,session):
    query = '''
            {next_items_page(limit:500,cursor:"%s") {
                  cursor
                  items {
                  id
                  name
                  column_values {
                  column{
                  title
                  }
                  ... on BoardRelationValue {display_value}
                  text
                     }
                    }
                  }
                }
         ''' % (cursor)


    headers = {
        'Authorization': api_token,
        'Content-Type': 'application/json',
    }


    payload = json.dumps({'query': query})


    response = session.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()

    else:
        x=1

    return data
def format_next_data(data,name_column):
    data1=data['data']
    data2=data1['next_items_page']
    data3=data2['items']
    global next_cursor
    next_cursor=data2['cursor']
    name=[]
    df={}
    for i in data3:
        name.append(i[name_column])

    df['Name']=name


    for i in data3:
        i['column_values'].pop(0)
        for j in i['column_values']:
            title=j['column']['title']

            if title not in df:
                df[title]=[]
            if j['text']=='':
                 df[title]=df[title]+['  ']
            elif j['text']==None:
                df[title] = df[title] + [j['display_value']]
            else:
                df[title]=df[title]+[j['text']]
    df=pd.DataFrame(df)
    return df
def format_data(data,name_column,account_column):
    data1=data['data']
    data2=data1['boards']
    data3=data2[0]
    data5=data3['groups']
    data6=data5[0]
    data4=data6['items_page']
    global cursor
    cursor=data4['cursor']
    data7=data4['items']
    name=[]
    df={}
    for i in data7:
        name.append(i[name_column])
    df['Name']=name
    for i in data7:
        if i['column_values'][0]['column']['title']=='Sotto elementi':
            i['column_values'].pop(0)
        for j in i['column_values']:
            title=j['column']['title']
            if title not in df:
                df[title]=[]
            if j['text']=='':
                 df[title]=df[title]+['  ']
            elif title==account_column:
                df[title] = df[title] + [j['display_value']]
            else:
                df[title]=df[title]+[j['text']]
    df=pd.DataFrame(df)
    return df
def create_df(group,Board_id,api_token,url,session,name_column,account_column,email_column):
    group_ids,group_names,board_name=get_groups(Board_id,api_token,url,session)
    for i in range(len(group_names)):
        if group_names[i]==group:
            data=get_group_items(Board_id,group_ids[i],api_token,url,session)
            df0=format_data(data,name_column,account_column)
            if len(df0[email_column])==500:
                data1=next_page(cursor,api_token,url,session)
                df1=format_next_data(data1,name_column)
                if len(df1[email_column])==500:
                    data2=next_page(next_cursor,api_token,url,session)
                    df2 = format_next_data(data2,name_column)
                    if len(df2[email_column]) == 500:
                        data2 = next_page(next_cursor,api_token,url,session)
                        df3 = format_next_data(data2,name_column)
                        df = pd.concat([df0, df1, df2,df3], ignore_index=True)
                    else:
                        df = pd.concat([df0, df1, df2], ignore_index=True)
                else:
                    df = pd.concat([df0, df1], ignore_index=True)
            else:
                df=df0
    return df


def gather_info():
    sender_email = input('What is your email?')
    phone=input('What is your phone number?')
    return sender_email,phone


def email_sender(receiver_email,name,company,lingua,smtp_server,sender_email,smtp_port,sender_password,errors,n_mail,bodys,phone,n_err,Brochure_c_path,Brochure_i_path,attachment_name,prima_eng_subject,prima_ita_subject,seconda_eng_subject,seconda_ita_subject,sender_name,sender_title):
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(sender_email, sender_password)
    if 'eng' in lingua.lower():
        index=0
    elif 'ita' in lingua.lower():
        index=1
    msg = MIMEMultipart()
    if "From" in msg:
        del msg["From"]
    if "To" in msg:
        del msg["To"]
    msg["To"] = receiver_email
    if "Subject" in msg:
        del msg["Subject"]
    if 'eng' in lingua.lower():
        pdf_file_path = Brochure_c_path
        if n_mail.lower() == 'prima':
            msg["Subject"] = prima_eng_subject.replace('company',company)
        elif n_mail.lower() == 'seconda':
            msg["Subject"] = seconda_eng_subject.replace('company',company)
    elif 'ita' in lingua.lower():
        pdf_file_path = Brochure_i_path
        if n_mail.lower() == 'prima':
            msg["Subject"] = prima_ita_subject.replace('company',company)
        elif n_mail.lower() == 'seconda':
            msg["Subject"] = seconda_ita_subject.replace('company',company)
    if isinstance(pdf_file_path, str):

        with open(pdf_file_path, "rb") as pdf_file:
            pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf", Name=f'{attachment_name}.pdf')
            pdf_attachment.add_header('content-disposition', 'attachment', filename=f"{attachment_name}.pdf")
            msg.attach(pdf_attachment)
    else:
        print('no attachment')
    if 'Mr' in name:
        name=name.replace('r','r.',1)
    elif 'Ms' in name:
        name=name.replace('s','s.',1)
    else:
        name = name.split()
        name = name[0]
    ext = bodys[index]
    ext = ext.replace('nome', name,1)
    ext = ext.replace('name', name,1)
    ext = ext.replace('company', company)
    ext = ext.replace('compagnia', company)
    salesperson=sender_name
    ext = ext.replace('phoneNumber', phone)
    now=datetime.now()
    hour=now.hour
    if hour<13:
        if 'eng' in lingua.lower():
            ext=ext.replace('hour','morning',1)
        elif 'ita' in lingua.lower():
            ext = ext.replace(' ora', 'giorno',1)
    else:
        if 'eng' in lingua.lower():
            ext = ext.replace('hour', 'afternoon',1)
        elif 'ita' in lingua.lower():
            ext = ext.replace('ora', 'pomeriggio',1)
    ext=ext.replace('position',sender_title)
    ext = ext.replace('salesperson', salesperson)
    msg['From'] = formataddr((salesperson, sender_email))
    msg.attach(MIMEText(ext,'plain'))
    try:
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email with .msg attachment sent successfully!")
    except Exception as e:
        errors.append(name)
        n_err+=1
    return n_err,errors
from firestore import get_document
def check_name(user,db):
    if user=='':
        return False, None, None,None, None, None, None
    dic = get_document(db, 'companies', 'krilldesign', 'salespeople', user)
    if dic is None:
        return False, None, None,None,None,None,None,None
    else:
        sender_email=dic['email']
        phone=dic['phone']
        login_password=dic['login_password']
        sender_password=dic['sender_password']
        smtp_server=dic['smtp_server']
        smtp_port = dic['smtp_port']
        title=dic['title']
    return True,sender_email,phone,title,login_password,sender_password,smtp_server,smtp_port
from firestore import create_document
def add_row_to_database(db,user,sender_email,phone,sender_password,title,smtp_server,smtp_port):
    if not check_name(user,db)[0]:
        create_document(db, 'companies', 'krilldesign', 'salespeople',user,title=title,email=sender_email,phone=phone,login_password=sender_password,sender_password=sender_password,smtp_server=smtp_server,smtp_port=smtp_port)


def get_bodys(primaEng,secondaEng,primaIta,secondaIta,terzaEng='',quartaEng='',quintaEng='',sestaEng='',terzaIta='',quartaIta='',quintaIta='',sestaIta='',json_path='docKey.json'):
    scope = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(right_path(json_path), scope)
    service_docs = build('docs', 'v1', credentials=credentials)
    if terzaEng=='':
        bodys = [get_text(primaEng, service_docs), get_text(primaIta, service_docs),get_text(secondaEng, service_docs), get_text(secondaIta, service_docs)]
    else:
        bodys = [get_text(primaEng, service_docs), get_text(primaIta, service_docs), get_text(secondaEng, service_docs),
                 get_text(secondaIta, service_docs),get_text(terzaEng, service_docs),get_text(terzaIta, service_docs),get_text(quartaEng, service_docs),
                 get_text(quartaIta, service_docs),get_text(quintaEng, service_docs),get_text(quintaIta, service_docs),
                 get_text(sestaEng, service_docs),get_text(sestaIta, service_docs)]
    return bodys

