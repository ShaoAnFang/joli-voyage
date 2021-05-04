#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
import re
import time
import json
# import pytz 
import random
import requests
import datetime

from bs4 import BeautifulSoup
from imgurpython import ImgurClient
from flask import Flask, request, abort
from flask_restful import Api
from oauth2client.service_account import ServiceAccountCredentials
from Module import Aime, Constellation, Movies, TemplateSend, Sticker
from Controller.liff_controller import LiffController

sendTime = time.time()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
#from linebot.models import (
#    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage
#)

app = Flask(__name__)

line_bot_api = LineBotApi('Ho0wK3dDGmaNUUkv+HyrJokY2SJ1PvwpeMnn4T4AwVlYOggWEgJyuPr1bgKe0YhHpCK+2l23H8JdTmVucBUp1L/Sxulr1yOGpZ6QYcRWk7ExarH9lML4th4FWApcz34JjbOwdhPsHNf/h7ndyfiXTgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ba9ccaf4c6bbfa15ac4e27f3a36f2e53')

api = Api(app)
#https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
liff_routes = [
    '/liff/shared',
    '/liff/shared/<string:name><string:title><string:cellphone><string:mail><string:phone>',
]
api.add_resource(LiffController, *liff_routes)
api.init_app(app)

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

@app.route('/GGWP', methods=['GET'])
def test():
    return "Hello World!"

@app.route('/star/<string:star>', methods=['GET'])
def getConstellation(star):
    resultString = Constellation.constellation(star)
    return resultString

@app.route('/movie', methods=['GET'])
def get_movies():
    movies = Movies.get_movies()
    return movies

def sticker(key):
    searchResult = Sticker.sticker(key)
    return searchResult

#存取imgur
def aime(key):
    imgurResult = Aime.aime(key)
    return imgurResult

def handsome():
    client_id = 'c3e767d450a401e'
    client_secret = 'cdf5fb70e82bc00e65c0d1d1a4eed318ae82024c'
    client = ImgurClient(client_id,client_secret)
    images = client.get_album_images('hjCtM')
    index = random.randint(0, len(images) - 1)
    return images[index].link

# LocationMessage
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event): 
    locationInfo = '地區:' + event.message.address[:20] + '\n\n'
    locationInfo += '經緯度: ' '(' + str(event.message.longitude)[:10] +' ,'+ str(event.message.latitude)[:10] + ' )'+ '\n\n'
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=locationInfo)) 
    
@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event): 
    sticker_message = StickerSendMessage(
        package_id = event.message.package_id,
        sticker_id = event.message.sticker_id
    )
    line_bot_api.reply_message(event.reply_token, sticker_message)


@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event): 
    msgType = event.message.type
    id = event.message.id
    m = 'msgType:' + msgType + '\n' + 'id:' + id
    url = 'https://api.line.me/v2/bot/message/{}/content'.format(id)
    headers =  {'Authorization':'Bearer E3V1P2J74V3qQ5VQsR0Au27E+NwBBlnh8r24mpP5vbkrogwj7PFroxNAKS9MU2iBeDMJiEFiaqe0SvKypYsoPcr70wVac/v4FJfXa1TwGPo0QeI1fkZcaejhJSz09aetC0TaMsblhNOorJaG4J/RlwdB04t89/1O/w1cDnyilFU=' }
    response = requests.get(url, headers=headers)
    #print(response)
    with open('{}.m4a'.format(id), 'wb') as f:
        f.write(response.content)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=m))
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
 
    if msg == '離開房間':
        roomID = event.source.room_id
        line_bot_api.leave_room(roomID)
        
    if msg == 'help':
        menulist = 'Hello 歡迎加入Joli 啾玩小日子 你可以 \n'
        menulist += '1. 輸入 joli 或 啾 查看最新文章\n\n'
        menulist += '2. 輸入 星座 天蠍\n\n'
        menulist += '3. 輸入 電影\n\n'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=menulist))
    
    if msg[0] == '星' and msg[1] == '座' and msg[2] == ' ':
        star = msg.split('星座 ')[1]
        constellationResult = getConstellation(star)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=constellationResult))

    # if msg == '時間':
    #     tz = pytz.timezone('Asia/Taipei')
    #     dd = datetime.datetime.now(tz).date()
    #     dt = datetime.datetime.now(tz).time()
    #     queryTime = "{}-{}-{} {}:{}".format(dd.year,dd.month,dd.day,dt.hour,dt.minute)
    #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=queryTime))
    
    if msg== 'Id' or msg== 'id':
        #if event.source.type =='group':
        #    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.source.group_id))
        #else: 

        profile = line_bot_api.get_profile(event.source.user_id)
        n = profile.display_name
        p = profile.picture_url
        i = profile.user_id
        m = profile.status_message
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text= n))

        if not m:
            z = n + '\n \n' + p + '\n \n' + '\n \n' + event.source.user_id
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text= z))
        else: 
            z = n + '\n \n' + p + '\n \n' + m + '\n \n' + event.source.user_id
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text= z))

    if msg == '電影':
        if event.source.type == 'group' :
            if event.source.group_id == 'C54f882fec4c5b8dc538b6d1cee5fc31f' :
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=''))
        g = get_movies()
        carousel_template_message = TemplateSend.moive(g)
        line_bot_api.reply_message(event.reply_token, carousel_template_message)
        
    if msg == 'joli' or msg == 'Joli' or msg == '啾' or msg == '最新文章':
        flex_message = TemplateSend.chloeStyleOne()
        if random.randint(1, 2) != 1:
            flex_message = TemplateSend.chloeStyleTwo()
        line_bot_api.reply_message(event.reply_token, flex_message)
            
    if sticker(msg) != 'GG':
        if event.source.type !='group':
            sticker_message = StickerSendMessage(
            package_id = sticker(msg)['package_id'],
            sticker_id = sticker(msg)['sticker_id']
            )
            line_bot_api.reply_message(event.reply_token, sticker_message)
        
        elif not event.source.group_id in quietArr :
            sticker_message = StickerSendMessage(
            package_id = sticker(msg)['package_id'],
            sticker_id = sticker(msg)['sticker_id']
            )
            line_bot_api.reply_message(event.reply_token, sticker_message)
            
if __name__ == "__main__":
    app.run()
