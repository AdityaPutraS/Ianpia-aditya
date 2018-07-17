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
uId_admin = os.getenv('UID_ADITYA',None)
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
    sumber = event.source.user_id
    if isiPostback[0] == 'KB':
        isiPostback.append(sumber)
        kB = helperData.buka('static/var/'+'kB')
        waktuMulai = helperData.buka('static/var/'+'waktuMulai')
        '''
        line_bot_api.push_message(
            isiPostback[2], [
                TextSendMessage(text='gId : '+isiPostback[1]),
                TextSendMessage(text='uId : '+isiPostback[2])
            ]
        )
        '''
        if(isiPostback[1] in kB):
                if(isiPostback[2] in kB[isiPostback[1]]):
                    #sudah pernah gabung
                    line_bot_api.push_message(isiPostback[1],TextSendMessage(text = 'Kamu sudah gabung, ketik .mulai untuk mulai'))
                else:
                    #cek apakah game sudah mulai
                    mulai = helperData.buka('static/var/'+'mulai')
                    if(mulai[isiPostback[1]]):
                        pm(isiPostback[0],'Game sudah mulai, '+line_bot_api.get_profile(sumber).display_name+' tidak bisa bergabung')
                    else:
                        #belum pernah gabung
                        kB[isiPostback[1]][isiPostback[2]] = []
                        urutanMain = helperData.buka('static/var/'+'urutanMain')
                        urutanMain[isiPostback[1]].append(sumber)
                        helperData.simpan(urutanMain,'static/var/'+'urutanMain')
                        #os.mkdir('static/'+isiPostback[1]+'-'+waktuMulai[isiPostback[1]]+'/'+isiPostback[2])
                        helperData.simpan(kB,'static/var/'+'kB')
                        nama = line_bot_api.get_profile(isiPostback[2]).display_name
                        line_bot_api.push_message(
                            isiPostback[1], TextSendMessage(text=nama + ' berhasil bergabung')
                        )
        else:
            line_bot_api.push_message(isiPostback[1],TemplateSendMessage(text = 'Game belum dimulai, mulai dengan ketik .kartuBohong.'))
    elif isiPostback[0] == 'Bohong':
        #cek apakah sudah ada yang menekan sebelumya
        bohong = helperData.buka('static/var/'+'bohong')
        idGame = isiPostback[2]
        uId = isiPostback[3]
        cekBohong = isiPostback[4]
        if(bohong[idGame]):
            #sudah ada yang menekannya duluan
            pm(sumber,'Sudah ditekan orang lain coy')
        else:
            #cek apakah di tumpukan beneran ada kartu
            stackGame = helperData.buka('static/var/'+'stackGame')
            if(len(stackGame[idGame])==0):
                pm(sumber,'Gausah ngegas, masih kosong gitu lho tumpukannya')
            else:
                bohong[idGame] = True
                helperData.simpan(bohong,'static/var/'+'bohong')
                #cek apakah player sebelumnya bohong
                #data='Bohong '+str(banyakKartuDiTambah)+' '+idGame+' '+uId),
                kB = helperData.buka('static/var/'+'kB')
                turn = helperData.buka('static/var/'+'turn')
                urutanMain = helperData.buka('static/var/'+'urutanMain')
                pm(uId_admin,'len(stackgame[idgame])='+str(len(stackGame[idGame])))
                pm(uId_admin,'isi postback1 ='+isiPostback[1])
                tmpKartuGame = stackGame[idGame][len(stackGame[idGame])-int(isiPostback[1]):]
                bersalah = False
                for t in tmpKartuGame:
                    #cek satu per satu
                    nomor,tipe = t.split()
                    if(nomor != cekBohong):
                        bersalah = True
                if(bersalah):
                    #tambah semua kartu ke yang berbohong
                    pm(idGame,line_bot_api.get_profile(uId).display_name+' berbohong, sebagai hukumannya, kartu di tangannya ditambah dengan semua kartu yang ada di tumpukan')
                    pm(uId,'Dosa euy')
                    kB[idGame][uId] += stackGame[idGame]
                    stackGame[idGame] = []
                    pm(idGame,'Karena '+line_bot_api.get_profile(sumber).display_name+' benar menebak, sekarang adalah gilirannya')
                    turn[idGame] = urutanMain[idGame].index(sumber)
                    helperData.simpan(turn,'static/var/'+'turn')
                    #pc semua pemain bahwa giliran berubah
                    for pemain in urutanMain[idGame]:
                        if(pemain == sumber):
                            pass
                        else:
                            pc(pemain,'Giliran ganti menjadi '+line_bot_api.get_profile(sumber).display_name)
                    pm(idGame,'Kartu sekarang adalah : '+curCard[idGame]+' (hati,wajik,sekop,keriting)')
                    bohong[idGame] = False
                    helperData.simpan(bohong,'static/var/'+'bohong')
                    helperData.simpan(kB,'static/var/'+'kB')
                    helperData.simpan(stackGame,'static/var/'+'stackGame')
                    helperData.simpan(curCard,'static/var/'+'curCard')
                    tanya(idGame,sumber)
                else:
                    #tambah semua kartu ke yang menuduh
                    pm(idGame,line_bot_api.get_profile(sumber).display_name+' sudah menuduh orang, dan dia salah.Sebagai hukumannya, kartu di tangannya ditambah dengan semua kartu yang ada di tumpukan')
                    pm(sumber,'Ea salah')
                    kB[idGame][sumber] += stackGame[idGame]
                    stackGame[idGame] = []
                    turn[idGame] = (turn[idGame]+1)%len(kB[idGame]) #<- menaikkan 1 turn, akan kembali ke 0 jika sudah sampai pemain terakhir
                    helperData.simpan(turn,'static/var/'+'turn')
                    pm(idGame,'Karena penuduh salah,giliran dilanjutkan seperti biasa.Sekarang adalah giliran '+line_bot_api.get_profile(urutanMain[idGame][turn[idGame]]).display_name)
                    pm(idGame,'Kartu sekarang adalah : '+curCard[idGame]+' (hati,wajik,sekop,keriting)')
                    bohong[idGame] = False
                    helperData.simpan(bohong,'static/var/'+'bohong')
                    helperData.simpan(kB,'static/var/'+'kB')
                    helperData.simpan(stackGame,'static/var/'+'stackGame')
                    helperData.simpan(curCard,'static/var/'+'curCard')
                    helperData.simpan(turn,'static/var/'+'turn')
                    tanya(idGame,urutanMain[idGame][turn[idGame]])
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
        shutil.rmtree(pathDir,ignore_errors=True)
    except OSError as exc:
        #ganti jadi pass setelah game selesai
        pm(uID,'Hapus '+pathDir+' gagal')
