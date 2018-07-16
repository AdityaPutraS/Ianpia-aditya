#Import
import os
from PIL import Image, ImageDraw
from random import shuffle
import math

#Global Variable
tipe = ['Hati','Keriting','Sekop','Wajik']
urutan = ['2','3','4','5','6','7','8','9','10','Jack','Queen','King','As']

#Function
def bagiKartu(jumlahPemain):
    '''
    Cara pakai :
        bagiKartu(3) -> akan membagi 52 kartu(joker tidak dihitung) ke 3 pemain secara adil
        fungsi akan mereturn list of list seperti berikut
        [ ['2 Hati','3 Sekop',...],['5 Wajik','King Hati',... ],... ]
        cara melihat kartu dari pemain ke 3 adalah
            kartuPemain = bagiKartu(3)
            print(kartuPemain[2])  <--- 2 karena list dimulai dari 0
    '''
    #membuat list semua kartu
    listKartu = []
    for nomor in urutan:
        for tip in tipe:
            listKartu.append(nomor+' '+tip)
    shuffle(listKartu)
    kartuPemain = []
    #menentukan tiap pemain dapat berapa kartu, jumlah kartu = 52
    sisaKartu = 52 % jumlahPemain
    kartuPerPemain = int(52 / jumlahPemain)
    no = 0
    for i in range(0,jumlahPemain):
        tmpKartu = []
        for j in range(0,kartuPerPemain):
            tmpKartu.append(listKartu[no])
            no += 1
        kartuPemain.append(tmpKartu)
    #memberi sisanya kepada pemain secara acak
    pemain = [x for x in range(0,jumlahPemain)]
    shuffle(pemain)
    for i in range(0,sisaKartu):
        kartuPemain[pemain[i]].append(listKartu[no])
        no += 1
    return kartuPemain
def loadGambar(w,h):
    '''
    Cara pakai:
        kartu = loadGambar(100,150)
        maka variable kartu akan berisi gambar dari setiap kartu
    Cara mengambil gambar kartu tertentu :
        kartu['As']['Hati'] akan mengembalikan gambar kartu As Hati
    '''
    kartu = {}
    for nomor in urutan:
        tmp = {}
        for tip in tipe:
            dirKartu = 'static/kartu/'+nomor+' '+tip+'.png'
            tmp[tip] = Image.open(dirKartu)
            tmp[tip] = tmp[tip].resize((w,h),Image.ANTIALIAS)
            #tmp[tip] = tmp[tip].resize((int(tmp[tip].size[0]/2),int(tmp[tip].size[1]/2)),Image.ANTIALIAS)
        kartu[nomor] = tmp
    return kartu
def gambarKartuDiTangan(sizeR,kartuTangan):
    '''
    Cara pakai:
        gambar = gambarKartuDiTangan(720,['2 Hati','3 Sekop',...])
    '''
    banyak = len(kartuTangan)
    gambarKartu = loadGambar(100,150)
    offKarX,offKarY = 110,160
    size = 1040
    kartuPerBaris = 9
    if(banyak <= kartuPerBaris):
        offsetX = int((size-(100+(banyak-1)*offKarX))/2)
    else:
        offsetX = int((size-(100+(kartuPerBaris-1)*offKarX))/2)
    ic(offsetX)
    offsetY = int((size-(150+math.ceil(banyak/(kartuPerBaris)-1)*offKarY))/2)
    ic(offsetY)
    background = Image.new('RGB', (size,size), (0,0,0))
    no = 0
    for i in range(0,banyak):
        nomor, tipe = kartuTangan[no].split()
        no += 1
        background.paste(gambarKartu[nomor][tipe],(offsetX,offsetY))
        offsetX += offKarX
        if(no % kartuPerBaris == 0):
            if((banyak-no) <= kartuPerBaris):
                offsetX = int((size-(100+((banyak-no)-1)*offKarX))/2)
            else:
                offsetX = int((size-(100+(kartuPerBaris-1)*offKarX))/2)
            offsetY += offKarY
    return background.resize((sizeR,sizeR),Image.ANTIALIAS)
