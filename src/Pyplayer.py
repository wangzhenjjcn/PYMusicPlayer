#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author WangZhen <wangzhenjjcn@gmail.com> MIT Licenses
# Keep These Words After You Modified these files

import datetime
import json
import os
import re
import sys
import threading
import time
import math

import pygame
import requests
import librosa

try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    import cookielib
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    print(f"python2.")
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    import tkinter.simpledialog as tkSimpleDialog    #askstring()
    import tkinter
    import http.cookiejar as cookielib
    print(f"python3.")

download_path = "./downloads/"
tmp_path = "./tmp/"
play_path="./downloads/"
if not os.path.exists(download_path):
    os.mkdir(download_path)
if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)
webSession = requests.session()
webSession.cookies = cookielib.LWPCookieJar(filename=tmp_path+"cookie.txt")
defaultHeader = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache"}
ajaxheaders = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept-encoding': "gzip, deflate",
    'x-requested-with': "XMLHttpRequest",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache",
    'accept': "application/json, text/javascript, */*; q=0.01",}

current_index=-1
# p="netease"
p="tencent"
stype="song"
code="579621905"
local=True
searching=False
playing=False
downloading=False
backsyc=False
playnext=False
downloadingThreads=16
nowThreads=0
word=""
datas=[]
filenames=[]
downloadList=[]
lastword=""
lasttype=""
# authors=[]
# links=[]
# lrcs=[]
# pics=[]
# songids=[]
# titles=[]
# types=[]
# urls=[]
#global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc

