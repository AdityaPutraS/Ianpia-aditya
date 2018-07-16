from flask import Flask, request, abort, send_from_directory
import os,shutil,json,math,errno
from time import gmtime, strftime
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
        kB = helperData.buka('static/'+'kB')
        waktuMulai = helperData.buka('static/'+'waktuMulai')
        line_bot_api.push_message(
            isiPostback[2], [
                TextSendMessage(text='gId : '+isiPostback[1]),
                TextSendMessage(text='uId : '+isiPostback[2])
            ]
        )
        if(isiPostback[1] in kB):
                if(isiPostback[2] in kB[isiPostback[1]]):
                    #sudah pernah gabung
                    line_bot_api.push_message(isiPostback[1],TextSendMessage(text = 'Game belum dimulai, mulai dengan ketik .kartuBohong'))
                else:
                    #belum pernah gabung
                    kB[isiPostback[1]][isiPostback[2]] = []
                    os.mkdir('static/'+isiPostback[1]+' '+waktuMulai[isiPostback[1]]+'/'+isiPostback[2])
                    helperData.simpan(kB,'static/'+'kB')
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
def buatDirAman(pathDir):
    try:
        os.mkdir(pathDir)
    except OSError as exc:
        pass
def hapusDirAman(pathDir,uID):
    try:
        shutil.rmtree(pathDir)
    except OSError as exc:
        pm(uID,'Hapus '+pathDir+' gagal')
def gambarImagemap(idGame,uID,tIM):
    waktuMulai = helperData.buka('static/waktuMulai')
    if(len(tIM)>=50):
        #kasus spesial
        path1='static/'+idGame+' '+waktuMulai[idGame]+'/'+uID
        path2='static/'+idGame+' '+waktuMulai[idGame]+'/'+uID+'_2'
        buatDirAman(path1)
        buatDirAman(path2)
        letak1 = helperKartu.genImagemap(path1,tIM[:25])
        letak2 = helperKartu.genImagemap(path2,tIM[25:])
        aksi1 = []
        for let in letak1:
            mesTmp = MessageImagemapAction(text='Kartu '+let[0],area=ImagemapArea(x=let[1][0],y=let[1][1],width=let[2][0],height=let[2][1]))
            aksi1.append(mesTmp)
        aksi2 = []
        for let in letak2:
            mesTmp = MessageImagemapAction(text='Kartu '+let[0],area=ImagemapArea(x=let[1][0],y=let[1][1],width=let[2][0],height=let[2][1]))
            aksi2.append(mesTmp)
        url1 = request.host_url+path1
        url2 = request.host_url+path2
        pm(uID,url2)
        line_bot_api.push_message(uID,[
            ImagemapSendMessage(base_url=url1,alt_text='Imagemap',base_size=BaseSize(width=1040,height=1040),actions=aksi1),
            ImagemapSendMessage(base_url=url2,alt_text='Imagemap',base_size=BaseSize(width=1040,height=1040),actions=aksi2)
            ]
        )
        hapusDirAman(path1,uID)
        hapusDirAman(path2,uID)
    else:
        aksi = []
        path1='static/'+idGame+' '+waktuMulai[idGame]+'/'+uID
        buatDirAman(path1)
        letak = helperKartu.genImagemap(path1,tIM)
        for let in letak:
            mesTmp = MessageImagemapAction(text='Kartu '+let[0],area=ImagemapArea(x=let[1][0],y=let[1][1],width=let[2][0],height=let[2][1]))
            aksi.append(mesTmp)
        line_bot_api.push_message(uID,[
            ImagemapSendMessage(base_url=request.host_url+path1,alt_text='Imagemap',base_size=BaseSize(width=1040,height=1040),actions=aksi)
            ]
        )
        hapusDirAman(path1,uID)
    
def tanya(idGame,Uid):
    kB = helperData.buka('static/'+'kB')
    kartuDiTangan = kB[idGame][Uid]
    line_bot_api.push_message(Uid,
        TextSendMessage(text='Klik kartu yang ingin kamu pilih (minimal 1,maksimal 4)')
    )
def pm(id,isi):
    line_bot_api.push_message(id,TextSendMessage(text=isi))
