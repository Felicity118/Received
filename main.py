import sys
import os
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


import io
import tempfile

from googleapiclient.http import MediaIoBaseDownload
import time
import pandas as pd
from datetime import datetime
from time import sleep
import subprocess
import random
import string
import smtplib
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import keyboard
import webbrowser
import re
from basic_email import create_df, get_groups, check_name, add_row_to_database, get_bodys, right_path, send_code, email_sender, open_docs
from firestore import get_all_documents_field_in_collection,update_document,get_document,create_document,get_document_subcollections,create_doc_reference
import json
import requests
from update import check_version,install_new_version,delete_old_version,upload_file
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window
from kivymd.uix.appbar import MDActionBottomAppBarButton,MDTopAppBarLeadingButtonContainer,MDActionTopAppBarButton
import threading
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.list import MDListItem, MDListItemHeadlineText,MDListItemSupportingText
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.screen import MDScreen
from kivymd.uix.appbar import MDActionBottomAppBarButton
import firebase_admin
from firebase_admin import credentials, firestore

from pathlib import Path
from shutil import copyfile
class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
class NavigationScreen(MDScreen):
    pass
class UserScreen(MDScreen):
    pass
class EmailScreen(MDScreen):
    pass
class ChangeScreen(Screen):
    pass
class CodeScreen(Screen):
    pass
class PasswordScreen(Screen):
    pass
class LoginScreen(Screen):
    pass
class DateScreen(Screen):
    pass
class SummaryScreen(MDScreen):
    pass
def is_json_file_empty(file_path: str) -> bool:
    try:
        with open(file_path, 'r') as file:
            content = json.load(file)

        return content == {} or content == []
    except json.JSONDecodeError:

        return True
    except FileNotFoundError:

        return True