class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('王振的音乐下载软件<WangZhen@20190409v1.0>')
        self.master.geometry('837x494')
        self.master.resizable(0,0)
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.Slider1 = Scale(self.top, orient='horizontal', from_=0, to=600)
        self.Slider1.place(relx=0.564, rely=0.081, relwidth=0.317, relheight=0.067)

        self.ProgressBar1Var = StringVar(value='100')
        self.ProgressBar1 = Progressbar(self.top, orient='horizontal', maximum=100, variable=self.ProgressBar1Var)
        self.ProgressBar1.place(relx=0.153, rely=0.955, relwidth=0.833, relheight=0.034)

        self.ProviderList = ['音乐搜索','歌手搜索','专辑搜索','视频搜索','电台搜索','用户搜索','歌词搜索','歌单搜索']
        self.Provider = Combobox(self.top, values=self.ProviderList, font=('宋体',9))
        self.Provider.place(relx=0.707, rely=0., relwidth=0.183, relheight=0.04)
        self.Provider.set(self.ProviderList[0])

        self.style.configure('NextSong.TButton',font=('宋体',9))
        self.NextSong = Button(self.top, text='下一首', command=self.NextSong_Cmd, style='NextSong.TButton')
        self.NextSong.place(relx=0.459, rely=0.081, relwidth=0.106, relheight=0.067)

        self.style.configure('PreSong.TButton',font=('宋体',9))
        self.PreSong = Button(self.top, text='上一首', command=self.PreSong_Cmd, style='PreSong.TButton')
        self.PreSong.place(relx=0.344, rely=0.081, relwidth=0.106, relheight=0.067)

        self.style.configure('Stop.TButton',font=('宋体',9))
        self.Stop = Button(self.top, text='停止', command=self.Stop_Cmd, style='Stop.TButton')
        self.Stop.place(relx=0.229, rely=0.081, relwidth=0.106, relheight=0.067)

        self.style.configure('Play.TButton',font=('宋体',9))
        self.Play = Button(self.top, text='播放', command=self.Play_Cmd, style='Play.TButton')
        self.Play.place(relx=0.115, rely=0.081, relwidth=0.106, relheight=0.067)

        self.style.configure('OpenPath.TButton',font=('宋体',9))
        self.OpenPath = Button(self.top, text='打开', command=self.OpenPath_Cmd, style='OpenPath.TButton')
        self.OpenPath.place(relx=0., rely=0.081, relwidth=0.106, relheight=0.067)

        self.Text1Var = StringVar(value='')
        self.Text1 = Entry(self.top, textvariable=self.Text1Var, font=('宋体',9))
        self.Text1.place(relx=0., rely=0., relwidth=0.689, relheight=0.051)
        self.Text1.bind('<Return>',self.Search_Cmd)

        self.style.configure('Search.TButton',font=('宋体',9))
        self.Search = Button(self.top, text='搜索', command=self.Search_Cmd, style='Search.TButton')
        self.Search.place(relx=0.908, rely=0., relwidth=0.102, relheight=0.054)

        self.ResaultBoxVar = StringVar(value='点击打开选择音乐目录播放音乐，或者在最上面输入关键字点击搜索检索音乐下载')
        self.ResaultBoxFont = Font(font=('YaHei Consolas Hybrid',12))
        self.ResaultBox = Listbox(self.top, listvariable=self.ResaultBoxVar, font=self.ResaultBoxFont)
        self.ResaultBox.place(relx=0., rely=0.162, relwidth=1.005, relheight=0.785)
        self.ResaultBox.bind('<Double-Button-1>',self.ResaultBoxDoubleClick)

        self.style.configure('Line1.TSeparator',background='#000000')
        self.Line1 = Separator(self.top, orient='horizontal', style='Line1.TSeparator')
        self.Line1.place(relx=0., rely=0.065, relwidth=1.004, relheight=0.002)

        self.style.configure('CopyRight.TLabel',anchor='w', font=('宋体',9))
        self.CopyRight = Label(self.top, text='DesignedByWangZhen', style='CopyRight.TLabel')
        self.CopyRight.place(relx=0., rely=0.972, relwidth=0.135, relheight=0.034)

        self.style.configure('Download.TButton',font=('宋体',9))
        self.Download = Button(self.top, text='下载所有', command=self.Download_Cmd, style='Download.TButton')
        self.Download.place(relx=0.889, rely=0.081, relwidth=0.106, relheight=0.067)

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。              
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc

       

    def checkType(self,event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word
        print("checkType")
        word=str(self.Text1.get()).encode("utf-8").decode("utf-8")
        if self.Provider.get()=="音乐搜索": 
            stype="song" 
            return
        if self.Provider.get()=="歌手搜索": 
            stype="singer"            
            return
        if self.Provider.get()=="专辑搜索": 
            stype="album"            
            return
        if self.Provider.get()=="歌单搜索": 
            stype="list"            
            return
        if self.Provider.get()=="视频搜索": 
            stype="video"            
            return
        if self.Provider.get()=="电台搜索": 
            stype="radio"            
            return
        if self.Provider.get()=="用户搜索": 
            stype="user"
            return
        if self.Provider.get()=="歌词搜索": 
            stype="lrc"
            return
        return

    def clearSettings(self,event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word
        self.ResaultBox.delete(0,END)
        datas=[]
        filenames=[]
        current_index=-1
        if playing :
            self.Play['text']='暂停'
        else:  
            self.Play['text']='播放'

    def backSync(self,event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        while backsyc:
           print("word:"+str(word)+"stype:"+str(stype)+"current_index:"+str(current_index)+"datas"+":"+str(len(datas)))
           time.sleep(15)


    def Searcher(self,event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        self.checkType()
        self.clearSettings()
        if "qq.com" in word:
            p="tencent"
        if "163.com" in word:
            p="netease"
        
        print("searching")
        print(word)
        print(stype)
        searching=True
        local=False
        while searching:
            if 'playlist' in word:
                print("searching songs")
                lid=word.split("playlist")[1]
                aid=[]
                for s in lid:
                    if s in "1234567890":
                        aid.append(s)
                    pass
                lid=''.join(aid)
                data=searchMusicListByIdAndCodeAndLimit(p,lid,code)
                datas.extend(data)
                print(lid)

            elif 'http' not in word:
                print("searching:"+str(word))
                datas=[]
                if stype=="video" or stype=="radio" or stype=="singer" :
                    p="netease"
                else:
                    p="tencent"
                if stype == "song" or stype == "list"  or stype == "video" or stype == "radio" or stype == "user":
                    if p=="tencent":
                        data=searchMusicByKeyAndTypeAndLimitAndOffset(word,stype,50,0)
                        n=0
                        while len(data)>0:
                            datas.extend(data)
                            n=n+1
                            data=searchMusicByKeyAndTypeAndLimitAndOffset(word,stype,50,n)
                    if p=="netease":
                        data=searchMusicByKeyAndTypeAndLimitAndOffset(word,stype,50,len(datas))
                        while len(data)>0:
                            datas.extend(data)
                            data=searchMusicByKeyAndTypeAndLimitAndOffset(word,stype,50,len(datas))
                if stype == "singer" or stype == "album" or stype == "lrc":
                    data=searchMusicByKeyAndTypeAndLimitAndOffset(word,stype,100,len(datas))
                    datas.extend(data )       
                print("word:"+str(word)+"  all:"+str(len(datas)))
            searching=False
            self.Search['text']='搜索结束'
            self.Set_ResaultBox()
            if stype=="video" and p=="netease":
                for i in range(0,len(datas)):
                    if  is_nan(datas[i]['vid']):
                        self.ResaultBox.itemconfig(i,bg="#990000")
                     
    

    def Player(self,event=None):
        global playnext,datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        playing = True
        self.Play['text']='暂停' 
        pygame.mixer.init()
        songtime=0
        filename=""
        while playing:    
            if   pygame.mixer.music.get_busy()==False : 
                if current_index==-1:
                    playing=False
                    continue
                if local:
                    filename=play_path+datas[current_index] 
                else:         
                    downloadSong(datas[current_index])
                    filename=tmp_path+getSongFilename(p,datas[current_index]) 
                    songtime=int(datas[current_index]['time'])
                for i in range(0,self.ResaultBox.size()):
                    self.ResaultBox.itemconfig(i,bg="#999999")  
                    self.ResaultBox.itemconfig(i,fg="#000000") 
                self.ResaultBox.itemconfig(current_index,fg="#FFFFFF")
                self.ResaultBox.itemconfig(current_index,bg="#6600FF")
                try:
                    print(filename)
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play(loops=0, start=0.0)
                    pygame.mixer.music.set_volume(1) 
                except Exception as e:
                    print(e)
                if playnext:
                    if len(datas)-1 == current_index:
                            current_index = 0
                    else:
                        current_index = current_index + 1
                else:
                    current_index = -1
                # downloadSong(datas[current_index])                
            else:
                time.sleep(0.1)
                if songtime<=0 or songtime ==None :
                    continue
                if(int(600*(pygame.mixer.music.get_pos()/(songtime*1000)))%5==0):
                    self.Slider1.set(int(600*(pygame.mixer.music.get_pos()/(songtime*1000))))
        return 


    def Downloader(self,event=None):
        global playnext,downloading,downloadList,datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        while downloading:    
            if len(downloadList)>0:
                downloading=True
            else :
                downloading=False
                continue
            song=downloadList.pop(0)        
            if downloading:
                    downloadMusicById(download_path+ re.sub(r'[\/:*?"<>|]','-',getSongFilename(None,song)),song['id'])
                    downloadMusicFile(download_path+re.sub(r'[\/:*?"<>|]','-',getLrcFilename(None,song)),song['lrc'])
                    downloadMusicFile(download_path+re.sub(r'[\/:*?"<>|]','-',getPicFilename(None,song)),song['pic'])
            self.Download['text']="下载中("+str(len(downloadList)+1)+")"
        downloading=False
        self.Download['text']="下载完成"

    def NextSong_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        #TODO, Please finish the function here!
        print("NextSong_Cmd")
        # global playing
        # playing = False
        # # pygame.mixer.quit()
        # global num
        # if len(res) == num:
        #     num = 0
        # try:
        #     # 停止播放，如果已停止，
        #     # 再次停止时会抛出异常，所以放在异常处理结构中
        #     pygame.mixer.music.stop()
        #     # pygame.mixer.quit()
        # except:
        #     pass
        # if not playing:
        #     # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        #     playing = True
        #     self.Play['text']='暂停'
        #     t = threading.Thread(target=self.Player)
        #     t.start()
        return 

    def PreSong_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        #TODO, Please finish the function here!
        # print("PreSong_Cmd")
        # global playing
        # playing = False
        # global num
        # if num == 0:
        #     num = len(res)-2
        # elif  num == len(res) -1:
        #     num -=2
        # else:
        #     num -=2
        # print("Pre"+str(num))
        # try:
        #     # 停止播放，如果已停止，
        #     # 再次停止时会抛出异常，所以放在异常处理结构中
        #     pygame.mixer.music.stop()
        #     # pygame.mixer.quit()
        # except:
        #     pass
        # if not playing:
        #     # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        #     playing = True
        #     self.Play['text']='暂停'
        #     t = threading.Thread(target=self.Player)
        #     t.start()
        return 

    def Stop_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        #TODO, Please finish the function here!
        print("Stop_Cmd")
        # global playing
        # playing = False
        # self.Play['text']='播放'
        # try:
        #     # 停止播放，如果已停止，
        #     # 再次停止时会抛出异常，所以放在异常处理结构中
        #     pygame.mixer.music.stop()
        
        # except:
        #     print("ERRRRRRRRR")
        #     pass
        return 

    def Play_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        #TODO, Please finish the function here!
        # print("Play_Cmd")
        # self.NextSong['state'] = 'normal'
        # self.PreSong['state'] = 'normal'
        # # 选择要播放的音乐文件夹
        # global folder,res,source,floder_path
        # if self.Play['text'] == '播放':
        #     folder = tkFileDialog.askdirectory()
        #     if not folder:
        #         return
        #     source="path"
        #     self.Play['text']='暂停'
        #     musics = [folder + '//' + music
        #         for music in os.listdir(folder) \
        #                 \
        #         if music.endswith(('.mp3', '.wav', '.ogg'))]
        #     res = musics
        #     floder_path=folder
        #     names=[]
        #     for song in musics:
        #         names.append(song.split('//')[1:])
        #         pass
        #     print(names)

        #     self.Set_ResaultBox(res)
        #     global playing
        #     playing = True
        #     # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        #     self.Play['text']='暂停'
        #     t = threading.Thread(target=self.Player)
        #     t.start()
        # elif self.Play['text'] == '暂停':
        #     #pygame.mixer.init()
        #     pygame.mixer.music.pause()
        #     self.Play['text']='继续'
        # elif self.Play['text'] == '继续':
        #     #pygame.mixer.init()
        #     pygame.mixer.music.unpause()
        #     self.Play['text']='暂停'
        #     pass
        # if not playing:
        #     # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        #     playing = True
        #     self.Play['text']='暂停'
        #     t = threading.Thread(target=self.Player)
        #     t.start()
        return 

    def OpenPath_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        #TODO, Please finish the function here!
        print("OpenPath_Cmd")
        # global folder
        # global res
        # global playing
        # global num,source,names,floder_path
        # folder = tkFileDialog.askdirectory()
        # playing = False
        # print(folder)
        # if not folder:
        #     return
        # source="path"
        # musics = [folder + '//' + music
        #     for music in os.listdir(folder) \
        #             \
        #     if music.endswith(('.mp3', '.wav', '.ogg'))]
        # res = musics
        # floder_path=folder
        # names=[]
        # for song in musics:
        #     names.append(song.split('//')[1:])
        #     pass
        # print(names)
        # # print(res)
        # self.Set_ResaultBox(res)
        # if not playing:
        #     self.Set_ResaultBox(res)
        #     # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        #     playing = True
        #     self.Play['text']='暂停'
        #     t = threading.Thread(target=self.Player)
        #     t.start()
        return 

    def Search_Cmd(self, event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        self.checkType()
        # #TODO, Please finish the function here!
        print("Search_Cmd")
        if not searching:
            # # 创建一个线程来检索，当前主线程用来接收用户操作
            searching = True
            self.Search['text']='搜索中'
            s = threading.Thread(target=self.Searcher)
            s.start()
        else:
            self.Search['text']='搜索中断'
            searching=False
            time.sleep(2)
        return 
    
    def Set_ResaultBox(self,event=None):
        # add song name to box
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        self.ResaultBox.delete(0,END)
        if len(datas)<1:
            print("data none")
            return
        if 'http' in word:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['singer'], 50,'L')+word_align(item['name'], 100,'L'))
            return

        if stype=='song' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['singer'], 50,'L')+word_align(item['name'], 100,'L'))
            return

        if stype=='singer' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['name'], 50,'L'))
            return
        
        if stype=='album' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['name'], 50,'L')+word_align(item['artist']['name'], 100,'L'))
            return

        if stype=='list' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['name'], 50,'L')+word_align(item['creator']['nickname'], 30,'L')+word_align(str(item['trackCount'])+"首", 50,'L'))
            return

        if stype=='video' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['title'], 60,'L')+word_align(item['creator'][0]['userName'], 30,'L'))
            return

        if stype=='radio'and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['name'], 50,'L')+word_align(str(item['dj']['nickname']), 30,'L'))
            return

        if stype=='user' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['nickname'], 30,'L')+word_align(str(item['description']), 30,'L'))
            return

        if stype=='lrc' and not local:
            for item in datas:
                self.ResaultBox.insert(END,word_align(item['name'], 30,'L')+word_align(str(item['ar'][0]['name'])+" ", 30,'L'))
            return

        if local:
            for item in datas:
                self.ResaultBox.insert(END, item)
                pass
            return

 
    def ResaultBoxDoubleClick(self, event):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        time.sleep(1)
        num=int(self.ResaultBox.curselection()[0])
        if len(datas)<1:
            return
        if local:
            print('local')
        else:   
            if stype=="list":
                print(datas[num]['id'])
                print(datas[num]['name'])
                stype="song"
                datas=searchMusicListByIdAndCodeAndLimit(p,datas[num]['id'],code)
                self.Set_ResaultBox()
            if stype=="song":
                print()
                current_index=num
                print("current Index:"+str(current_index))
                self.Play_Current_Index()
            if stype=="album":
                stype="song"
                datas=searchMusicAlbumByIdAndCodeAndLimit(p,datas[num]['id'],code)
                self.Set_ResaultBox()
                print()
            if stype=="video":
                downloadVideo(getVideoFilename(p,datas[num]) ,datas[num]['vid'])
                print()
        return 

    def Play_Current_Index(self,event=None):
        global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        downloadSong(datas[current_index])
        if not playing:
            print(playing)
            print("new thread")
            playing = True
            t = threading.Thread(target=self.Player)
            t.start()
            pass
        else:
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
            except:
                print("StopERR PlayINgStop")
                playing=False
                pass

    def Download_Cmd(self, event=None):
        global playnext,downloading,downloadList,datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching,word,backsyc
        print("Download_Cmd")
        self.Download['text']='下载中'
        if stype=="song" and not local:
            downloadList.extend(datas)
        if stype=="album":
            for data in datas:
                datasnew=searchMusicAlbumByIdAndCodeAndLimit(p,data['id'],code)
                downloadList.extend(datasnew)
        if not downloading:
            print("new downloading thread")
            downloading = True
            d = threading.Thread(target=self.Downloader)
            d.start()
            pass
    

