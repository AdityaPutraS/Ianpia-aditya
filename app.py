from flask import Flask, request, abort
import os,shutil,json
import helperKartu,helperData
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
kB = {}
turn = {}
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
                    kB = buka('static/'+'kB')
                    kB[isiPostback[1]][isiPostback[2]] = []
                    simpan(kB,'static/'+'kB')
                    line_bot_api.push_message(
                        isiPostback[1], TextSendMessage(text=nama + ' berhasil bergabung')
                    )
        else:
            line_bot_api.push_message(isiPostback[1],TemplateSendMessage(text = 'Game belum dimulai, mulai dengan ketik .kartuBohong'))
def balas(event,pesan):
    line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=pesan)
            )
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    isi = event.message.text
    
    if isinstance(event.source,SourceGroup):
        idGame = event.source.group_id
    elif isinstance(event.source,SourceRoom):
        idGame = event.source.room_id
    else:
        idGame = ''
    
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
                    shutil.rmtree('static/test')
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
                    line_bot_api.push_message(event.source.user_id,ImageSendMessage(original_content_url = urlGambar,preview_image_url = urlGambar))
                balas(event,'Done')
    elif(isi == 'hapusTest'):
        shutil.rmtree('static/test')
    elif(isi == '.kartuBohong'):
        uId = event.source.user_id
        dataGameKartu = ''
        if(isinstance(event.source,SourceGroup) or isinstance(event.source,SourceRoom)):
            dataGameKartu = 'KB '+idGame+' '+uId
            if(idGame in kB):
                balas(event,'Game sudah dimulai, silahkan join dengan mengeklik tombol join')
            else:
                os.mkdir(os.path.join(APP_ROOT,'static',idGame))
                kB[idGame] = {}
                turn[idGame] = 0
                simpan(kB,'static/'+'kB')
                simpan(turn,'static/'+'turn')
                buttons_template = ButtonsTemplate(
                    title='Join game Kartu Bohong', text='Klik untuk bergabung', actions=[
                        PostbackAction(label='Join', data=dataGameKartu),
                    ])
                template_message = TemplateSendMessage(
                    alt_text='Kartu Bohong', template=buttons_template)
                line_bot_api.reply_message(event.reply_token, template_message)
        else:
            balas(event,'Tidak bisa memulai permainan di 1:1 chat')    
    elif(isi == '.mulai'):
        if(idGame == ''):
            balas(event,'Tidak bisa digunakan di 1:1 chat')
        else:
            if(os.path.exists(os.path.join(APP_ROOT,'static',idGame))):
                turn = buka('static/'+'turn')
                kB = buka('static/'+'kB')
                turn[idGame] = 0
                banyakPemain = len(kB[idGame])
                tmpKartu = helperKartu.bagiKartu(banyakPemain)
                no = 0
                for pemain in kB[idGame]:
                    os.mkdir(os.path.join(APP_ROOT,'static',idGame,pemain))
                    kb[idGame][pemain] = tmpKartu[no]
                    gambar = helperKartu.gambarKartuDiTangan(360,kartu,tmpKartu[no])
                    pathGambar = os.path.join('static',idGame,pemain,turn[idGame]+'.png')
                    gambar.save(pathGambar)
                    urlGambar = request.host_url+pathGambar
                    line_bot_api.push_message(pemain,[
                        TextSendMessage(text='Ini Kartumu'),
                        ImageSendMessage(original_content_url = urlGambar,preview_image_url = urlGambar)
                        ]
                    )
                    no += 1
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
            
    elif(isi == '.berhenti'):
        #check apakah game sudah ada
        if(idGame == ''):
            balas(event,'Tidak bisa digunakan di 1:1 chat')
        else:
            if(os.path.exists(os.path.join(APP_ROOT,'static',idGame))):
                shutil.rmtree('static/'+idGame)
                kB = buka('static/'+'kB')
                turn = buka('static/'+'turn')
                del kB[idGame]
                del turn[idGame]
                simpan(kB,'static/'+'kB')
                simpan(turn,'static/'+'turn')
                balas(event,'Game berhenti')
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    #fungsi debug
    elif(isi == 'listGame'):
        game = ''
        kB = buka('static/'+'kB')
        for i in kB:
            game = game + i + '\n'
        balas(event,game)
    elif(isi == 'listPemain'):
        pemain = ''
        kB = buka('static/'+'kB')
        for i in kB[idGame] :
            pemain = pemain + i + '\n'
        balas(event,pemain)
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