
# t.me/DSPGorelikBot

# dspbot

import cv2
import numpy as np
import os
from PIL import Image
import subprocess
import sqlite3
import tempfile
import telebot
from telebot import apihelper

import requests




# access_token = '***'
# apihelper.proxy = {'https': 'https://85.132.71.82:3128'}

# PROXY = 'socks5://80.211.17.211:1080'
# PROXY = 'socks5://88.198.24.108:1080'
#
# apihelper.proxy = {'http': PROXY, 'https': PROXY}

from config import TELEGRAM_API_TOKEN

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

def convertToRGB(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


#3. Определяет есть ли лицо на отправляемых фотографиях или нет, сохраняет только те,
#где оно есть
@bot.message_handler(content_types=['photo'])
def photo(message):
    print ('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print ('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print ('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    image = cv2.imread('image.jpg')
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    link = r'opencv\data\haarcascade\haarcascade_frontalface_default.xml'
    link = r'G:\dsp2\opencv\data\haarcascades\haarcascade_frontalface_default.xml'

    haar_cascade_face = cv2.CascadeClassifier(link)

    faces_rects = haar_cascade_face.detectMultiScale(image_gray, scaleFactor=1.2, minNeighbors=5);

    # Let us print the no. of faces found
    print('Faces found: ', len(faces_rects))

    if len(faces_rects)>0:
        for (x, y, w, h) in faces_rects:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite('img_rec.jpg', image)
        bot.send_photo(message.chat.id, photo = open('img_rec.jpg', 'rb'))
    else:
        bot.send_message(message.chat.id, 'не нашел фронтальных лиц на фото')



@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id, 'Привет, ты vfvbcfk мне /start')



@bot.message_handler(commands=['users'])
def start_message(message):
    bot.send_message(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id, 'Users list')
    con = sqlite3.connect('voices.db')
    cursor = con.cursor()
    users = cursor.execute("SELECT DISTINCT user_id, username FROM voices ").fetchall()
    #
    # voices_by_users = cursor.execute("SELECT * FROM voices GROUP BY user_id").fetchall()
    # print(voices_by_users)
    #

    for user in users:
        print (user)
        user_voices = cursor.execute("SELECT voice FROM voices WHERE user_id = ?", (user[0],)).fetchall()

        print (user_voices)
        # bot.send_message(message.chat.user[0], message.from_user.last_name)
        # username = bot.get_user_profile_photos(user[0])
        # print (username)

    con.commit()
    con.close()
        # bot.send_message(message.chat.id, user[0])

# @bot.message_handler(content_types=['text'])
# def send_text(message):

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
#GET USERS
    elif message.text.startswith('get users'):
        con = sqlite3.connect('voices.db')
        cursor = con.cursor()
        users = cursor.execute("SELECT user_id, username FROM voices GROUP BY user_id").fetchall()
        print (users)
            # bot.send_message(message.chat.user[0], message.from_user.last_name)
            # username = bot.get_user_profile_photos(user[0])
            # print (username)
        users_out = 'user_id:user_name \n\n'
        for user in users:
            users_out += user[0] + ':' + user[1] + '\n'

        bot.send_message(message.chat.id, users_out)

        con.commit()
        con.close()

#GET VOICE IDS
    elif message.text.startswith('get voice_ids'):
        uid = message.text.split(' ')[-1]
        con = sqlite3.connect('voices.db')
        cursor = con.cursor()
        voice_ids = cursor.execute("SELECT voice FROM voices WHERE user_id=?",(uid,)).fetchall()
        print (voice_ids)
            # bot.send_message(message.chat.user[0], message.from_user.last_name)
            # username = bot.get_user_profile_photos(user[0])
            # print (username)

        bot.send_message(message.chat.id, voice_ids)

        con.commit()
        con.close()
#GET WAV
    elif message.text.startswith('get wav'):

        uid = message.text.split(' ')[-1]
        user_dir = ('converted/'+uid)
        print (user_dir)
        dir = (os.listdir(user_dir))
        print (dir)
        for file in dir:
            print (file)
            wav = user_dir + '/' + file
            print(wav)
            bot.send_document(message.chat.id, open(wav,'rb'))

    #     downloaded_file = bot.download_file(file_info.file_path)
    #     src = file_info.file_path
    #     with open (src, 'wb') as new_file:
    #         new_file.write(downloaded_file)
    #     bot.reply_to(message, 'Сохранил голосовое')
    #     voice = downloaded_file
    #     bot.send_document(message.chat.id,voice)

    elif message.text == 'Пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')

    elif message.text.startswith('uid '):
        uid = message.text.split(' ')[1]
        con = sqlite3.connect('voices.db')
        cursor = con.cursor()
        user_voices = cursor.execute("SELECT * FROM voices WHERE user_id = ?", (uid,)).fetchall()

        print(user_voices)
        for voice in user_voices:
            file_info = bot.get_file(voice[2])
            print (file_info)



            # bot.send_message(message.chat.user[0], message.from_user.last_name)
            # username = bot.get_user_profile_photos(user[0])
            # print (username)

        con.commit()
        con.close()


    elif message.text.startswith('fid '):
        fid = message.text.split(' ')[1]
        bot.send_message(message.chat.id,  fid)
        file_info = bot.get_file(fid)

        print(os.getcwd())

        downloaded_file = bot.download_file(file_info.file_path)
        file = file_info.file_path
        print (file)
        with open (file, 'wb') as new_file:
            new_file.write(downloaded_file)
            src = (new_file.name)
            new_file.close()

        subprocess.call(['bin/ffmpeg.exe', '-i', file, '-ar', '16000', file[:-4] + 'converted.wav'])

        #
        # # print (type(new_file))
        # print (src)
        #
        # # infile = open(src, 'rb')
        #
        # command = [
        #     r'bin/ffmpeg.exe',  # путь до ffmpeg.exe
        #     '-i', src,
        #     '-f', 's16le',
        #     '-acodec', 'pcm_s16le',
        #     '-ar', '16000',
        #     '-'
        # ]
        # outfile = open('outfile.pcm', 'w+')
        # proc = subprocess.Popen(command, stdout=outfile, stderr=subprocess.DEVNULL)
        # proc.wait()
        # outfile.close()
        # infile.close()


        # bot.send_message(message.chat.id,  str(file_info.file_size) + ' ' + file_info.file_path)
        #
        #
        # ##########
        # file_web_path = 'https://api.telegram.org/file/bot{0}/{1}'.\
        #     format(TELEGRAM_API_TOKEN, file_info.file_path)
        # print (file_web_path)
        # file = requests.get(file_web_path)
        # print (type(file))
        # #
        # # raw = message.photo[2].file_id
        # path = 'temp_file'
        # # file_info = bot.get_file(raw)
        # downloaded_file = bot.download_file(file_info.file_path)
        # print (type(downloaded_file))
        # # with open(path, 'wb') as new_file:
        #     new_file.write(downloaded_file)

        #         with open(filename, 'br') as file:
        #             bytes = file.read()
        # in_file = path.read()

#         bytes = convert_to_pcm16b16000r(in_bytes=bytes)



@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    # bot.send_message(message.chat.id, 'получил голосовое')
    file_info = bot.get_file(message.voice.file_id)
    #     file = requests.get('https://api.telegram.org/file/bot{0}/{1}'
    #                         .format(TELEGRAM_API_TOKEN, file_info.file_path))

    voice_id = message.voice.file_id
    user_id = str(message.from_user.id)
    username = message.from_user.username
    bot.send_message(message.chat.id, 'сохранено в базе данных, voice_id = ' + voice_id + ' user_id = ' + user_id, ' username =  ' + username)

    # bot.send_message(message.chat.id, user_id)


    con = sqlite3.connect('voices.db')
    cursor = con.cursor()
    cursor.execute("INSERT INTO voices VALUES(?, ?,?)", (user_id, username, voice_id))
    con.commit()
    con.close()


    downloaded_file = bot.download_file(file_info.file_path)
    file = file_info.file_path
    filename = file.split('/')[-1]
    print (filename)
    with open(file, 'wb') as new_file:
        new_file.write(downloaded_file)
        src = (new_file.name)
        new_file.close()
    os.makedirs('converted/'+str(user_id), exist_ok = True)
    path4converted = 'converted/' + str(user_id) + '/' + filename[:-4] + 'conv.wav'
    print (path4converted)
    subprocess.call(['bin/ffmpeg.exe', '-i', file, '-ar', '16000',path4converted])


#     downloaded_file = bot.download_file(file_info.file_path)
#     src = file_info.file_path
#     with open (src, 'wb') as new_file:
#         new_file.write(downloaded_file)
#     bot.reply_to(message, 'Сохранил голосовое')
#     voice = downloaded_file
#     bot.send_document(message.chat.id,voice)

#     conn = sqlite3.connect("voices.db") # или :memory: чтобы сохранить в RAM
#     cursor = conn.cursor()

#     cursor.execute("INSERT INTO voices VALUES(?, ?)"(extension, message.document.file_id))
#     con.commit()

#     conn.close()



bot.polling(timeout=200)