def word_align(_string, _length, _type='L'):
    """
    中英文混合字符串对齐函数
    my_align(_string, _length[, _type]) -> str

    :param _string:[str]需要对齐的字符串
    :param _length:[int]对齐长度
    :param _type:[str]对齐方式（'L'：默认，左对齐；'R'：右对齐；'C'或其他：居中对齐）
    :return:[str]输出_string的对齐结果
    """
    _str_len = len(str(_string))  # 原始字符串长度（汉字算1个长度）
    for _char in _string:  # 判断字符串内汉字的数量，有一个汉字增加一个长度
        if u'\u4e00' <= _char <= u'\u9fa5':  # 判断一个字是否为汉字（这句网上也有说是“ <= u'\u9ffff' ”的）
            _str_len += 1
    _space = _length-_str_len  # 计算需要填充的空格数
    if _type == 'L':  # 根据对齐方式分配空格
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space//2
        _right = _space-_left
    return ' '*_left + _string + ' '*_right

def is_nan(x):
    for s in x:
        if s==1 or s=="1": continue
        if s==2 or s=="2": continue
        if s==3 or s=="3": continue
        if s==4 or s=="4": continue
        if s==5 or s=="5": continue
        if s==6 or s=="6": continue
        if s==7 or s=="7": continue
        if s==8 or s=="8": continue
        if s==9 or s=="9": continue
        if s==0 or s=="0": continue
        if s=="+" or s=="." or s=="-": continue
        return True
    return False