def hapusSemuaImagemap(idGame):
    waktuMulai = helperData.buka('static/var/'+'waktuMulai')
    hapusDirAman('static/'+idGame+'-'+waktuMulai[idGame],uId_admin)
    os.mkdir('static/'+idGame+'-'+waktuMulai[idGame])
def gambarImagemap(idGame,uID,tIM):
    waktuMulai = helperData.buka('static/var/'+'waktuMulai')
    turn = helperData.buka('static/var/'+'turn')
    urutanMain = helperData.buka('static/var/'+'urutanMain')
    tokenImagemap = strftime("%M%S", gmtime())
    if(len(tIM)>=50):
        #kasus spesial
        path1='static/'+idGame+'-'+waktuMulai[idGame]+'/'+uID+tokenImagemap
        path2='static/'+idGame+'-'+waktuMulai[idGame]+'/'+uID+'_2'+tokenImagemap
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
        pesan = [
                ImagemapSendMessage(base_url=url1,alt_text='Kartumu',base_size=BaseSize(width=1040,height=1040),actions=aksi1),
                ImagemapSendMessage(base_url=url2,alt_text='Kartumu',base_size=BaseSize(width=1040,height=1040),actions=aksi2),
                ]
        line_bot_api.push_message(uID,pesan)
    else:
        aksi = []
        path1='static/'+idGame+'-'+waktuMulai[idGame]+'/'+uID+tokenImagemap
        buatDirAman(path1)
        letak = helperKartu.genImagemap(path1,tIM)
        for let in letak:
            mesTmp = MessageImagemapAction(text='Kartu '+let[0],area=ImagemapArea(x=let[1][0],y=let[1][1],width=let[2][0],height=let[2][1]))
            aksi.append(mesTmp)
        url1 = request.host_url+path1
        pesan = [
                ImagemapSendMessage(base_url=url1,alt_text='Kartumu',base_size=BaseSize(width=1040,height=1040),actions=aksi),
                ]
        line_bot_api.push_message(uID,pesan)
