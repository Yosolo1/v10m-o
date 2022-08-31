from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import shortener
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
from yarl import URL
import re
import random
from draft_to_calendar import send_calendar

listproxy = []

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def nameRamdom():
    populaton = 'abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    name = "".join(random.sample(populaton,10))
    return name

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚊𝚗𝚍𝚘 𝚙𝚊𝚛𝚊 𝚜𝚞𝚋𝚒𝚛☁...')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        if cloudtype == 'moodle':
            client = MoodleClient(user_info['moodle_user'],
                                  user_info['moodle_password'],
                                  user_info['moodle_host'],
                                  user_info['moodle_repo_id'],
                                  proxy=proxy)
            loged = client.login()
            itererr = 0
            if loged:
                if user_info['uploadtype'] == 'evidence':
                    evidences = client.getEvidences()
                    evidname = str(filename).split('.')[0]
                    for evid in evidences:
                        if evid['name'] == evidname:
                            evidence = evid
                            break
                    if evidence is None:
                        evidence = client.createEvidence(evidname)

                originalfile = ''
                if len(files)>1:
                    originalfile = filename
                draftlist = []
                for f in files:
                    f_size = get_file_size(f)
                    resp = None
                    iter = 0
                    tokenize = False
                    if user_info['tokenize']!=0:
                       tokenize = True
                    while resp is None:
                          if user_info['uploadtype'] == 'evidence':
                             fileid,resp = client.upload_file(f,evidence,fileid,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                          elif user_info['uploadtype'] == 'draft':
                             fileid,resp = client.upload_file_draft(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          elif user_info['uploadtype'] == 'perfil':
                             fileid,resp = client.upload_file_perfil(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          elif user_info['uploadtype'] == 'blog':
                             fileid,resp = client.upload_file_blog(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          elif user_info['uploadtype'] == 'calendar':
                             fileid,resp = client.upload_file_calendar(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          iter += 1
                          if iter>=10:
                              break
                    os.unlink(f)
                if user_info['uploadtype'] == 'evidence':
                    try:
                        client.saveEvidence(evidence)
                    except:pass
                return draftlist
            else:
                bot.editMessageText(message,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚎𝚗 𝚕𝚊 𝚗𝚞𝚋𝚎⚠️')
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            bot.editMessageText(message,'🚀Subiendo ☁ Espere por favor...😄')
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)                
               return filesdata
        return None
    except Exception as ex:
        bot.editMessageText(message,f'⚠️Error {str(ex)}⚠️')


def processFile(update,bot,message,file,thread=None,jdb=None):
    user_info = jdb.get_user(update.message.sender.username)
    name =''
    if user_info['rename'] == 1:
        ext = file.split('.')[-1]
        if '7z.' in file:
            ext1 = file.split('.')[-2]
            ext2 = file.split('.')[-1]
            name = nameRamdom() + '.'+ext1+'.'+ext2
        else:
            name = nameRamdom() + '.'+ext
    else:
        name = file
    os.rename(file,name)
    file_size = get_file_size(name)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(name,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(name).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(name)
        zip.close()
        mult_file.close()
        client = processUploadFiles(name,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(name)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(name,file_size,[name],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'📦𝙿𝚛𝚎𝚙𝚊𝚛𝚊𝚗𝚍𝚘 𝚊𝚛𝚌𝚑𝚒𝚟𝚘📄...')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(name).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' \
                    or getUser['uploadtype'] == 'perfil' \
                    or getUser['uploadtype'] == 'blog' \
                    or getUser['uploadtype'] == 'calendar'\
                    or getUser['uploadtype'] == 'calendarevea':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        if user_info['urlshort']==1:
            if len(files)>0:
                i = 0
                while i < len(files):
                    files[i]['directurl'] = SuperDbot.short_url(files[i]['directurl'])
                    i+=1
        bot.deleteMessage(message.chat.id,message.message_id)
        finishInfo = infos.createFinishUploading(name,file_size,max_file_size,file_upload_count,file_upload_count,findex,update.message.sender.username)
        filesInfo = infos.createFileMsg(name,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(name).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
    else:
        bot.editMessageText(message,'⚠️𝙴𝚛𝚛𝚘𝚛 𝚎𝚗 𝚕𝚊 𝚗𝚞𝚋𝚎⚠️')

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        tl_admin_user = os.environ.get('tl_admin_user')

        #set in debug
        tl_admin_user = 'Luis_Daniel_Diaz'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)
        #if username == tl_admin_user or user_info:
        if username in str(tl_admin_user).split(';') or user_info :  # validate user
            if user_info is None:
                #if username == tl_admin_user:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "🚷NO TIENES PERMITIDO USARME🚷.\nPor favor contacta con mi programador @Luis_Daniel_Diaz\n"
            intento_msg = "💢El usuario @"+username+ " ha intentando usar el bot sin permiso💢"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(958475767,intento_msg)
            return


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '✅El usuario @'+user+' ah sido agregado al bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /adduser username⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = '❇️Ahora @'+user+' es admin del bot también.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /adduser username⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/addproxy' in msgText:
            isadmin = jdb.is_admin(username)
            global listproxy
            if isadmin:
                try:
                    proxy = str(msgText).split(' ')[1]
                    listproxy.append(proxy)
                    zize = len(listproxy)-1
                    bot.sendMessage(update.message.chat.id,f'Proxy registrado en la posicion {zize}')
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /addproxy proxy⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/checkproxy' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    msg = 'Proxis Registrados\n'
                    cont = 0
                    for proxy in listproxy:
                        msg += str(cont) +'--'+proxy+'\n'
                        cont +=1
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /checkproxy⚠️')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/leerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/banuser' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'❌No Se Puede Banear Usted❌')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '🚫El usuario @'+user+' ah sido baneado del bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /banuser username❌')
            else:
                bot.sendMessage(update.message.chat.id,'⚠️No posee permisos de administrador⚠️')
            return
        if '/obtenerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                bot.sendMessage(update.message.chat.id,'Base de datos👇🏻:')
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return
        # end

        # comandos de usuario
        if '/xdlink' in msgText:

            try: 
                urls = str(msgText).split(' ')[1]
                channelid = getUser['channelid']
                xdlinkdd = xdlink.parse(urls, username)
                msg = f'🔗Aquí está su link encriptado en xdlink:🔗 `{xdlinkdd}`'
                msgP = f'🔗Aquí está su link encriptado en xdlink protegido:🔗 `{xdlinkdd}`'
                if channelid == 0:
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
                else: 
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msgP)
            except:
                msg = f'📌El comando debe ir acompañado de un link moodle...'
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return
        if '/shorturl' in msgText:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['urlshort']==0:
                            jdb.items[user]['urlshort'] = 1
                            continue
                        if jdb.items[user]['urlshort']==1:
                            jdb.items[user]['urlshort'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'✅ShortUrl Cambiado✅')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id, statInfo,reply_markup=reply_markup)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /banuser username❌')
                return
        if '/rename' in msgText:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['rename']==0:
                            jdb.items[user]['rename'] = 1
                            continue
                        if jdb.items[user]['rename']==1:
                            jdb.items[user]['rename'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'✅Rename Cambiado✅')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id, statInfo,reply_markup=reply_markup)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /banuser username❌')
                return
        if '/xd' in msgText:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['xdlink']==0:
                            jdb.items[user]['xdlink'] = 1
                            continue
                        if jdb.items[user]['xdlink']==1:
                            jdb.items[user]['xdlink'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'✅XDLinks Cambiado✅')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id, statInfo,reply_markup=reply_markup)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /banuser username❌')
                return
        if '/chanid' in msgText:
            channelId = str(msgText).split(' ')[1]
            getUser = user_info
            try:
                if getUser:
                    getUser['channelid'] = str(msgText).split(' ')[1]
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'╭───ⓘ☣️El comando debe ir acompañado de un id de canal...\n╰⊸\n💡Ejemplo: -100XXXXXXXXXX.')
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/delchan' in msgText:
            getUser = user_info
            if getUser:
                getUser['channelid'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
        if '/login' in msgText:
             bot.sendMessage(update.message.chat.id,'🔐')
             bot.sendMessage(update.message.chat.id,"🗝️Logueandose...")
             import requests
             getUser = user_info
             if getUser:
                user = getUser['moodle_user']
                passw = getUser['moodle_password']
                host = getUser['moodle_host']
                proxy = getUser['proxy']
                url = host
                r = requests.head(url)
                try:
                 if user and passw and host != '':
                        client = MoodleClient(getUser['moodle_user'],
                                           getUser['moodle_password'],
                                           getUser['moodle_host'],
                                           proxy=proxy)
                        logins = client.login()
                        if logins:
                                bot.editMessageText(message,"✅Conexion lista...✅")  
                                return
                        else: 
                            bot.editMessageText(message,"☣️Error al conectar con el host...")
                            message273 = bot.sendMessage(update.message.chat.id,🗝️Logueandose...")
                            if r.status_code == 200 or r.status_code == 303:
                                bot.editMessageText(message273,f"🧾Estado de la pagina: {r}\n☣️Revise que su cuenta no ah sido baneada...")
                                return
                            else: bot.editMessageText(message273,f"🚷Pagina caida, estado: {r}")    
                            return
                except Exception as ex:
                            bot.editMessageText(message273,"☣️Tipo de error: "+str(ex))    
                else: bot.editMessageText(message,"☣️No ha puesto sus credenciales.")    
                return
        if '/commands' in msgText:
            message = bot.sendMessage(update.message.chat.id,'🙂Para añadir estos comandos al menú de acceso rápido debe enviarle el comando /setcommands a @BotFather y luego seleccionar su bot, luego solo queda reenviarle el mensaje con los siguientes comandos y bualah😁.')
            comandos = open('comandos.txt','r')
            bot.sendMessage(update.message.chat.id,comandos.read())
            información.close()
            return
        if '/help' in msgText:
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return
        if '/setproxy' in msgText:
            getUser = user_info
            if getUser:
                try:
                   pos = int(str(msgText).split(' ')[1])
                   proxy = str(listproxy[pos])
                   getUser['proxy'] = proxy
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'Su Proxy esta Listo'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /setproxy proxy⚠️')
                return
        if '/info' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '🗜️Perfecto ahora los zips serán de '+ sizeof_fmt(size*1024*1024)+' las partes📚'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /zips tamaño de zips⚠️')
                return
        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /acc usuario,contraseña⚠️')
            return
        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /host url de la moodle⚠️')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /repo ID de la moodle⚠️')
            return
     
      #  if '/tokenize_on' in msgText:
      #      try:
       #         getUser = user_info
        #        if getUser:
       #             getUser['tokenize'] = 1
        #            jdb.save_data_user(username,getUser)
        #            jdb.save()
        #            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
       #             bot.sendMessage(update.message.chat.id,statInfo)
       #     except:
       #         bot.sendMessage(update.message.chat.id,'❌Error en el comando /tokenize state❌')
        #    return
     #   if '/tokenize_off' in msgText:
      #      try:
       #         getUser = user_info
       #         if getUser:
       #             getUser['tokenize'] = 0
       #             jdb.save_data_user(username,getUser)
       #             jdb.save()
        #            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
         #           bot.sendMessage(update.message.chat.id,statInfo)
        #    except:
        #        bot.sendMessage(update.message.chat.id,'❌Error en el comando /tokenize state❌')
         #   return
     

        if '/cloud' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['cloudtype'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /cloud (moodle o cloud⚠️')
            return
        if '/uptype' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /uptype (typo de subida (evidence,draft,calendar,calendarevea,blog)⚠️')
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            return
        if '/crypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'Proxy encryptado:\n{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'Proxy decryptado:\n{proxy_de}')
            return
        if '/dir' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['dir'] = repoid + '/'
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo,reply_markup=reply_markup)
            except:
                bot.sendMessage(update.message.chat.id,'⚠️Error en el comando /dir carpeta destino⚠️')
            return
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'🚫TAREA CANCELADA🚫')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'⏳𝙰𝙽𝙰𝙻𝙸𝚉𝙰𝙽𝙳𝙾...⌛')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = '╭───ⓘ🌟𝔹𝕆𝕋 𝕀ℕ𝕀ℂ𝕀𝔸𝔻𝕆🌟─〄\n│\n'
            start_msg+= '├⊸🤖Hola @' + str(username)+' !!!!\n│\n'
            start_msg+= '├──⊰᯽⊱┈──╌❊ - ❊╌──┈⊰᯽⊱──⊸\n│\n'
            start_msg+= '├⊸☺️! Bienvenid@ al bot de descargas gratis SuperDownload en su versión 1.5🌟!\n'
            start_msg+= '├⊸🙂Si necesita ayuda o información utilice:\n│\n'
            start_msg+= '├⊸/help\n'
            start_msg+= '├⊸/about\n'
            start_msg+= '├⊸/config\n│\n'
            start_msg+= '├⊸🙂Si usted desea añadir la barra de comandos al menú de acceso rápido de su bot envíe /commands.\n│\n'
            start_msg+= '├⊸😁𝚀𝚞𝚎 𝚍𝚒𝚜𝚏𝚛𝚞𝚝𝚎 𝚐𝚛𝚊𝚗𝚍𝚎𝚖𝚎𝚗𝚝𝚎 𝚜𝚞 𝚎𝚜𝚝𝚊𝚍í𝚊😁.\n│\n'
            start_msg+= '╰───ⓘSuperDownload v1.5🌟─〄\n'
            bot.editMessageText(message,start_msg)
        elif '/config' in msgText:
            msg_nub = "╭───ⓘ💡LISTA DE NUBES PRECONFIGURADAS:\n"
            msg_nub += "├⊸☁️ UCLV ☛ /uclv\n"
            msg_nub += "├⊸☁️ Aulacened ☛ /aulacened\n"
            msg_nub += "├⊸☁️ Cursos ☛ /cursos\n"
            msg_nub += "├⊸☁️ Evea ☛ /evea\n"
            msg_nub += "├⊸☁️ Eduvirtual ☛ /eduvirtual\n"
            msg_nub += "├⊸☁️ Eva ☛ /eva\n"
            msg_nub += "╰⊸☁️ Art.sld ☛ /artem\n"   
            bot.editMessageText(message,msg_nub)
        elif '/aulacened' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulacened.uci.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 248
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aulacened cargada...")
           
        elif '/uclv' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://moodle.uclv.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 399
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de UCLV cargada...")

        elif '/uvs' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://uvs.ucm.cmw.sld.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 120
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Uvs cargada...")

        elif '/evea' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://evea.uh.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 248
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Evea cargada...")
        
        elif '/cursos' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://cursos.uo.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Cursos cargada...")
        
        elif '/eva' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eva.uo.edu.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---."
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Eva cargada...")
        
        elif "/artem" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "http://www.aulavirtual.art.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 90
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aula Artemisa cargada...")
            
        elif '/eduvirtual' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eduvirtual.uho.edu.cu/"
            getUser['uploadtype'] =  "blog"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 3
            getUser['zips'] = 8
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Eduvirtual cargada...")
        
        elif "/gtm" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulauvs.gtm.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 7
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"✅Configuración de Aula Guantanamo cargada...")
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'Obteniendo Token...')
            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'Su Token es: '+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'La Moodle '+client.path+' No tiene Token')
            except Exception as ex:
                bot.editMessageText(message2,'La Moodle '+client.path+' No tiene Token o revise la Cuenta')
        if '/watch' in msgText:
            import requests
            url = user_info['moodle_host']
            msg2134 = bot.editMessageText(message,f"🔎Escaneando url guardado en info...")
            try:
             r = requests.head(url)
             if r.status_code == 200 or r.status_code == 303:
                bot.editMessageText(msg2134,f"✅Pagina: {url} activa.")
             else: bot.editMessageText(msg2134,f"🚫Pagina: {url} caida.")
            except Exception as ex:
                bot.editMessageText(message,"⁉️Error al escanear"+str(ex))
        elif '/files' == msgText and user_info['cloudtype']=='moodle':
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 files = client.getEvidences()
                 filesInfo = infos.createFilesMsg(files)
                 bot.editMessageText(message,filesInfo)
                 client.logout()
             else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
        elif '/txt_' in msgText and user_info['cloudtype']=='moodle':
             findex = str(msgText).split('_')[1]
             findex = int(findex)
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 evidences = client.getEvidences()
                 evindex = evidences[findex]
                 txtname = evindex['name']+'.txt'
                 sendTxt(txtname,evindex['files'],update,bot)
                 client.logout()
                 bot.editMessageText(message,'𝚃𝚇𝚃 𝙰𝚚𝚞𝚒👇')
             else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
             pass
        elif '/delete' in msgText:
           try: 
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            bot.editMessageText(message,'🔐')
            message = bot.sendMessage(update.message.chat.id,'🪛Logueandose para intentar eliminar el archivo...')
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "✅Archivo eliminado con exito...🗑️")
            else: bot.sendMessage(update.message.chat.i, "🚷No se pudo loguear...")            
           except: bot.sendMessage(update.message.chat.id, "☣️No se pudo eliminar el archivo...")
        elif '/del_' in msgText and user_info['cloudtype']=='moodle':
            findex = int(str(msgText).split('_')[1])
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfile = client.getEvidences()[findex]
                client.deleteEvidence(evfile)
                client.logout()
                bot.editMessageText(message,'𝙰𝚛𝚌𝚑𝚒𝚟𝚘 𝚎𝚕𝚒𝚖𝚒𝚗𝚊𝚍𝚘🗑️')
            else:
                bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
        elif '/delall' in msgText and user_info['cloudtype']=='moodle':
            contador = 0
            eliminados = 0
            bot.editMessageText(message,'Eliminando los 50 primero elementos...')
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                user_info['moodle_password'],
                                user_info['moodle_host'],
                                user_info['moodle_repo_id'],
                                proxy=proxy)
            loged = client.login()
            prueba = client.getEvidences()
            if len(prueba) == 0:
                bot.sendMessage(update.message.chat.id,'La Moodle está vacia🗑️')
                return 
            try:
                for contador in range(50):
                    proxy = ProxyCloud.parse(user_info['proxy'])
                    client = MoodleClient(user_info['moodle_user'],
                                    user_info['moodle_password'],
                                    user_info['moodle_host'],
                                    user_info['moodle_repo_id'],
                                    proxy=proxy)
                    loged = client.login()
                    if loged:               
                            evfile = client.getEvidences()[0]
                            client.deleteEvidence(evfile)
                            eliminados += 1
                            bot.sendMessage(update.message.chat.id,'Archivo ' +str(eliminados)+' eliminado🗑️')                            
                    else:
                        bot.editMessageText(message,'🧐')
                message = bot.sendMessage(update.message.chat.id,'⊷⚠️Error y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
                bot.sendMessage(update.message.chat.id,'Se eliminaron Completamente los  50 Elementos')
            except:
                bot.sendMessage(update.message.chat.id,'No se pudieron eliminar 50 elementos solo se eliminaron '+str(eliminados))
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 7386053
            #    api_hash = '78d1c032f3aa546ff5176d9ff0e7f341'
            #    bot_token = '5124841893:AAH30p6ljtIzi2oPlaZwBmCfWQ1KelC6KUg'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'⊷⚠️𝙴𝚛𝚛𝚘𝚛, 𝚗𝚘 𝚜𝚎 𝚙𝚞𝚍𝚘 𝚊𝚗𝚊𝚕𝚒𝚣𝚊𝚛 𝚌𝚘𝚛𝚛𝚎𝚌𝚝𝚊𝚖𝚎𝚗𝚝𝚎⚠️⊶')
    except Exception as ex:
           print(str(ex))
           bot.sendMessage(update.message.chat.id,str(ex))

def main():
    bot_token = os.environ.get('bot_token')
    #set in debug
    bot_token = '5391544545:AAHhauKxmTOW_nlCi0O6s9fxe9o_9g0tGRs'

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