def downloadMusicById(filename,mid):
    global p
    bps=""
    if   p=="tencent":
        bps="ape"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicFile(filename.replace("mp3","ape"),url)
        bps="flac"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicFile(filename.replace("mp3","flac"),url)
        bps="320"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicFile(filename,url)
        
    if  p=="netease":
        bps="999000"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicFile(filename,url)

def downloadMusicByIdWithHttp(filename,mid):
    global p
    bps=""
    if   p=="tencent":
        bps="ape"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicByHttpRequest(filename.replace("mp3","ape"),url)
        bps="flac"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicByHttpRequest(filename.replace("mp3","flac"),url)
        bps="320"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicByHttpRequest(filename,url)
        
    if  p=="netease":
        bps="999000"
        url="https://api.itooi.cn/music/%s/url?key=579621905&id=%s&br=%s"%(p,str(mid),bps)
        downloadMusicByHttpRequest(filename,url)
    

def downloadMusicByHttpRequest(filename,url):
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if(url == None or "http" not in url):
        print("urlerr:"+str(url))
        return 3
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests':'1'}
    _filename = tmp_path+re.sub(r'[\/:*?"<>|]','-',filename)
    if  os.path.exists(_filename):
        print("已存在：文件大小："+str(os.path.getsize(_filename)))
        if os.path.getsize(_filename) < 1024000 and ( "mp3" in filename or "mp4" in filename or "flac" in filename or "ape" in filename):
            print("小于1MB的重新下载中")
        else:
            return 0    
    # print("download:"+url+"  as  "+_filename)
    response = requests.get(url, headers=headers)
    try:
        with open(_filename.encode('UTF-8').decode("UTF-8"), 'wb') as f:
            f.write(response.content)
            f.flush()
            f.close()
            return 0
    except Exception as e:
        print(e)
        pass
    finally:
        f.close()