class MainApp(MDApp):
    dialog = None
    wrong_code=StringProperty("")
    error_message = StringProperty("")
    login_email_error_message = StringProperty("")
    retrieve_email_error_message = StringProperty("")
    login_password_error_message = StringProperty("")
    password_reset_error_message = StringProperty("")
    outcome = StringProperty("")
    help_text='ciao'
    space=0.15
    pos_group=0.65
    pos_name=pos_group-space
    pos_n_mail=pos_name-space
    pos_email = pos_n_mail
    pos_phone = pos_email-space
    pos_n_mail2=pos_phone-space
    def do_requests(self):
        self.text_fields = {}
        cred = credentials.Certificate(right_path("firestore_key.json"))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        self.db = db
    def build(self):
        delete_old_version()
        self.title="Receiver"
        Window.set_icon(right_path('myicon.ico'))

        self.screen=Builder.load_file(right_path('app.kv'))
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Aliceblue"
        self.file_manager = None
        return self.screen
    def run_open_file_manager(self):
        Clock.schedule_once(self.open_file_manager, 0)

    def open_file_manager(self,time):
        if self.file_manager is None:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.upload_document
            )
        self.file_manager.show(os.path.expanduser("~"))

    def exit_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
            self.file_manager = None

    def upload_document(self, file_path):
        """Handles file selection and uploads to Google Drive"""
        self.exit_file_manager()
        name=os.path.basename(file_path)
        self.file_name = name.split('.')[0]
        self.upload_id=upload_file(file_path, self.file_name)

        print(self.file_name)
        self.continue_after_selection()
        # print(upload_id)
        # return upload_id


    def create_session(self):
        self.url = 'https://api.monday.com/v2'
        session = requests.Session()
        session.headers.update({'User-Agent': 'My User Agent'})
        self.session = session
    def sum_on_start(self):
        # common_imports()
        self.create_session()
    def assist_on_start(self):
        thread = threading.Thread(target=self.sum_on_start)
        thread.start()
    def on_start(self):
        self.root.md_bg_color = self.theme_cls.backgroundColor
        self.do_requests()
        self.assist_on_start()
        try:
            resource_name = "remember_me.json"
            writable_json_path = self.ensure_writable_file(resource_name)
            with open(writable_json_path, 'r') as file:
                data = json.load(file)
            username=data['username']
            id=data['id']
            self.username=username
            self.assist_autologin()
            self.assist_years(0)

        except Exception as e:

            self.root.current = 'login'

        self.show_text_field('user_name', "What is your full name?", 0.5, 0.85, on_validate_callback=self.esonerate_name, screen='User',height='38dp')
        file_id,version,bol=check_version(self.db)
        self.file_id=file_id
        self.version=version
        print(version,bol)
        if not bol:
            self.show_update_prompt(version)

    def assist_table(self):
        thread = threading.Thread(target=self.add_table)
        thread.start()
    def assist_years(self,dt):
        while True:
            try:
                self.create_year_list()
                break
            except Exception as e:
                x=1

    def assist_autologin(self):
        thread = threading.Thread(target=self.auto_login)
        thread.start()
    def create_year_list(self):
        # print('about to create year list')
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.clear_widgets()
        fields,docs=get_all_documents_field_in_collection(self.db,'companies',self.id,'Outbound Results')
        years = [doc.id for doc in docs]
        # print(years)
        self.years=years
        for year in years:
            item = MDListItem(
                MDListItemHeadlineText(
                text=year,
                ),
                size_hint_x=.8,
                pos_hint= {'center_x': 0.5})
            item.bind(on_release=lambda x, y=year: self.on_year_click(y))
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.add_widget(item)

    def on_year_click(self, year):
        self.selected_year = year
        self.populate_months()

    def populate_months(self):
        """Populate the list with months."""
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.clear_widgets()

        months=get_document_subcollections(self.db,'companies',self.id,'Outbound Results',self.selected_year)
        self.check_month=True
        for month in months:
            item = MDListItem(MDListItemHeadlineText(text=month,),size_hint_x=.8,pos_hint= {'center_x': 0.5})
            item.bind(on_release=lambda x, m=month: self.on_month_click(m))

            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.add_widget(item)
        self.add_left_action_item()
    def add_left_action_item(self):
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.back_arrow.icon='arrow-left'
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.back_arrow.bind(on_release=lambda x: self.go_back_date())
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.back_arrow.disabled = False

    def remove_left_action_item(self):

        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.back_arrow.icon=''
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.back_arrow.disabled = True
    def go_back_date(self):
        if self.check_month:
            self.go_back_to_years()
            self.check_month=False
            self.remove_left_action_item()
    def go_back_to_months(self):
        self.root.current = 'navigation'
        try:
            self.root.get_screen('log').ids.log.remove_widget(self.table_anchor)
        except:
            x=1
    def go_back_to_years(self):
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.clear_widgets()
        years=self.years
        for year in years:
            item = MDListItem(
                MDListItemHeadlineText(
                    text=year,
                ),
                size_hint_x=None,
                width=dp(200),
                pos_hint={'center_x': 0.5})
            item.bind(on_release=lambda x, y=year: self.on_year_click(y))
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Log').ids.date_list.add_widget(item)

    def on_month_click(self, month):
        """Handle month selection."""
        self.selected_month = month
        self.assist_table()
    def show_spinner(self):
        self.spinner = MDLinearProgressIndicator(
            size_hint_x=0.5,
            size_hint_y=None,
            type='indeterminate',
            pos_hint= {'center_x': .5, 'center_y': .5},
        )
        self.root.get_screen('log').ids.table_anchor.add_widget(self.spinner)
        self.spinner.start()
    def hide_spinner(self):
        self.root.get_screen('log').ids.table_anchor.remove_widget(self.spinner)

    def create_table(self,dt):
        # width = 25
        self.root.get_screen('log').ids.date_list.padding=[150,150,0,200]
        for row in self.row_data:
            item = MDListItem(
                MDListItemHeadlineText(
                    text=row[0]+' '+row[1],
                ),
                MDListItemSupportingText(text=f"Board: {row[2]}, Group: {row[3]}, successful emails: {row[4]}, unsuccessul emails: {row[5]}"),
                size_hint_x=.8,
                pos_hint={'center_x': 0.5}
            )
            self.root.get_screen('log').ids.date_list.add_widget(item)
        self.hide_spinner()


    def change_to_log_screen(self,dt):
        self.show_spinner()
        self.root.get_screen('log').ids.top_bar.text=f'{self.selected_month} {self.selected_year}'
        self.root.current = 'log'

    def add_table(self):
        Clock.schedule_once(self.change_to_log_screen)
        fields,docs= get_all_documents_field_in_collection(self.db,'companies',self.id,'Outbound Results',self.selected_year,self.selected_month)
        dics=[doc.get().to_dict() for doc in docs]
        dates=[doc.id for doc in docs]
        row_data=[(dates[d],dics[d]['salesperson'],dics[d]['board_name'],dics[d]['group_name'],dics[d]['number_successful'],dics[d]['number_unsuccessful']) for d in range(len(dics))]
        self.row_data=row_data
        Clock.schedule_once(self.create_table)

    def add_row(self,today,salesperson,board_name,group_name,number_successful,number_unsuccessfull,unsucesss_leads):

        str1='[color =  # 297B50]'
        str2='[/color]'
        new_row = (today,salesperson,board_name,group_name,number_successful,number_unsuccessfull,unsucesss_leads)
        self.table.add_row(new_row)
    def switch_tab(self,bar: MDNavigationBar,item: MDNavigationItem,item_icon: str,item_text: str,):
        if self.role=='Business Developer' and item_text=='User':
            return False
        self.root.get_screen('navigation').ids.nav_screen_manager.current = item_text

    def switch_screen(self, screen_name):
        self.root.get_screen('navigation').ids.nav_screen_manager.current = screen_name
    def change_to_navigation(self,dt):
        self.root.get_screen('login').ids.email.text=''
        self.root.get_screen('login').ids.password.text = ''
        self.root.current = 'navigation'
    def auto_login(self):
        username=self.username
        field_values, docs = get_all_documents_field_in_collection(self.db, 'companies', field='email')
        doc_ref = docs[field_values.index(username)]
        dic = doc_ref.get().to_dict()
        self.dic=dic
        doc_path = doc_ref.path
        company_name = doc_path.split('/')[1]
        api_doc = create_doc_reference(self.db, ['companies', company_name])
        self.api_token = api_doc.get().to_dict()['api_token']
        id = api_doc.id
        self.id=id
        field_values, docs = get_all_documents_field_in_collection(self.db, 'companies',id,'boards', field='board_id')
        board_names=[j.id for j in docs]
        self.Board_ids=dict(zip(board_names,field_values))
        Clock.schedule_once(self.change_to_navigation)
        self.role=dic['title']
        Clock.schedule_once(lambda dt: self.adjust_navigation_for_user())
    def cancel_email(self,dt):
        self.root.get_screen('password').ids.email.text = ''
        t='Email not in database. Try again.'
    def check_retrieve_email(self):
        field_values,docs=get_all_documents_field_in_collection(self.db,'companies',field='email')
        self.fiel_values=field_values
        self.docs=docs
        if self.root.get_screen('password').ids.email.text not in field_values:
            Clock.schedule_once(self.cancel_email)
            return False
        else:
            self.retrieve_email_error_message=''
        return True
    def message_login_email_error(self,dt):
        self.root.get_screen('login').ids.email.text = ''
        self.login_email_error_message = 'Email not in database. Try again.'

    def message_login_email_correct(self,dt):
        self.login_email_error_message = ''
    def assist_check_login_email(self):
        thread = threading.Thread(target=self.check_login_email)
        thread.start()
    def check_login_email(self):
        field_values,docs=get_all_documents_field_in_collection(self.db,'companies',field='email')
        self.field_values=field_values
        self.docs=docs
        if self.root.get_screen('login').ids.email.text not in field_values:
            Clock.schedule_once(self.message_login_email_error)
            return False
        else:
            Clock.schedule_once(self.message_login_email_correct)
            return True

    def open_menu(self,item):
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_items(x)
            } for i in self.Board_ids
        ]
        self.menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            position='bottom',
        )
        self.menu.open()
    def open_bodys_menu(self,item):
        doc_names=['Prima','Seconda','Terza','Quarta','Quinta','Sesta']
        if self.board_name!='Materiale 2':
            doc_names=doc_names[:2]
        doc_names = doc_names[:2]
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_body_items(x)
            } for i in doc_names
        ]
        self.bodys_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            position='top',
        )
        self.bodys_menu.open()
    def set_body_items(self,item):
        self.doc_number=item.lower()
        doc_language=['ita','eng']
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_language(x)
            } for i in doc_language
        ]
        self.language_menu = MDDropdownMenu(
            caller=self.bodys_menu,
            items=menu_items,
            position='center',
        )
        self.language_menu.open()
        self.bodys_menu.dismiss()
    def continue_after_selection(self):
        if self.active_attachment_button==self.english_attachment_button:
            self.english_attachment_button.children[0].text = self.file_name
            self.Brochure_c = self.upload_id
            create_document(self.db, 'companies', self.id, 'attachments', self.file_name, Brochure_c=self.upload_id)
        elif self.active_attachment_button==self.italian_attachment_button:
            self.italian_attachment_button.children[0].text = self.file_name
            self.Brochure_i = self.upload_id
            create_document(self.db, 'companies', self.id, 'attachments', self.file_name, Brochure_i=self.upload_id)
    def assist_set_italian_brochure(self,item):
        self.italian_item=item
        thread = threading.Thread(target=self.set_italian_brochure)
        thread.start()
    def set_italian_button_text(self,time):
        self.italian_attachment_button.children[0].text =self.italian_button_text
    def show_english_button(self,time):
        email_screen = self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email')
        if not self.english_button_monitor:
            self.english_attachment_button = MDButton(MDButtonText(text='Attachment eng'),
                                                      on_release=self.open_english_attachment_menu,
                                                      pos_hint={"center_x": 0.62, "center_y": .2})
            email_screen.add_widget(self.english_attachment_button)
            self.english_button_monitor=True
    def delete_italian_attachment(self,time):
        self.attachment_deletion_menu(self.italian_attachment_button, self.real_italian_ids)
    def set_italian_brochure(self):
        item=self.italian_item
        self.italian_attachment_menu.dismiss()

        if not item:
            print('Same as english')
            self.italian_button_text='Same as english'
            Clock.schedule_once(self.set_italian_button_text)
            self.Brochure_i=True
        elif item=='Add attachment':
            self.run_open_file_manager()
            print('adding attachment')
        elif item=='None':
            self.italian_button_text='None'
            Clock.schedule_once(self.set_italian_button_text)

            self.Brochure_i=False
            print('no attachment')
        elif item=='Remove attachment':
            Clock.schedule_once(self.delete_italian_attachment)
            print('attachment removed')
        else:
            self.italian_button_text=item
            Clock.schedule_once(self.set_italian_button_text)
            self.Brochure_i=self.total_italian_brochures[self.italian_ids.index(item)]
            print(self.Brochure_i)
        Clock.schedule_once(self.show_english_button)


    def attachment_deletion_menu(self,item,list):
        menu_items = [
            {
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.delete_brochure(x)
            } for i in list
        ]
        self.deletion_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            position='top',
        )
        self.deletion_menu.open()
    def delete_brochure(self,item):
        self.deletion_menu.dismiss()

        if self.active_attachment_button==self.english_attachment_button:
            doc_ref=self.total_english_docs[self.english_ids.index(item)]
            doc_ref.delete()
            if doc_ref.id==self.english_attachment_button.children[0].text:
                self.english_attachment_button.children[0].text='Attachment eng'
        elif self.active_attachment_button==self.italian_attachment_button:
            doc_ref=self.total_italian_doc[self.italian_ids.index(item)]
            doc_ref.delete()
            if doc_ref.id == self.italian_attachment_button.children[0].text:
                self.italian_attachment_button.children[0].text = 'Attachment ita'

    def open_english_attachment_menu(self,item):
        self.active_attachment_button = item
        self.real_english_ids=[i.id for i in self.english_docs]+[f.id for f in self.new_english_docs]
        self.english_ids=self.real_english_ids+['None','Add attachment','Remove attachment']
        self.total_english_docs=self.english_docs+self.new_english_docs+[None,None,None]
        self.total_english_brochures=self.english_brochures+self.new_english_brochures+[None,None,None]
        menu_items = []
        for i in self.english_ids[:-3]:
            menu_items.append({
                "text": f"{i}",
                "on_release": lambda x=i: self.set_english_brochure(x),
                "height": dp(40),
                "theme_text_color": "Primary",
                "text_color": (0, 0, 0, 1),
                "md_bg_color": (1, 1, 1, 1)
            })
        if isinstance(self.Brochure_i, str) or not self.Brochure_i:
            menu_items.append({
                "text": "None",
                "on_release": lambda x="None": self.set_english_brochure(x),
                "height": dp(20),
                "theme_text_color": "Custom",
                "text_color": (0.7, 0, 0, 1),
                "md_bg_color": (0.9, 0.9, 0.9, 1)
            })
        if isinstance(self.Brochure_i, str):
            menu_items.append({
            "text": "Same as italian",
            "on_release": lambda x=False: self.set_english_brochure(x),
            "height": dp(20),
            "theme_text_color": "Custom",
            "text_color": (0, 0, 0.8, 1),
            "md_bg_color": (0.9, 0.9, 0.9, 1)
        })
        menu_items.append({
            "text": "Add attachment",
            "on_release": lambda x="Add attachment": self.set_english_brochure(x),
            "height": dp(20),
            "theme_text_color": "Custom",
            "text_color": (0, 0.5, 0, 1),
            "md_bg_color": (0.9, 0.9, 0.9, 1)
        })
        menu_items.append({
            "text": "Remove attachment",
            "on_release": lambda x="Remove attachment": self.set_english_brochure(x),
            "height": dp(20),
            "theme_text_color": "Custom",
            "text_color": (0.5, 0.5, 0, 1),
            "md_bg_color": (0.9, 0.9, 0.9, 1)
        })
        self.english_attachment_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            position='top',
        )
        self.english_attachment_menu.open()

    def set_english_brochure(self,item):
        self.english_attachment_menu.dismiss()
        if not item:
            print('same as italian')
            self.english_attachment_button.children[0].text ='Same as italian'
            self.Brochure_c=True
        elif item=='Add attachment':
            self.run_open_file_manager()
            print('added attachment')
        elif item=='None':
            self.english_attachment_button.children[0].text = 'None'
            self.Brochure_c=False
            print('no attachment')
        elif item=='Remove attachment':
            self.attachment_deletion_menu(self.english_attachment_button,self.real_english_ids)
            print('attachment removed')
        else:
            self.english_attachment_button.children[0].text = item
            self.Brochure_c = self.total_english_brochures[self.english_ids.index(item)]
            print(self.Brochure_c)
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.send_email.disabled = False
    def set_language(self,item):
        self.doc_language=item
        thread = threading.Thread(target=self.set_body_item)
        thread.start()
        self.language_menu.dismiss()

    def set_body_item(self):
        item=self.doc_number+' '+self.doc_language
        doc_dic={'prima ita':0,'prima eng':1,'seconda ita':2,'seconda eng':3,'terza ita':4,'terza eng':5,'quarta ita':6,
                 'quarta eng': 7,'quinta ita':8,'quinta eng':9,'sesta ita':10,'sesta eng':11}
        url=self.urls[doc_dic[item]]
        webbrowser.open(url)
    def set_items(self, item):
        self.board_name = item
        thread = threading.Thread(target=self.set_item)
        thread.start()
    def update_selection(self,dt):
        self.hide_text_field('group')
        item=self.board_name
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.board_button.text = item
        self.menu.dismiss()
    def open_attachment_menu(self,item):
        self.active_attachment_button=item
        self.get_italian_brochures()
        self.total_italian_doc=self.italian_docs+self.new_italian_docs+[None,None,None]
        self.real_italian_ids=[i.id for i in self.italian_docs]+[f.id for f in self.new_italian_docs]
        self.italian_ids = self.real_italian_ids+['None','Add attachment','Remove attachment']
        self.total_italian_brochures=self.italian_brochures+self.new_italian_brochures+[None,None,None]
        menu_items=[]
        for i in self.italian_ids[:-3]:
            menu_items.append({
                "text": f"{i}",
                "on_release": lambda x=i: self.assist_set_italian_brochure(x),
                "height": dp(40),
                "theme_text_color": "Primary",
                "text_color": (0, 0, 0, 1),
                "md_bg_color": (1, 1, 1, 1)
            })

        if self.english_button_monitor:
            if not self.english_attachment_button.children[0].text=='Same as italian':
                menu_items.append({
                "text": "None",
                "on_release": lambda x='None': self.assist_set_italian_brochure(x),
                "height": dp(20),
                "theme_text_color": "Custom",
                "text_color": (0.8, 0, 0, 1),
                "md_bg_color": (0.9, 0.9, 0.9, 1)
            })
                if not self.english_attachment_button.children[0].text=='None':
                    menu_items.append({
                "text": "Same as english",
                "on_release": lambda x=False: self.assist_set_italian_brochure(x),
                "height": dp(20),
                "theme_text_color": "Custom",
                "text_color": (0, 0, 0.7, 1),
                "md_bg_color": (0.9, 0.9, 0.9, 1)
            })
        else:
            menu_items.append({
                "text": "None",
                "on_release": lambda x='None': self.assist_set_italian_brochure(x),
                "height": dp(20),
                "theme_text_color": "Custom",
                "text_color": (0.8, 0, 0, 1),
                "md_bg_color": (0.9, 0.9, 0.9, 1)
            })
            menu_items.append({
                "text": "Same as english",
                "on_release": lambda x=False: self.assist_set_italian_brochure(x),
                "height": dp(20),
                "theme_text_color": "Custom",
                "text_color": (0, 0, 0.7, 1),
                "md_bg_color": (0.9, 0.9, 0.9, 1)
            })
        menu_items.append({
            "text": "Add attachment",
            "on_release": lambda x='Add attachment': self.assist_set_italian_brochure(x),
            "height": dp(20),
            "theme_text_color": "Custom",
            "text_color": (0, 0.5, 0, 1),
            "md_bg_color": (0.9, 0.9, 0.9, 1)
        })
        menu_items.append({
            "text": "Remove attachment",
            "on_release": lambda x='Remove attachment': self.assist_set_italian_brochure(x),
            "height": dp(20),
            "theme_text_color": "Custom",
            "text_color": (0.5, 0.5, 0, 1),
            "md_bg_color": (0.9, 0.9, 0.9, 1)
        })
        self.italian_attachment_menu = MDDropdownMenu(
            caller=item,
            items=menu_items,
            position='top',
        )
        self.italian_attachment_menu.open()


    def show_group_field(self,dt):
        self.show_text_field('group', 'Group Name', 0.5, self.pos_group, self.check_create_df)
        self.url_button=MDButton(MDButtonText(text='Edit Email Bodys'), on_release=self.open_bodys_menu,pos_hint={"center_x":0.85,"center_y": .1})
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').add_widget(self.url_button)
    def set_item(self):
        item=self.board_name
        Clock.schedule_once(self.update_selection)
        dic=get_document(self.db, 'companies', 'krilldesign', 'boards', item)
        self.account_column = dic['account_column']
        self.name_column = dic['name_column']
        self.email_column = dic['email_column']
        self.language_column = dic['language_column']
        self.prima_eng = dic['prima_eng']
        self.prima_ita = dic['prima_ita']
        self.seconda_ita = dic['seconda_ita']
        self.seconda_eng = dic['seconda_eng']
        self.urls = ['https://docs.google.com/document/d/' + self.prima_ita + '/edit?usp=sharing',
                'https://docs.google.com/document/d/' + self.prima_eng + '/edit?usp=sharing',
                'https://docs.google.com/document/d/' + self.seconda_ita + '/edit?usp=sharing',
                'https://docs.google.com/document/d/' + self.seconda_eng + '/edit?usp=sharing']

        self.prima_eng_subject = dic['prima_eng_subject']
        self.prima_ita_subject = dic['prima_ita_subject']
        self.seconda_ita_subject = dic['seconda_ita_subject']
        self.seconda_eng_subject = dic['seconda_eng_subject']
        self.bodys = get_bodys(self.prima_eng, self.seconda_eng, self.prima_ita, self.seconda_ita)
        self.Brochure_c=dic['Brochure_c']
        try:
            self.Brochure_i = dic['Brochure_i']
        except:
            self.Brochure_i=dic['Brochure_c']
        self.attachment_name=dic['attachment_name']
        Clock.schedule_once(self.hide_all)
        Clock.schedule_once(self.show_group_field)

        self.Board_id=self.Board_ids[item]
        group_ids, group_names, board_name = get_groups(self.Board_id, self.api_token, self.url, self.session)
        self.group_names=group_names
    def assist_login(self):
        thread = threading.Thread(target=self.login)
        thread.start()
    def disable_login_button(self,dt):
        self.root.get_screen('login').ids.login_button.disabled = True


    def adjust_navigation_for_user(self):
        admin_button = self.root.get_screen('navigation').ids.admin_button
        if self.role == 'Business Developer':
            admin_button.opacity = 0
        else:
            admin_button.opacity = 1

    def login(self):
        if not self.check_login_email():
            return False
        field_values, docs = get_all_documents_field_in_collection(self.db, 'companies', field='email')
        doc_ref=docs[field_values.index(self.root.get_screen('login').ids.email.text)]
        dic=doc_ref.get().to_dict()
        self.dic=dic
        password=dic['login_password']
        self.role=dic['title']
        if self.root.get_screen('login').ids.password.text==password:
            self.login_password_error_message = ''
            doc_path = doc_ref.path
            company_name = doc_path.split('/')[1]
            api_doc=create_doc_reference(self.db,['companies',company_name])
            self.api_token=api_doc.get().to_dict()['api_token']
            id = api_doc.id
            self.id=id
            field_values, docs = get_all_documents_field_in_collection(self.db, 'companies', id, 'boards', field='board_id')
            board_names = [j.id for j in docs]
            self.Board_ids = dict(zip(board_names, field_values))
            Clock.schedule_once(self.assist_years)
            Clock.schedule_once(self.change_to_navigation)
            Clock.schedule_once(lambda dt: self.adjust_navigation_for_user())
            if self.root.get_screen('login').ids.checkbox.active:
                resource_name = "remember_me.json"
                writable_json_path = self.ensure_writable_file(resource_name)
                with open(writable_json_path, "w") as file:
                    json.dump({"username": self.root.get_screen('login').ids.email.text, "password": password,'id':id}, file)
        else:
            Clock.schedule_once(self.wrong_credential)

    def wrong_credential(self,dt):
        self.root.get_screen('login').ids.password.text = ''
        self.login_password_error_message = 'Incorrect password'
    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
        self.hide_text_field('phone', screen='User')
        self.hide_text_field('smtp_server', screen='User')
        self.hide_text_field('smtp_port', screen='User')
        self.hide_text_field('sender_password', screen='User')
        self.hide_text_field('title', screen='User')
        return re.match(pattern, email) is not None
    def assist_send_code(self):
        thread = threading.Thread(target=self.send_code)
        thread.start()
    def change_to_code(self,dt):
        self.root.current = 'code'
    def send_code(self):
        if self.check_retrieve_email():
            self.code=send_code(self.root.get_screen('password').ids.email.text)
            Clock.schedule_once(self.change_to_code)
    def check_code(self):
        if self.root.get_screen('code').ids.code.text==self.code:
            self.root.current = 'changepassword'
        else:
            self.root.get_screen('code').ids.code.text=''
    def retrieve_password(self):
        self.root.get_screen('password').ids.email.text=self.root.get_screen('login').ids.email.text
        self.root.current = 'password'
    def on_confirmnewpassword_change(self,value):
        self.password_reset_error_message = 'The two password do not coincide'
        if self.root.get_screen('changepassword').ids.newpassword.text==value:
            self.password_reset_error_message =''
    def reset_password(self):
        if self.root.get_screen('changepassword').ids.newpassword.text==self.root.get_screen('changepassword').ids.confirmnewpassword.text:
            doc_ref = self.docs[self.fiel_values.index(self.root.get_screen('password').ids.email.text)]
            salesperson=doc_ref.id
            doc_path = doc_ref.path
            company_name = doc_path.split('/')[1]
            update_document(self.db, 'companies', company_name,'salespeople',salesperson, login_password=f"{self.root.get_screen('changepassword').ids.newpassword.text}")
            self.password_reset_error_message =''
            self.popup_title='Password Change Successful!'
            self.popup_text='You have successfully changed your password!'
            self.show_popup(0)
            self.root.current = 'login'
        else:
            self.root.get_screen('changepassword').ids.confirmnewpassword.text=''
            self.password_reset_error_message='The two password do not coincide'
    def use_text(self):
        self.group = self.text_fields['group'].text
        self.user=self.text_fields['name'].text
        self.n_mail=self.text_fields['number'].text
    def get_italian_brochures(self):
        self.italian_brochures, self.italian_docs = get_all_documents_field_in_collection(self.db, 'companies',
                                                                                          self.id, 'boards',
                                                                                          field='Brochure_i')
        self.new_italian_brochures, self.new_italian_docs = get_all_documents_field_in_collection(self.db,
                                                                                                  'companies',
                                                                                                  self.id,
                                                                                                  'attachments',
                                                                                                  field='Brochure_i')

    def validate_name(self,instance):
        self.sender_name=instance.text
        check,self.sender_email,self.phone,self.sender_title,self.login_password,self.sender_password,self.smtp_server,self.smtp_port=check_name(instance.text,self.db)
        self.check=check
        if check:
            try:
                self.hide_text_field('email')
            except:
                pass
            instance.helper_text = ''
            self.show_text_field('number', 'Quale email vuoi mandare?', 0.5, self.pos_n_mail,self.choose_italian_attachment)
            self.get_italian_brochures()
        else:
            try:
                self.hide_text_field('number')
            except:
                pass
            instance.helper_text='Name not in database. Enter your information.'
            instance.helper_text_color_normal="blue"
            self.switch_screen('User')
            try:
                text1=self.text_fields['name'].text
            except:
                text1=''
            self.text_fields['user_name'].text=text1
            self.show_text_field('email', 'What is your email?', 0.5, 0.75, on_validate_callback=self.ask_number, screen='User',height='38dp')

    def debug_focus_wrapper(self, callback):
        """ Wraps the callback to add debugging and ensure it's properly bound """

        def wrapper(instance, value):
            print(f"DEBUG: on_focus triggered for {instance}, Focused: {value}")
            callback(instance, value)

        return wrapper
    def esonerate_name(self,instance):
        check,self.sender_email,self.phone,self.sender_title,self.login_password,self.sender_password,self.smtp_server,self.smtp_port=check_name(instance.text,self.db)
        self.check=check
        if not check:
            instance.helper_text = ''
            self.show_text_field('email', 'What is your email?', 0.5, 0.74, on_validate_callback=self.ask_number, screen='User',height='38dp')
        else:
            instance.helper_text='Name already in database.'
            instance.helper_text_color_normal="blue"

    def ensure_writable_file(self, resource_name):
        resource_path = right_path(resource_name)
        writable_folder = self.user_data_dir
        writable_folder_path = Path(writable_folder)
        writable_folder_path.mkdir(parents=True, exist_ok=True)
        writable_file_path = writable_folder_path / resource_name
        if not writable_file_path.exists():
            copyfile(resource_path, writable_file_path)

        return writable_file_path
    def logout(self):
        resource_name = "remember_me.json"
        writable_json_path = self.ensure_writable_file(resource_name)
        with open(writable_json_path, 'w') as file:
            json.dump({}, file)
        self.root.current='login'
        self.root.get_screen('login').ids.email.text = ''
        self.root.get_screen('login').ids.password.text = ''
        self.hide_all(1)
        self.cancel_board_selection(1)
    def show_text_field(self,field_id,hint_text,pos_x,pos_y,on_validate_callback=None,text='',screen='Email',height='56dp',helper_text='',on_focus=None):
        text=str(text)
        if on_focus:
            text_field = MDTextField(
            MDTextFieldHintText(
                text=f'{hint_text}',
            ),
            MDTextFieldHelperText(
            text= f"{helper_text}",
            mode= "on_focus",),

            mode='outlined',
            size_hint_x= None,
            width="350dp",
            max_height=height,
            text=text,
            pos_hint={'center_x': pos_x, 'center_y': pos_y},
            on_focus=on_focus,)
        else:
            text_field = MDTextField(
                MDTextFieldHintText(
                    text=f'{hint_text}',
                ),
                MDTextFieldHelperText(
                    text=f"{helper_text}",
                    mode="on_focus", ),

                mode='outlined',
                size_hint_x=None,
                width="350dp",
                max_height=height,
                text=text,
                pos_hint={'center_x': pos_x, 'center_y': pos_y}, )
        if field_id not in self.text_fields:
            self.text_fields[field_id] = text_field
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen(screen).add_widget(text_field)

            if on_validate_callback:
                text_field.bind(on_text_validate=on_validate_callback)

        else:
            self.text_fields[field_id].text = ''

    def is_valid_phone_number(self, phone_number):
        phone_number=phone_number.replace(" ","")
        pattern = r'^\+\d+$'
        if re.match(pattern, phone_number):
            return True
        else:
            return False
    def add_contact(self):
        self.sender_email=self.text_fields['email'].text
        self.phone=self.text_fields['phone'].text
        title=self.text_fields['title'].text
        smtp_server = self.text_fields['smtp_server'].text
        smtp_port = self.text_fields['smtp_port'].text
        username=self.text_fields['user_name'].text
        add_row_to_database(self.db,self.text_fields['user_name'].text,title=title,sender_email=self.sender_email,phone=self.phone,sender_password=self.text_fields['sender_password'].text,smtp_server=smtp_server,smtp_port=smtp_port)
        self.popup_title='Success!'
        self.popup_text=f'{username} was added to your team!'
        self.show_popup(1)
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('User').ids.add_user.disabled = True
        self.hide_text_field('email',screen='User')
        self.hide_text_field('phone',screen='User')
        self.text_fields['user_name'].text=''
        self.hide_text_field('smtp_server',screen='User')
        self.hide_text_field('smtp_port',screen='User')
        self.hide_text_field('sender_password', screen='User')
        self.hide_text_field('title',screen='User')
    def check_email_number(self,text):
        text=text.lower()
        if text=='prima' or text=='seconda' or text=='terza' or text=='quarta' or text=='quinta' or text=='sesta':
            return True
        else:
            return False

    def choose_italian_attachment(self,instance):
        if self.check_email_number(instance.text):
            instance.helper_text = ''
            self.english_button_monitor=False
            self.italian_attachment_button = MDButton(MDButtonText(text='Attachment ita'), on_release=self.open_attachment_menu,pos_hint={"center_x": 0.38, "center_y": .2})
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').add_widget(self.italian_attachment_button)
        else:
            instance.text = ''

    def ask_user_number(self,instance):
        if self.is_valid_phone_number(instance.text):
            instance.helper_text = ''

            self.show_text_field('sender_password', "What's your email's password?", 0.5, 0.52, self.ask_password,screen='User',height='38dp')
        else:
            self.hide_text_field('smtp_server', screen='User')
            self.hide_text_field('smtp_port', screen='User')
            self.hide_text_field('sender_password', screen='User')
            self.hide_text_field('title', screen='User')
            instance.helper_text = 'Phone number not properly formatted. Check and try again.'
            instance.text = ''
            instance.helper_text_color_normal = "red"
    def ask_password(self,instance):
        self.show_text_field('title', 'Work title', 0.5, 0.41, text='Business Developer', screen='User',height='38dp')
        smtp_server = self.dic['smtp_server']
        smtp_port = self.dic['smtp_port']
        self.show_text_field('smtp_server', 'Smtp server', 0.5, 0.30, text=smtp_server, screen='User',height='38dp')
        self.show_text_field('smtp_port', 'Smtp port', 0.5, 0.19, text=smtp_port, screen='User',height='38dp')
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('User').ids.add_user.disabled = False
    def ask_number(self,instance):
        if self.is_valid_email(instance.text):
            self.show_text_field('phone', 'What is your phone number?', 0.5, 0.63,on_validate_callback=self.ask_user_number,helper_text='include country code ex.+39',screen='User',height='38dp')
        else:
            instance.text=''


    def hide_text_field(self, field_id,screen='Email'):
        try:
            if field_id in self.text_fields:
                text_field = self.text_fields[field_id]
                email_screen = self.root.get_screen('navigation').ids.nav_screen_manager.get_screen(screen)
                email_screen.remove_widget(text_field)
                del self.text_fields[field_id]
            else:
                email_screen = self.root.get_screen('navigation').ids.nav_screen_manager.get_screen(screen)
                if field_id in email_screen.ids:
                    text_field = email_screen.ids[field_id]
                    email_screen.remove_widget(text_field)
                    del email_screen.ids[field_id]
        except:
            print(f"couldn't delete field {field_id}")

    def check_create_df(self,instance):
        while True:
            try:
                if instance.text in self.group_names:
                    instance.helper_text = ''
                    self.show_text_field('name',"What is your full name?",0.5,self.pos_name,self.validate_name)
                    self.english_brochures, self.english_docs = get_all_documents_field_in_collection(self.db,
                                                                                                      'companies',
                                                                                                      self.id, 'boards',
                                                                                                      field='Brochure_c')
                    self.new_english_brochures, self.new_english_docs = get_all_documents_field_in_collection(self.db,
                                                                                                              'companies',
                                                                                                              self.id,
                                                                                                              'attachments',
                                                                                                              field='Brochure_c')

                else:
                    instance.helper_text='Group name does not exist. Check and try again.'
                    instance.text=''
                break
            except:
                x=1
    def update_label_text(self,dt):
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.sending_label.text = f'{self.i}/{self.total}'

    def disable_button(self, dt):
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.send_email.disabled = True
    def assist_download_update(self,*arg):
        thread = threading.Thread(target=self.download_update_help)
        thread.start()

    def download_file(self,file_id, destination_path):
        scope = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']
        credentials_doc = ServiceAccountCredentials.from_json_keyfile_name(right_path('docKey.json'), scope)
        service_drive = build('drive', 'v3', credentials=credentials_doc)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        request = service_drive.files().get_media(fileId=file_id)
        with io.FileIO(destination_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                self.update_progress=int(status.progress() * 100)
                try:
                    self.spinner.value = self.update_progress
                except:
                    x=1
                print(f"Download {int(status.progress() * 100)}%.")
        try:
            self.dialog.dismiss()
        except:
            x=1

    def download_update(self,file_id, version):
        new_file_name = f'Received {version}.exe'
        destination_path = os.path.join(os.getcwd(), new_file_name)
        self.download_file(file_id, destination_path)
        print('file downloaded')
        install_new_version(new_file_name, version)
        self.stop()
    def download_dialog_graphics(self,dt):
        self.update_progress=10
        self.spinner = MDLinearProgressIndicator(
            size_hint_x=0.3,
            size_hint_y=None,
            value=self.update_progress,
            pos_hint={'center_x': .5, 'center_y': .5},
        )
        self.dialog.clear_widgets()
        self.dialog.add_widget(self.spinner)
        self.spinner.start()
    def download_update_help(self):
        Clock.schedule_once(self.download_dialog_graphics)
        self.download_update(self.file_id,self.version)
    def show_update_prompt(self,version):
        self.headline=MDDialogHeadlineText(text="Update Available!")
        self.dialog = MDDialog(
            self.headline,
            MDDialogSupportingText(text=f'Version {version} is ready. Do you want to update?'),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Later"), on_release=self.close_dialog),
                MDButton(MDButtonText(text="Update"), on_release=self.assist_download_update),
                spacing="8dp",
            )
        )
        self.dialog.open()
    def show_popup(self,dt):
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=self.popup_title,
            ),
            MDDialogSupportingText(text=self.popup_text),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="OK"),
                    on_release=self.close_dialog,
                )
            ),
        )
        self.dialog.open()
    def create_popup_text(self,count,n_err):
        succ=count-n_err
        if succ==1:
            str1='email'
        else:
            str1='emails'
        if n_err==1:
            str2='email'
        else:
            str2='emails'
        if n_err!=0:
            popup_text = f"You have successully sent {count - n_err} {str1}, while it wasn't possible to send {n_err} {str2}."
        else:
            popup_text=f"You have successully sent {count} {str1}!"
        self.popup_text = popup_text
    def close_dialog(self, *args):
        self.dialog.dismiss()
    def send(self):

        thread = threading.Thread(target=self.invia)
        thread.start()

    def invia(self):
        self.use_text()
        Clock.schedule_once(self.disable_button)
        if not self.check:
            self.add_contact()
        df = create_df(self.group, self.Board_id, self.api_token, self.url, self.session,self.name_column,self.account_column,self.email_column)
        self.session.close()
        n_mail = self.n_mail.lower()
        if n_mail == 'prima':
            bodys = self.bodys[:2]
        elif n_mail == 'seconda':
            bodys = self.bodys[2:]
        Email = df[self.email_column]
        Name = df['Name']
        Account = df[self.account_column]
        Lingua = df[self.language_column]
        urls=self.urls
        errors = []
        n_err = 0
        count=len(Email)
        self.total=count
        if self.Brochure_i and not isinstance(self.Brochure_i,str):
            if isinstance(self.Brochure_c,str):
                self.Brochure_i=self.Brochure_c
            elif self.Brochure_c and not isinstance(self.Brochure_c,str):
                print('impossible')
            elif not self.Brochure_c:
                print('impossible')
        elif not self.Brochure_i:
            if self.Brochure_c and not isinstance(self.Brochure_c,str):
                print('impossible')
            elif not self.Brochure_c:
                print('no attachments')
            if isinstance(self.Brochure_c, str):
                print('no italian attachments')
        elif isinstance(self.Brochure_i,str):
            if self.Brochure_c:
                if isinstance(self.Brochure_c, str):
                    print('Both emails have distinct attachments')
                else:
                    self.Brochure_c=self.Brochure_i
            elif not self.Brochure_c:
                print('no enghlish attachments')

        Brochure_c_path=None
        if isinstance(self.Brochure_c, str):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                Brochure_c_path = temp_pdf.name
            self.download_file(self.Brochure_c,Brochure_c_path)
        Brochure_i_path=None
        if isinstance(self.Brochure_i, str):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf2:
                Brochure_i_path = temp_pdf2.name
            self.download_file(self.Brochure_i, Brochure_i_path)
        for i in range(count):
            self.i = i + 1
            Clock.schedule_once(self.update_label_text)
            if i==count-1:
                sleep(1)
            if Account[i]=='':
                n_err+=1
                Clock.schedule_once(self.update_label_text)
                continue
            try:
                n_err, errors=email_sender(Email[i], Name[i], Account[i], Lingua[i], self.smtp_server, self.sender_email, self.smtp_port,
                         self.sender_password, errors, n_mail, bodys, self.phone, n_err,Brochure_c_path,Brochure_i_path,self.attachment_name,self.prima_eng_subject,self.prima_ita_subject,self.seconda_eng_subject,self.seconda_ita_subject,self.sender_name,self.sender_title)
            except:
                n_err+=1
        try:
            os.remove(Brochure_i_path)
            os.remove(Brochure_c_path)
        except:
            x=1
        Clock.schedule_once(self.hide_all)
        Clock.schedule_once(self.cancel_board_selection)
        error_string=''
        for e in range(len(errors)):
            if e!=len(errors)-1:
                error_string+=errors[e]+','
            else:
                error_string += errors[e]
        today=datetime.today()
        year=str(today.year)
        month_number = today.month
        month_name = datetime(2024, month_number, 1).strftime("%B")
        today = today.strftime("%d-%m")
        formatted_time = datetime.now().strftime("%H:%M")
        today=today+' '+formatted_time
        self.create_popup_text(count,n_err)
        create_document(self.db,'companies',self.id,'Outbound Results',year,month_name, today,salesperson=self.user,board_name=self.board_name,group_name=self.group,number_successful=count-n_err,number_unsuccessful=n_err,name_of_unsuccessful=error_string)
        self.popup_title='Successful Outbound!'
        Clock.schedule_once(self.show_popup)
        Clock.schedule_once(self.assist_years)
    def cancel_board_selection(self,dt):
        self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.board_button.text = ""
    def hide_all(self,dt):
        try:
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').remove_widget(self.italian_attachment_button)
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').remove_widget(self.english_attachment_button)
            self.hide_text_field('group')
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').remove_widget(self.url_button)
            self.hide_text_field('name')
            self.hide_text_field('number')
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').ids.sending_label.text = ''
            self.root.get_screen('navigation').ids.nav_screen_manager.get_screen('Email').remove_widget(
                self.active_attachment_button)
        except Exception as e:
            x=1
ma = MainApp()
ma.run()