def getidGame(event):
    if isinstance(event.source,SourceGroup):
        idGame = event.source.group_id
    elif isinstance(event.source,SourceRoom):
        idGame = event.source.room_id
    else:
        idGame = ''
    return idGame
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    isi = event.message.text
    uId = event.source.user_id
    idGame = getidGame(event)
    
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
                
                kartuPemain = helperKartu.bagiKartu(banyakPemain)
                for i in range(0,banyakPemain):
                    gambar = helperKartu.gambarKartuDiTangan(360,kartuPemain[i])[0]
                    pathGambar = os.path.join('static','test',str(i)+'.png')
                    gambar.save(pathGambar)
                    urlGambar = request.host_url+os.path.join('static','test',str(i)+'.png')
                    urlPrev = request.host_url+os.path.join('static','res','clickDisini.jpg')
                    line_bot_api.push_message(event.source.user_id,ImageSendMessage(original_content_url = urlGambar,preview_image_url = urlPrev))
                balas(event,'Done')
    elif(isi == 'hapusTest'):
        shutil.rmtree('static/test')
    elif(isi == '.kartuBohong'):
        dataGameKartu = ''
        turn = helperData.buka('static/'+'turn')
        kB = helperData.buka('static/'+'kB')
        waktuMulai = helperData.buka('static/'+'waktuMulai')
        if(isinstance(event.source,SourceGroup) or isinstance(event.source,SourceRoom)):
            dataGameKartu = 'KB '+idGame+' '+uId
            if(idGame in kB):
                balas(event,'Game sudah dimulai, silahkan join dengan mengeklik tombol join')
            else:
                dirW = strftime("%Y%m%d%H%M%S", gmtime())
                os.mkdir(os.path.join(APP_ROOT,'static',idGame+' '+dirW))
                kB[idGame] = {}
                turn[idGame] = 1
                waktuMulai[idGame] = dirW
                helperData.simpan(kB,'static/'+'kB')
                helperData.simpan(turn,'static/'+'turn')
                helperData.simpan(waktuMulai,'static/'+'waktuMulai')
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
            waktuMulai = helperData.buka('static/'+'waktuMulai')
            if(idGame in waktuMulai):
                turn = helperData.buka('static/'+'turn')
                kB = helperData.buka('static/'+'kB')
                urutanMain = helperData.buka('static/'+'urutanMain')
                pilihan = helperData.buka('static/'+'pilihan')
                pilihan[idGame] = {}
                turn[idGame] = 0
                banyakPemain = len(kB[idGame])
                tmpKartu = helperKartu.bagiKartu(banyakPemain)
                no = 0
                urutan = ''
                tmpUrutan = []
                for pemain in kB[idGame]:
                    kB[idGame][pemain] = tmpKartu[no]
                    gambarImagemap(idGame,pemain,tmpKartu[no])
                    pilihan[idGame][pemain] = []
                    nama = line_bot_api.get_profile(pemain).display_name
                    tmpUrutan.append(pemain)
                    urutan = urutan + nama + '->'
                    no+=1
                urutan += 'Kembali ke awal'
                urutanMain[idGame] = tmpUrutan #berisi id urutan permainan di game dengan id : idGame seperti berikut ['Cqadadba1g31ev19..','1iufqjk9jfnk...',...]
                namaFirst = line_bot_api.get_profile(urutanMain[idGame][0]).display_name
                line_bot_api.push_message(idGame,[
                    TextSendMessage(text = 'Urutan bermain : '+urutan),
                    TextSendMessage(text = 'Dimulai dari kartu 2 (wajik,hati,sekop,keriting) oleh '+ namaFirst)
                    ]
                )
                helperData.simpan(kB,'static/'+'kB')
                helperData.simpan(turn,'static/'+'turn')
                helperData.simpan(urutanMain,'static/'+'urutanMain')
                helperData.simpan(pilihan,'static/'+'pilihan')
                tanya(idGame,urutanMain[idGame][0])
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    elif(isi[:6] == 'Kartu '):
        pilihan = helperData.buka('static/'+'pilihan')
        turn = helperData.buka('static/'+'turn')
        kB = helperData.buka('static/'+'kB')
        urutanMain = helperData.buka('static/'+'urutanMain')
        if (isinstance(event.source,SourceGroup) or isinstance(event.source,SourceRoom)):
            idGame = getidGame(event)
            pm(idGame,'Tidak bisa dilakukan di sini, harus di 1:1 chat')
        else:
            #cari idgame
            idGame = ''
            for id in kB:
                if(uId in kB[id]):
                    idGame = id
            #cek apakah pemain terdaftar di permainan
            if(idGame == ''):
                #tidak terdaftar
                pm(uId,'Anda belum ikut permainan dimanapun')
            else:
                #terdaftar
                tmpI,nomorKartu,tipeKartu = isi.split()
                #cek apakah sekarang gilirannya dia
                if(urutanMain[idGame][turn[idGame]] == uId):
                    #cek apakah yang dipilih sudah 4
                    if(len(pilihan[idGame][uId])==4):
                        listKartu = pilihan[idGame][uId][0]+', '+pilihan[idGame][uId][1]+', '+pilihan[idGame][uId][2]+', '+pilihan[idGame][uId][3]
                        confirm_template = ConfirmTemplate(text='Kamu sudah memilih 4 kartu, tekan submit untuk submit pilihan, ulang untuk mengulang memilih', actions=[
                            MessageAction(label='Submit', text='Gaskeun Bosq'),
                            MessageAction(label='Ulang', text='Aku mau ulang'),
                        ])
                        line_bot_api.push_message(uId,[
                            TextSendMessage(text = 'Pilihanmu adalah : '+listKartu),
                            TemplateSendMessage(alt_text='Sudah lebih dari 4', template=confirm_template)
                        ])
                    else:
                        #cek apakah beneran punya kartunya
                        namaKartu = nomorKartu+' '+tipeKartu
                        if(namaKartu in kB[idGame][uId]):
                            #valid
                            #cek apakah kartu sudah ada di pilihan
                            if(namaKartu in pilihan[idGame][uId]):
                                pm(uId,'Pilih kartu lain')
                            else:
                                pilihan[idGame][uId].append(namaKartu)
                                listKartu = ''
                                for l in pilihan[idGame][uId]:
                                    listKartu = listKartu + l + ', '
                                listKartu = listKartu[:len(listKartu)-2] #<- potong ', ' di akhir
                                confirm_template = ConfirmTemplate(text='Kamu sudah memilih '+str(len(pilihan[idGame][uId]))+' kartu, tekan submit untuk submit pilihan, ulang untuk mengulang memilih', actions=[
                                    MessageAction(label='Submit', text='Gaskeun Bosq'),
                                    MessageAction(label='Ulang', text='Aku mau ulang'),
                                ])
                                line_bot_api.push_message(uId,[
                                    TextSendMessage(text = 'Pilihanmu adalah : '+listKartu),
                                    TemplateSendMessage(alt_text='Pilihan kartu', template=confirm_template)
                                ])
                        else:
                            #tidak valid
                            balas(event,'Kamu tidak punya kartu '+namaKartu)
                else:
                    balas(event,'Sekarang bukan giliranmu')
                helperData.simpan(kB,'static/'+'kB')
                helperData.simpan(turn,'static/'+'turn')
                helperData.simpan(urutanMain,'static/'+'urutanMain')
                helperData.simpan(pilihan,'static/'+'pilihan')
    elif(isi == '.berhenti'):
        #check apakah game sudah ada
        if(idGame == ''):
            balas(event,'Tidak bisa digunakan di 1:1 chat')
        else:
            waktuMulai = helperData.buka('static/'+'waktuMulai')
            if(idGame in waktuMulai):
                hapusDirAman('static/'+idGame+' '+waktuMulai[idGame],uId)
                kB = helperData.buka('static/'+'kB')
                turn = helperData.buka('static/'+'turn')
                urutanMain = helperData.buka('static/'+'urutanMain')
                pilihan = helperData.buka('static/'+'pilihan')
                del kB[idGame]
                del turn[idGame]
                del urutanMain[idGame]
                del pilihan[idGame]
                del waktuMulai[idGame]
                helperData.simpan(kB,'static/'+'kB')
                helperData.simpan(turn,'static/'+'turn')
                helperData.simpan(urutanMain,'static/'+'urutanMain')
                helperData.simpan(pilihan,'static/'+'pilihan')
                helperData.simpan(waktuMulai,'static/'+'waktuMulai')
                balas(event,'Game berhenti')
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    #fungsi debug
    elif(isi == 'listGame'):
        game = ''
        kB = helperData.buka('static/'+'kB')
        for i in kB:
            game = game + i + '\n'
        balas(event,game)
    elif(isi == 'listPemain'):
        pemain = ''
        kB = helperData.buka('static/'+'kB')
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
    elif(isi == 'imagemap'):
        tIM = helperKartu.bagiKartu(1)
        gambarImagemap(idGame,event.source.user_id,tIM[0])
if __name__ == "__main__":
    app.run()