def downloadMusicFile(filename,url):
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if(url == None or "http" not in url):
        print("urlerr:"+str(url))
        return 3
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests':'1'}
    if  os.path.exists(filename):
        print("已存在：文件大小："+str(os.path.getsize(filename)))
        if os.path.getsize(filename) < 1024000 and( "mp3" in filename or "mp4" in filename or "flac" in filename or "ape" in filename):
            print("小于1MB的重新下载中")
        else:
            return 0    
    response = requests.get(url, headers=headers)
    try:
        with open(filename.encode('UTF-8').decode("UTF-8"), 'wb') as f:
            f.write(response.content)
            f.flush()
            f.close()
            return 0
    except Exception as e:
        print(e)
        pass
    


def closeWindow():
    # 修改变量，结束线程中的循环
    global datas,filenames,backsyc,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    searching=False
    playing=False
    backsyc=False
    downloading=False
    print("Suddendenly going die 321...")
    time.sleep(3)
    try:
        # 停止播放，如果已停止，
        # 再次停止时会抛出异常，所以放在异常处理结构中
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception as e:
        print(e)
        pass
    try:
        print( 'killing...')
        time.sleep(3)
        sys.exit(0)
    except Exception as e:
        print(e)
        print( 'Going Die...')
        time.sleep(3)
        os._exit(0)
    finally:
        print( 'Finish Exit')