def tanya(idGame,Uid):
    kB = helperData.buka('static/var/'+'kB')
    kartuDiTangan = kB[idGame][Uid]
    pm(Uid,'Sekarang giliramu')
    gambarImagemap(idGame,Uid,kartuDiTangan)
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
        turn = helperData.buka('static/var/'+'turn')
        kB = helperData.buka('static/var/'+'kB')
        waktuMulai = helperData.buka('static/var/'+'waktuMulai')
        stackGame = helperData.buka('static/var/'+'stackGame')
        bohong = helperData.buka('static/var/'+'bohong')
        curCard = helperData.buka('static/var/'+'curCard')
        urutanMain = helperData.buka('static/var/'+'urutanMain')
        lastPlayer = helperData.buka('static/var/'+'lastPlayer')
        mulai = helperData.buka('static/var/'+'mulai')
        if(isinstance(event.source,SourceGroup) or isinstance(event.source,SourceRoom)):
            dataGameKartu = 'KB '+idGame
            if(idGame in kB):
                balas(event,'Game sudah dimulai, silahkan join dengan mengeklik tombol join')
            else:
                dirW = strftime("%Y%m%d%H%M%S", gmtime())
                os.mkdir(os.path.join(APP_ROOT,'static',idGame+'-'+dirW))
                kB[idGame] = {}
                turn[idGame] = 0
                waktuMulai[idGame] = dirW
                urutanMain[idGame] = []
                stackGame[idGame] = []
                mulai[idGame] = False
                lastPlayer[idGame] = ''
                curCard[idGame] = helperKartu.urutan[0]
                bohong[idGame] = False
                helperData.simpan(mulai,'static/var/'+'mulai')
                helperData.simpan(lastPlayer,'static/var/'+'lastPlayer')
                helperData.simpan(urutanMain,'static/var/'+'urutanMain')
                helperData.simpan(bohong,'static/var/'+'bohong')
                helperData.simpan(stackGame,'static/var/'+'stackGame')
                helperData.simpan(curCard,'static/var/'+'curCard')
                helperData.simpan(kB,'static/var/'+'kB')
                helperData.simpan(turn,'static/var/'+'turn')
                helperData.simpan(waktuMulai,'static/var/'+'waktuMulai')
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
            waktuMulai = helperData.buka('static/var/'+'waktuMulai')
            if(idGame in waktuMulai):
                turn = helperData.buka('static/var/'+'turn')
                kB = helperData.buka('static/var/'+'kB')
                urutanMain = helperData.buka('static/var/'+'urutanMain')
                pilihan = helperData.buka('static/var/'+'pilihan')
                mulai = helperData.buka('static/var/'+'mulai')
                pilihan[idGame] = {}
                banyakPemain = len(kB[idGame])
                tmpKartu = helperKartu.bagiKartu(banyakPemain)
                no = 0
                urutan = ''
                #tmpUrutan = []
                for pemain in kB[idGame]:
                    kB[idGame][pemain] = tmpKartu[no]
                    pilihan[idGame][pemain] = []
                    nama = line_bot_api.get_profile(pemain).display_name
                    #tmpUrutan.append(pemain)
                    urutan = urutan + nama + '->'
                    no+=1
                urutan += 'Kembali ke awal'
                #urutanMain[idGame] = tmpUrutan #berisi id urutan permainan di game dengan id : idGame seperti berikut ['Cqadadba1g31ev19..','1iufqjk9jfnk...',...]
                mulai[idGame] = True
                helperData.simpan(mulai,'static/var/'+'mulai')
                helperData.simpan(kB,'static/var/'+'kB')
                helperData.simpan(turn,'static/var/'+'turn')
                helperData.simpan(urutanMain,'static/var/'+'urutanMain')
                helperData.simpan(pilihan,'static/var/'+'pilihan')
                idFirst = urutanMain[idGame][0]
                namaFirst = line_bot_api.get_profile(idFirst).display_name
                for pemain in urutanMain[idGame]:
                    gambarImagemap(idGame,pemain,kB[idGame][pemain])
                line_bot_api.push_message(idGame,[
                    TextSendMessage(text = 'Urutan bermain : '+urutan),
                    TextSendMessage(text = 'Dimulai dari kartu 2 (wajik,hati,sekop,keriting) oleh '+ namaFirst)
                    ]
                )
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    elif(isi[:6] == 'Kartu '):
        pilihan = helperData.buka('static/var/'+'pilihan')
        turn = helperData.buka('static/var/'+'turn')
        kB = helperData.buka('static/var/'+'kB')
        urutanMain = helperData.buka('static/var/'+'urutanMain')
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
                    curCard = helperData.buka('static/var/'+'curCard')
                    pm(uId,'Kartu yang seharusnya kamu keluarkan sekarang adalah : '+curCard[idGame]+' (hati,wajik,sekop,keriting). Kamu juga bisa berbohong dengan memilih kartu lain')
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
                helperData.simpan(kB,'static/var/'+'kB')
                helperData.simpan(turn,'static/var/'+'turn')
                helperData.simpan(urutanMain,'static/var/'+'urutanMain')
                helperData.simpan(pilihan,'static/var/'+'pilihan')
    elif(isi == 'Aku mau ulang'):
        pilihan = helperData.buka('static/var/'+'pilihan')
        kB = helperData.buka('static/var/'+'kB')
        #cari idGame
        idGame = ''
        for id in kB:
            if(uId in kB[id]):
                idGame = id
        if(idGame == ''):
            balas(event,'Gabung dulu mas')
        else:
            pilihan[idGame][uId] = []
            pm(uId,'Silahkan pilih lagi')
        helperData.simpan(pilihan,'static/var/'+'pilihan')    
    elif(isi == 'Gaskeun Bosq'):
        pilihan = helperData.buka('static/var/'+'pilihan')
        turn = helperData.buka('static/var/'+'turn')
        kB = helperData.buka('static/var/'+'kB')
        urutanMain = helperData.buka('static/var/'+'urutanMain')
        waktuMulai = helperData.buka('static/var/'+'waktuMulai')
        stackGame = helperData.buka('static/var/'+'stackGame')
        lastPlayer = helperData.buka('static/var/'+'lastPlayer')
        #cari idGame
        idGame = ''
        for id in kB:
            if(uId in kB[id]):
                idGame = id
        if(idGame == ''):
            balas(event,'Gabung dulu bosq')
        else:
            banyakKartuDiTambah = len(pilihan[idGame][uId])
            pm(idGame,line_bot_api.get_profile(uId).display_name+' menambah '+str(banyakKartuDiTambah)+' kartu ke tumpukan')
            lastPlayer[idGame] = uId
            helperData.simpan(lastPlayer,'static/var/'+'lastPlayer')
            for pil in pilihan[idGame][uId]:
                #tambah ke tumpukan game
                stackGame[idGame].append(pil)
                #hapus dari tangan pemain
                idx = kB[idGame][uId].index(pil)
                del kB[idGame][uId][idx]
            helperData.simpan(stackGame,'static/var/'+'stackGame')
            pm(idGame,'Sekarang ada '+str(len(stackGame[idGame]))+' kartu di tumpukan')
            helperData.simpan(kB,'static/var/'+'kB')
            pilihan[idGame][uId] = []
            helperData.simpan(pilihan,'static/var/'+'pilihan')
            curCard = helperData.buka('static/var/'+'curCard')
            cekBohong = curCard[idGame]
            idx = (helperKartu.urutan.index(curCard[idGame])+1)%13
            curCard[idGame] = helperKartu.urutan[idx]
            helperData.simpan(curCard,'static/var/'+'curCard')
            #hapus imagemap dari local
            hapusSemuaImagemap(idGame)
            #buat tombol bohong
            buttons_template = ButtonsTemplate(
                title='Mencurigakan?', text='Tekan bohong jika kamu curiga dia berbohong', actions=[
                    PostbackAction(label='Bohong', data='Bohong '+str(banyakKartuDiTambah)+' '+idGame+' '+lastPlayer[idGame]+' '+cekBohong),
                ])
            template_message = [
                    TemplateSendMessage(alt_text='Mencurigakan?', template=buttons_template),
                    TextSendMessage(text = 'Kartu sekarang adalah : '+curCard[idGame]+' (hati,wajik,sekop,keriting)')
                ]
            line_bot_api.push_message(idGame, template_message)
            #turn naik 1
            turn[idGame] = (turn[idGame]+1)%len(kB[idGame]) #<- menaikkan 1 turn, akan kembali ke 0 jika sudah sampai pemain terakhir
            pm(idGame,'Sekarang adalah giliran : '+line_bot_api.get_profile(urutanMain[idGame][turn[idGame]]))
            helperData.simpan(turn,'static/var/'+'turn')
            tanya(idGame,urutanMain[idGame][turn[idGame]])
    elif(isi == '.berhenti'):
        #check apakah game sudah ada
        if(idGame == ''):
            balas(event,'Tidak bisa digunakan di 1:1 chat')
        else:
            waktuMulai = helperData.buka('static/var/'+'waktuMulai')
            if(idGame in waktuMulai):
                hapusDirAman('static/'+idGame+'-'+waktuMulai[idGame],uId)
                kB = helperData.buka('static/var/'+'kB')
                turn = helperData.buka('static/var/'+'turn')
                urutanMain = helperData.buka('static/var/'+'urutanMain')
                pilihan = helperData.buka('static/var/'+'pilihan')
                bohong = helperData.buka('static/var/'+'bohong')
                curCard = helperData.buka('static/var/'+'curCard')
                lastPlayer = helperData.buka('static/var/'+'lastPlayer')
                stackGame = helperData.buka('static/var/'+'stackGame')
                mulai = helperData.buka('static/var/'+'mulai')
                del mulai[idGame]
                del waktuMulai[idGame]
                del stackGame[idGame]
                del lastPlayer[idGame]
                del curCard[idGame]
                del kB[idGame]
                del turn[idGame]
                del urutanMain[idGame]
                del pilihan[idGame]
                del bohong[idGame]
                helperData.simpan(mulai,'static/var/'+'mulai')
                helperData.simpan(waktuMulai,'static/var/'+'waktuMulai')
                helperData.simpan(stackGame,'static/var/'+'stackGame')
                helperData.simpan(lastPlayer,'static/var/'+'lastPlayer')
                helperData.simpan(curCard,'static/var/'+'curCard')
                helperData.simpan(bohong,'static/var/'+'bohong')
                helperData.simpan(kB,'static/var/'+'kB')
                helperData.simpan(turn,'static/var/'+'turn')
                helperData.simpan(urutanMain,'static/var/'+'urutanMain')
                helperData.simpan(pilihan,'static/var/'+'pilihan')
                balas(event,'Game berhenti')
            else:
                balas(event,'Game belum dimulai bahkan. Mulai dengan .kartuBohong')
    #fungsi debug
    elif(isi == 'listGame'):
        game = ''
        kB = helperData.buka('static/var/'+'kB')
        for i in kB:
            game = game + i + '\n'
        balas(event,game)
    elif(isi == 'listPemain'):
        pemain = ''
        kB = helperData.buka('static/var/'+'kB')
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