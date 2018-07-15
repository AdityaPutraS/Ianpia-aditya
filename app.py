from flask import Flask, request, abort
import os
import helperKartu
from PIL import Image

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)

app = Flask(__name__)

#Load variable lokal
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
kartu = helperKartu.loadGambar()
APP_ROOT = '/app'

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
                kartuPemain = helperKartu.bagiKartu(banyakPemain)
                if(os.path.exists(os.path.join(APP_ROOT,'test'))):
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test ada'))
                else:
                    os.mkdir(os.path.join(APP_ROOT,'test'))
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test tidak ada'))
				if(os.path.exists(os.path.join(APP_ROOT,'test'))):
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test ada'))
                else:
                    os.mkdir(os.path.join(APP_ROOT,'test'))
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test tidak ada'))
                '''
                #cek apakah dict kartu kosong
                if(kartu):
                    #tidak kosong
                    pass
                else:
                    #kosong
                    kartu = helperKartu.loadGambar()
                '''
                for i in range(0,banyakPemain):
                    gambar = helperKartu.gambarKartuDiTangan(360,kartu,kartuPemain[i])
                    pathGambar = os.path.join(APP_ROOT,'test',str(i)+'.png')
                    gambar.save(pathGambar)
                    urlGambar = request.host_url+os.path.join('test',str(i)+'.png')
                    line_bot_api.push_message(event.source.user_id,ImageSendMessage(original_content_url = urlGambar,preview_image_url = urlGambar))
                balas(event,'Done')
                '''
                for i in range(0,banyakPemain):
                    pathGambar = 'test/'+str(i)+'.png'
                    os.remove(pathGambar)
                    line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Done hapus '+str(i)))
                '''
    elif(isi == 'cekTest'):
        if(os.path.exists(os.path.join(APP_ROOT,'test'))):
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test ada'))
        else:
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test tidak ada'))
    elif(isi == 'hapusTest'):
        if(os.path.exists(os.path.join(APP_ROOT,'test'))):
            os.remove(os.path.join(APP_ROOT,'test'))
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test ada'))
        else:
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'Test tidak ada'))   
    elif(isi == 'debug'):
            line_bot_api.push_message(event.source.user_id,TextSendMessage(text = 'APP_ROOT : '+APP_ROOT))
if __name__ == "__main__":
    app.run()