def searchMusicListByIdAndCodeAndLimit(provider,lid,key):
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    print("searchMusicListByIdAndCodeAndLimit:"+str(provider)+str(lid)+str(key))
    data=None
    r_file=None
    url="https://api.itooi.cn/music/%s/songList?key=%s&id=%s"%(provider,code,lid)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
    # print(f"text = {responseRes.text}")
    if data['code']==2333 or len(data['data'])<1: 
        return []
    if not os.path.exists(tmp_path+str(provider)+"-list-"+str(lid)+"-"+str(key)):
        try:
            r_file = open((tmp_path+str(provider)+"-list-"+str(lid)+"-"+str(key)), "w", encoding="utf-8")
            r_file.write(str(data))
            r_file.flush()
            # print(data['data']['songs'])
            return data['data']['songs']
        except Exception as  e:
            print(e)
        finally:
            r_file.close()
            # print(data['data']['songs'])
            return data['data']['songs']
        return data
    else:
        try:
            with open(tmp_path+str(provider)+"-list-"+str(lid)+"-"+str(key), "r", encoding="utf-8") as r_file:
                data=json.load(r_file)
                print(data)
        except Exception as  e:
            print(e)
        finally:
            # print(data['data']['songs'])
            return data['data']['songs']
        return data

def searchMusicAlbumByIdAndCodeAndLimit(provider,aid,key):
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    print("searchMusicAlbumByIdAndCodeAndLimit:"+str(provider)+str(aid)+str(key))
    data=None
    r_file=None
    url="https://api.itooi.cn/music/%s/album?key=%s&id=%s"%(provider,code,aid)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
    # print(f"text = {responseRes.text}")
    if data['code']==2333 or len(data['data'])<1: 
        return []
    if not os.path.exists(tmp_path+str(provider)+"-album-"+str(aid)+"-"+str(key)):
        try:
            r_file = open((tmp_path+str(provider)+"-album-"+str(aid)+"-"+str(key)), "w", encoding="utf-8")
            r_file.write(str(data))
            r_file.flush()
            # print(data['data']['songs'])
            return data['data']
        except Exception as  e:
            print(e)
        finally:
            r_file.close()
            # print(data['data']['songs'])
            return data['data']
        return data
    else:
        try:
            with open(tmp_path+str(provider)+"-album-"+str(aid)+"-"+str(key), "r", encoding="utf-8") as r_file:
                data=json.load(r_file)
                print(data)
        except Exception as  e:
            print(e)
        finally:
            # print(data['data'])
            return data['data']
        return data


