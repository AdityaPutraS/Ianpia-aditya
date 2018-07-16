from flask import Flask, request, abort
import os,shutil
import helperKartu
from PIL import Image

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
'''from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,TemplateSendMessage,ButtonsTemplate
)'''

app = Flask(__name__)

#Load variable lokal
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
APP_ROOT = '/app'
kartu = helperKartu.loadGambar()
#Bare minimum
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
    
@handler.add(PostbackEvent)
def handle_postback(event):
    isiPostback = event.postback.data.split()
    nama = line_bot_api.get_profile(isiPostback[2]).display_name
    if isiPostback[0] == 'KB':
        line_bot_api.push_message(
            isiPostback[2], [
                TextSendMessage(text='gId : '+isiPostback[1]),
                TextSendMessage(text='uId : '+isiPostback[2])
            ]
        )
        if(os.path.exists(os.path.join(APP_ROOT,'static',isiPostback[1]))):
                if(os.path.exists(os.path.join(APP_ROOT,'static',isiPostback[1],isiPostback[2]))):
                    #sudah pernah gabung
                    line_bot_api.push_message(isiPostback[1],TemplateSendMessage(text = 'Game belum dimulai, mulai dengan ketik .kartuBohong'))
                else:
                    #belum pernah gabung
                    os.mkdir(os.path.join(APP_ROOT,'static',isiPostback[1],isiPostback[2]))
        else:
            line_bot_api.push_message(isiPostback[1],TemplateSendMessage(text = 'Game belum dimulai, mulai dengan ketik .kartuBohong'))
        line_bot_api.push_message(
            isiPostback[1], TextSendMessage(text=nama + ' berhasil bergabung')
            )
def balas(event,pesan):
    line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=pesan)
            )
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    isi = event.message.text
    if('bagiKartu' in isi):
        banyakPemain = int(isi[10:][:len(isi)-11]) #bagiKartu(10) <--- mengambil hanya 10 nya saja
        if(banyakPemain > 7):
            balas(event,'Pemain maksimal 7 orang')
        else:
            if(banyakPemain < 2):
                balas(event,'Pemain minimal 2 orang')
            else:
                #Jumlah pemain valid
                
                if(os.path.exists(os.path.join(APP_ROOT,'static','test'))):
                    pass
                else:
                    os.mkdir(os.path.join(APP_ROOT,'static','test'))
                '''
                #cek apakah dict kartu kosong
                if(kartu):
                    #tidak kosong
                    pass
                else:
                    #kosong
                    kartu = helperKartu.loadGambar()
                '''
                kartuPemain = helperKartu.bagiKartu(banyakPemain)
                for i in range(0,banyakPemain):
                    gambar = helperKartu.gambarKartuDiTangan(360,kartu,kartuPemain[i])
                    pathGambar = os.path.join('static','test',str(i)+'.png')
                    gambar.save(pathGambar)
                    urlGambar = request.host_url+os.path.join('static','test',str(i)+'.png')
                    line_bot_api.push_message(event.source.user_id,ImageSendMessage(original_content_url = urlGambar,preview_image_url = None))
                balas(event,'Done')
    elif(isi == 'hapusTest'):
        shutil.rmtree('static/test')
    elif(isi == '.kartuBohong'):
        uId = event.source.user_id
        valid = False
        tipe = ''
        dataGameKartu = ''
        if(isinstance(event.source,SourceGroup)):
            gId = event.source.group_id
            valid = True
            tipe = 'g'
            dataGameKartu = 'KB '+gId+' '+uId
            if(os.path.exists(os.path.join(APP_ROOT,'static',gId))):
                pass
            else:
                os.mkdir(os.path.join(APP_ROOT,'static',gId))
        elif(isinstance(event.source,SourceRoom)):
            rId = event.source.room_id
            valid = True
            tipe = 'r'
            dataGameKartu = 'KB '+rId+' '+uId
            if(os.path.exists(os.path.join(APP_ROOT,'static',rId))):
                pass
            else:
                os.mkdir(os.path.join(APP_ROOT,'static',rId))
        else:
            balas(event,'Tidak bisa memulai permainan di 1:1 chat')
        #Kirim button ke group/room
        if(valid):            
            buttons_template = ButtonsTemplate(
                title='Join game Kartu Bohong', text='Klik untuk bergabung', actions=[
                    PostbackAction(label='Join', data=dataGameKartu),
                ])
            template_message = TemplateSendMessage(
                alt_text='Kartu Bohong', template=buttons_template)
            line_bot_api.reply_message(event.reply_token, template_message)
    elif(isi == '.mulai'):
        pass
    elif(isi == '.berhenti'):
        #check apakah game sudah ada
        if isinstance(event.source,SourceGroup):
            idGame = event.source.group_id
        elif isinstance(event.source,SourceRoom):
            idGame = event.source.room_id
        else:
            idGame = ''
        if(idGame == ''):
            balas(event,'Tidak bisa digunakan di 1:1 chat')
        else:
            if(os.path.exists(os.path.join(APP_ROOT,'static',idGame))):
                shutil.rmtree('static/'+idGame)
                balas(event,'Game berhenti')
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    elif(isi == 'appRoot'):
        text = ''
        for i in os.listdir():
            text = text + i + ' '
        balas(event,text)
    elif(isi == 'static'):
        text = ''
        for i in os.listdir('static'):
            text = text + i + ' '
        balas(event,text)
if __name__ == "__main__":
    app.run()