def searchMusicByKeyAndTypeAndLimitAndOffset(keyword,wtype,limit,offset):
    #搜索音乐/专辑/歌词/歌单/MV/用户/歌手/电台搜索
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    print("searchMusicByKeyAndTypeAndLimitAndOffset:"+"keyword:"+str(keyword)+" wtype:"+str(wtype)+"limit:"+str(limit)+" offset:"+str(offset))
    data=None
    r_file=None
    url=" https://api.itooi.cn/music/%s/search?key=%s&s=%s&type=%s&limit=%s&offset=%s"%(p,code,keyword,wtype,limit,offset)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
    # print(f"text = {responseRes.text}")
    
    if data['code'] != 2333 and data['data']!= None and data['data']!='null':
        if not os.path.exists(tmp_path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)) :
            try:
                r_file = open((tmp_path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)), "w", encoding="utf-8")
                r_file.write(str(data))
                r_file.flush()
            except Exception as  e:
                print(e)
            finally:
                r_file.close()
        else:
            try:
                with open((tmp_path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)), "r", encoding="utf-8") as r_file:
                    data=json.load(r_file)
                    print(data)
            except Exception as  e:
                print(e)
            finally:
                r_file.close()
    if  data['code'] == 2333:
        return []
    if data['data']==None or data['data']=='null':
        return []
    if wtype == "song" and data['data'] != None:
        return data['data']
    if wtype == "singer" and data['data']['artists'] != None:
        return data['data']['artists']
    if wtype == "album"and data['data']['albums'] != None:
        return data['data']['albums']
    if wtype == "list"and data['data']['playlistCount'] >offset+2:
        return data['data']['playlists']
    if wtype == "video"and data['data']['videos'] != None:
        return data['data']['videos']
    if wtype == "radio"and len(data['data'])>0:
        return data['data']['djRadios']
    if wtype == "user"and data['data']['userprofiles'] != None:
        return data['data']['userprofiles']
    if wtype == "lrc"and data['data']['songs'] != None:
        return data['data']['songs']
    return []

def downloadSong(data):
    global p
    try:
        downloadMusicByIdWithHttp(getSongFilename(p,data),data['id'])
        downloadMusicByHttpRequest(getLrcFilename(p,data),data['lrc'])
        downloadMusicByHttpRequest(getPicFilename(p,data),data['pic'])
    except Exception as e:
        print(e)
    
def downloadMusic(data):
    global p
    for song in data:
        try:
            downloadMusicByIdWithHttp(getSongFilename(p,song),song['id'])
            downloadMusicByHttpRequest(getLrcFilename(p,song),song['lrc'])
            downloadMusicByHttpRequest(getPicFilename(p,song),song['pic'])
        except Exception as e:
            print(e)

def downloadVideo(filename,vid):
    global p
    bps="1080"
    if  p=="tencent":
        bps="4"
        url="https://api.itooi.cn/music/%s/mvUrl?key=579621905&id=%s&r=%s"%(p,vid,bps)
        downloadMusicFile(filename,url)    
    if  p=="netease":
        bps="1080"
        url="https://api.itooi.cn/music/%s/mvUrl?key=579621905&id=%s&r=%s"%(p,vid,bps)
        downloadMusicFile(filename,url)
        

def getSongFilename(provider,song):
    if provider ==None:
        return re.sub(r'[\/:*?"<>|]','-',song['singer']+"-"+song['name']+".mp3")
    return     re.sub(r'[\/:*?"<>|]','-',str(provider)+'-'+song['id']+"-"+song['singer']+"-"+song['name']+".mp3")

def getVideoFilename(provider,video):
    if provider ==None:
        return re.sub(r'[\/:*?"<>|]','-',video['title']+".mp4")
    return re.sub(r'[\/:*?"<>|]','-',str(provider)+'-'+video['title']+".mp4")

def getLrcFilename(provider,song):
    if provider ==None:
        return re.sub(r'[\/:*?"<>|]','-',song['singer']+"-"+song['name']+".lrc")
    return re.sub(r'[\/:*?"<>|]','-',str(provider)+'-'+song['id']+"-"+song['singer']+"-"+song['name']+".lrc")

def getPicFilename(provider,song):
    if provider ==None:
        return re.sub(r'[\/:*?"<>|]','-',song['singer']+"-"+song['name']+".jpg")
    return re.sub(r'[\/:*?"<>|]','-',str(provider)+'-'+song['id']+"-"+song['singer']+"-"+song['name']+".jpg")

def getSongDetialById(provider,key,sid):
    #   "id": "526307800",
    #     "name": "123我爱你",
    #     "singer": "新乐尘符",
    #     "pic": "http://p1.music.126.net/_LNk7rEEBSdAcnyHL8zi6Q==/109951163093399018.jpg?param=400y400",
    #     "lrc": "https://api.itooi.cn/music/netease/lrc?id=526307800&key=579621905",
    #     "url": "https://api.itooi.cn/music/netease/url?id=526307800&key=579621905",
    #     "time": 199
    global datas,filenames,defaultHeader,ajaxheaders,download_path,tmp_path,play_path,webSession,current_index,local,code,p,stype,nowThreads,downloadingThreads,downloading,playing,searching
    print("getSongDetialById:"+str(provider)+str(key)+str(sid))
    data=None
    if not os.path.exists(tmp_path+str(provider)+"-song-"+str(key)+"-"+str(sid)):
        url="https://api.itooi.cn/music/%s/song?key=%s&id=%s"%(provider,key,sid)
        responseRes=webSession.get(url,  headers = ajaxheaders)
        data = json.loads(responseRes.text)
        # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
        # print(f"text = {responseRes.text}")
        try:
            r_file = open((tmp_path+str(provider)+"-song-"+str(key)+"-"+str(sid)), "w", encoding="utf-8")
            r_file.write(str(data))
            r_file.flush()
            return data['data']
        except Exception as  e:
            print(e)
            responseRes.text
        finally:
            r_file.close()
            return data['data']
    else:
        try:
            with open((tmp_path+str(provider)+"-song-"+str(key)+"-"+str(sid)), "r", encoding="utf-8") as r_file:
                data= json.load(r_file)
            return data['data']
        except Exception as  e:
            print(e)
        finally:
            r_file.close()
            return data['data']
    return data

if __name__ == "__main__":
    top = Tk()
    top.protocol('WM_DELETE_WINDOW', closeWindow)
    Application(top).mainloop()
    try: top.destroy()
    except: 
        print("MAIN ERR")
        pass
