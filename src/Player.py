#!/usr/bin/env python
#-*- coding:utf-8 -*-


import json
import os
import re
import sys
import threading
import time
import pygame
import requests

try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    print(f"python2.")
    import cookielib
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    print(f"python3.")
    import http.cookiejar as cookielib
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()

download_path = "./downloads/"
tmp_path = download_path+"/tmp/"
play_path="./downloads/"
code="579621905"
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
data_resault=[]
data_download=[]
data_playing=[]
current_Playing=-1
#global data_resault,data_download,data_playing

class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('MyazureMusicPlayer  WangZhen-wangzhenjjcn@gmail.com V2.0 FLAC APE MP3 2019-4-16-12:56')
        self.master.geometry('1280x600')
        self.master.resizable(0,0)
        self.createWidgets()
        self.Volume.set(60)
        self.CreatSingerPathVar.set(1)
        self.DownloadAlbumPicVar.set(1)
        self.DownloadAlbumPicVar.set(1)
        self.HighQualityVar.set(1)
        self.DownloadLrcVar.set(1)

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('DownloadFrame.TLabelframe',font=('宋体',9))
        self.DownloadFrame = LabelFrame(self.top, text='正在下载', style='DownloadFrame.TLabelframe')
        self.DownloadFrame.place(relx=0.431, rely=0., relwidth=0.57, relheight=0.522)

        self.style.configure('PlayFrame.TLabelframe',font=('宋体',9))
        self.PlayFrame = LabelFrame(self.top, text='正在播放', style='PlayFrame.TLabelframe')
        self.PlayFrame.place(relx=0.431, rely=0.533, relwidth=0.57, relheight=0.468)

        self.ResaultListVar = StringVar(value='ResaultList')
        self.ResaultListFont = Font(font=('YaHei Consolas Hybrid',9))
        self.ResaultList = Listbox(self.top, listvariable=self.ResaultListVar, font=self.ResaultListFont,selectmode=EXTENDED)
        self.ResaultList.place(relx=0., rely=0.053, relwidth=0.432, relheight=0.947)
        self.ResaultList.bind('<Double-Button-1>',self.ResaultListDoubleClick)
        self.ResaultList.bind('<ButtonRelease-1>',self.ResaultListLeftClick)


        self.SearchTpyeList = ['音乐搜索','歌手搜索','专辑搜索','视频搜索','电台搜索','用户搜索','歌词搜索','歌单搜索',]
        self.SearchTpye = Combobox(self.top, values=self.SearchTpyeList, font=('宋体',12))
        self.SearchTpye.place(relx=0.125, rely=0., relwidth=0.113, relheight=0.04)
        self.SearchTpye.set(self.SearchTpyeList[0])
        self.SearchTpye.bind('<<ComboboxSelected>>',self.SearchTpyeChecked)

        self.ProviderList = ['QQ音乐','网易云音乐',]
        self.Provider = Combobox(self.top, values=self.ProviderList, font=('宋体',12))
        self.Provider.place(relx=0., rely=0., relwidth=0.125, relheight=0.04)
        self.Provider.set(self.ProviderList[0])
        self.Provider.bind('<<ComboboxSelected>>',self.ProviderChecked)

        self.SearchWordVar = StringVar(value='关键字')
        self.SearchWord = Entry(self.top, text='关键字', textvariable=self.SearchWordVar, font=('宋体',12))
        self.SearchWord.place(relx=0.238, rely=0., relwidth=0.195, relheight=0.04)
        self.SearchWord.bind('<Return>',self.Search_Cmd)
        self.SearchWord.bind('<ButtonRelease-1>',self.SearchWordLeftClick)

        self.style.configure('CancelDownload.TButton',font=('宋体',9))
        self.CancelDownload = Button(self.DownloadFrame, text='停止下载', command=self.CancelDownload_Cmd, style='CancelDownload.TButton')
        self.CancelDownload.place(relx=0.209, rely=0.843, relwidth=0.144, relheight=0.105)
        self.CancelDownload.bind('<Enter> ',self.checkFileFormartAndSettings)

        self.style.configure('SetDownloadPath.TButton',font=('宋体',9))
        self.SetDownloadPath = Button(self.DownloadFrame, text='设置下载目录', command=self.SetDownloadPath_Cmd, style='SetDownloadPath.TButton')
        self.SetDownloadPath.place(relx=0.56, rely=0.843, relwidth=0.144, relheight=0.105)
        self.SetDownloadPath.bind('<Enter> ',self.checkFileFormartAndSettings)

        self.style.configure('ClearDownload.TButton',font=('宋体',9))
        self.ClearDownload = Button(self.DownloadFrame, text='清空下载', command=self.ClearDownload_Cmd, style='ClearDownload.TButton')
        self.ClearDownload.place(relx=0.384, rely=0.843, relwidth=0.144, relheight=0.105)
        self.ClearDownload.bind('<Enter> ',self.checkFileFormartAndSettings)

        self.DownloadAlbumPicVar = StringVar(value='0')
        self.style.configure('DownloadAlbumPic.TCheckbutton',font=('宋体',9))
        self.DownloadAlbumPic = Checkbutton(self.DownloadFrame, text='下载专辑封面', variable=self.DownloadAlbumPicVar, style='DownloadAlbumPic.TCheckbutton')
        self.DownloadAlbumPic.place(relx=0.044, rely=0.588, relwidth=0.155, relheight=0.08)

        self.DownloadLrcVar = StringVar(value='0')
        self.style.configure('DownloadLrc.TCheckbutton',font=('宋体',9))
        self.DownloadLrc = Checkbutton(self.DownloadFrame, text='下载歌词', variable=self.DownloadLrcVar, style='DownloadLrc.TCheckbutton')
        self.DownloadLrc.place(relx=0.044, rely=0.511, relwidth=0.155, relheight=0.08)

        self.CreatSingerPathVar = StringVar(value='0')
        self.style.configure('CreatSingerPath.TCheckbutton',font=('宋体',9))
        self.CreatSingerPath = Checkbutton(self.DownloadFrame, text='创建歌手目录', variable=self.CreatSingerPathVar, style='CreatSingerPath.TCheckbutton')
        self.CreatSingerPath.place(relx=0.044, rely=0.435, relwidth=0.155, relheight=0.08)

        self.DownloadListVar = StringVar(value='DownloadList')
        self.DownloadListFont = Font(font=('YaHei Consolas Hybrid',9))
        self.DownloadList = Listbox(self.DownloadFrame, listvariable=self.DownloadListVar, font=self.DownloadListFont)
        self.DownloadList.place(relx=0.209, rely=0.051, relwidth=0.77, relheight=0.703)

        self.style.configure('Download_Selected.TButton',font=('宋体',9))
        self.Download_Selected = Button(self.DownloadFrame, text='下载选中', command=self.Download_Selected_Cmd, style='Download_Selected.TButton')
        self.Download_Selected.place(relx=0.033, rely=0.716, relwidth=0.144, relheight=0.105)
        self.Download_Selected.bind('<Enter> ',self.checkFileFormartAndSettings)

        self.style.configure('Download_All.TButton',font=('宋体',9))
        self.Download_All = Button(self.DownloadFrame, text='下载所有', command=self.Download_All_Cmd, style='Download_All.TButton')
        self.Download_All.place(relx=0.033, rely=0.843, relwidth=0.144, relheight=0.105)
        self.Download_All.bind('<Enter> ',self.checkFileFormartAndSettings)

        self.HighQualityVar = BooleanVar(value='1')
        self.style.configure('HighQuality.TCheckbutton',font=('宋体',9))
        self.HighQuality = Checkbutton(self.DownloadFrame, text='FLAC', variable=self.HighQualityVar, style='HighQuality.TCheckbutton',onvalue=True,offvalue=False)
        self.HighQuality.place(relx=0.044, rely=0.102, relwidth=0.122, relheight=0.08)
        self.HighQuality.bind('<Leave> ',self.checkFileFormartAndSettings)

        self.MidQualityVar =  BooleanVar(value='0')
        self.style.configure('MidQuality.TCheckbutton',font=('宋体',9))
        self.MidQuality = Checkbutton(self.DownloadFrame, text='APE', variable=self.MidQualityVar, style='MidQuality.TCheckbutton',onvalue=True,offvalue=False)
        self.MidQuality.place(relx=0.044, rely=0.179, relwidth=0.122, relheight=0.08)
        self.MidQuality.bind('<Leave>',self.checkFileFormartAndSettings)

        self.LowQualityVar = BooleanVar(value='0')
        self.style.configure('LowQuality.TCheckbutton',font=('宋体',9))
        self.LowQuality = Checkbutton(self.DownloadFrame, text='MP3', variable=self.LowQualityVar, style='LowQuality.TCheckbutton',onvalue=True,offvalue=False)
        self.LowQuality.place(relx=0.044, rely=0.256, relwidth=0.122, relheight=0.08)
        self.LowQuality.bind('<Leave>',self.checkFileFormartAndSettings)

        self.style.configure('DownloadPathInfo.TLabel',anchor='w', font=('宋体',9))
        self.DownloadPathInfo = Label(self.DownloadFrame, text='当前目录：./Downnload/', style='DownloadPathInfo.TLabel',wraplength = 180)
        self.DownloadPathInfo.place(relx=0.724, rely=0.818, relwidth=0.265, relheight=0.131)

        self.style.configure('Label1.TLabel',anchor='w', font=('宋体',9))
        self.Label1 = Label(self.DownloadFrame, text='下载选项：', style='Label1.TLabel')
        self.Label1.place(relx=0.033, rely=0.383, relwidth=0.1, relheight=0.054)

        self.style.configure('DownloadLable.TLabel',anchor='w', font=('宋体',9))
        self.DownloadLable = Label(self.DownloadFrame, text='文件格式：', style='DownloadLable.TLabel')
        self.DownloadLable.place(relx=0.033, rely=0.051, relwidth=0.1, relheight=0.054)

        self.style.configure('Stop.TButton',font=('宋体',9))
        self.Stop = Button(self.PlayFrame, text='停止', command=self.Stop_Cmd, style='Stop.TButton')
        self.Stop.place(relx=0.812, rely=0.085, relwidth=0.144, relheight=0.117)

        self.style.configure('Next_Song.TButton',font=('宋体',9))
        self.Next_Song = Button(self.PlayFrame, text='下一首', command=self.Next_Song_Cmd, style='Next_Song.TButton')
        self.Next_Song.place(relx=0.658, rely=0.085, relwidth=0.144, relheight=0.117)

        self.style.configure('Pre_Song.TButton',font=('宋体',9))
        self.Pre_Song = Button(self.PlayFrame, text='上一首', command=self.Pre_Song_Cmd, style='Pre_Song.TButton')
        self.Pre_Song.place(relx=0.505, rely=0.085, relwidth=0.144, relheight=0.117)

        self.style.configure('Pause.TButton',font=('宋体',9))
        self.Pause = Button(self.PlayFrame, text='暂停', command=self.Pause_Cmd, style='Pause.TButton')
        self.Pause.place(relx=0.351, rely=0.085, relwidth=0.144, relheight=0.117)

        self.style.configure('Play.TButton',font=('宋体',9))
        self.Play = Button(self.PlayFrame, text='播放', command=self.Play_Cmd, style='Play.TButton')
        self.Play.place(relx=0.198, rely=0.085, relwidth=0.144, relheight=0.117)

        self.style.configure('Open_Path.TButton',font=('宋体',9))
        self.Open_Path = Button(self.PlayFrame, text='打开', command=self.Open_Path_Cmd, style='Open_Path.TButton')
        self.Open_Path.place(relx=0.044, rely=0.085, relwidth=0.144, relheight=0.117)

        self.PlayListVar = StringVar(value='PlayList')
        self.PlayListFont = Font(font=('YaHei Consolas Hybrid',9))
        self.PlayList = Listbox(self.PlayFrame, listvariable=self.PlayListVar, font=self.PlayListFont)
        self.PlayList.place(relx=0.209, rely=0.285, relwidth=0.77, relheight=0.612)
        self.PlayList.bind('<Double-Button-1>',self.PlayListDoubleClick)

        self.Volume = Scale(self.PlayFrame, orient='vertical', from_=100, to=0)
        self.Volume.place(relx=0.132, rely=0.256, relwidth=0.04, relheight=0.63)
        self.Volume.bind('<ButtonRelease-1>',self.SettingVolume)

        self.style.configure('VolumeLable.TLabel',anchor='w', font=('宋体',9))
        self.VolumeLable = Label(self.PlayFrame, text='音量：', style='VolumeLable.TLabel')
        self.VolumeLable.place(relx=0.044, rely=0.285, relwidth=0.067, relheight=0.06)
class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        if self.DownloadList.size()>0:
            if self.DownloadList.get(0)=="DownloadList":
                self.DownloadList.delete(0,END)
        if self.ResaultList.size()>0:
            if self.ResaultList.get(0)=="ResaultList":
                self.ResaultList.delete(0,END)
        if self.PlayList.size()>0:
            if self.PlayList.get(0)=="PlayList":
                self.PlayList.delete(0,END)                
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)

    def Searcher(self,event=None):
        global data_resault
        data_resault=[]
        if self.ResaultList.size()>0:
            if self.ResaultList.get(0)=="ResaultList":
                self.ResaultList.delete(0,END)        
        print("Search")
        datas=[]
        self.ResaultList.delete(0,END)
        while self.Download_All['text']=="搜索中":
            if getTypeByCombobox(self.SearchTpye) == "song" or getTypeByCombobox(self.SearchTpye)  == "list"  or getTypeByCombobox(self.SearchTpye)  == "video" or getTypeByCombobox(self.SearchTpye)  == "radio" or  getTypeByCombobox(self.SearchTpye)  == "user":
                if self.Provider.current() ==0 :
                    data=searchMusic(tmp_path,getProvider(self.Provider),self.SearchWord.get(),getTypeByCombobox(self.SearchTpye),50,0)
                    n=0
                    while len(data)>0:
                        print(len(data))
                        datas.extend(data)
                        data_resault.extend(data)
                        for item in data:
                            insertDataToListbox(item,self.ResaultList,END)
                        print(len(datas))
                        n=n+1
                        data=searchMusic(tmp_path,getProvider(self.Provider),self.SearchWord.get(),getTypeByCombobox(self.SearchTpye),50,n)
                if self.Provider.current() ==1:
                    data=searchMusic(tmp_path,getProvider(self.Provider),self.SearchWord.get(),getTypeByCombobox(self.SearchTpye),50,len(datas))
                    while len(data)>0:
                        print(len(data))
                        datas.extend(data)
                        data_resault.extend(data)
                        for item in data:
                            insertDataToListbox(item,self.ResaultList,END)
                        print(len(datas))
                        data=searchMusic(tmp_path,getProvider(self.Provider),self.SearchWord.get(),getTypeByCombobox(self.SearchTpye),50,len(datas))
                if getTypeByCombobox(self.SearchTpye) == "singer" or getTypeByCombobox(self.SearchTpye) == "album" or getTypeByCombobox(self.SearchTpye) == "lrc":
                    data=searchMusic(tmp_path,getProvider(self.Provider),self.SearchWord.get(),getTypeByCombobox(self.SearchTpye),100,0)
                    datas.extend(data)    
                    data_resault.extend(data)
                    for item in data:
                        insertDataToListbox(item,self.ResaultList,END)
            if getTypeByCombobox(self.SearchTpye)=="video" and getProvider(self.Provider)=="netease":
                for i in range(0,len(datas)):
                    if  is_nan(datas[i]['vid']):
                        # self.ResaultBox.itemconfig(i,bg="#990000")
                        print(str(i)+"is nan")
            if len(datas)<1:
                print("data none")
            self.setFileFormartAndSettings()
            self.searchUnLock()
            # data_resault=datas.copy()

    def Downloader(self,event=None):
        if self.DownloadList.size()>0:
            if self.DownloadList.get(0)=="DownloadList":
                self.DownloadList.delete(0,END)
        global data_resault,data_download,data_playing
        print()     
        while len(data_download)>0  and "中" in self.Download_All['text']:
            data=data_download.pop(0)
            self.DownloadList.delete(0,None)
            print(data)
            if "path" in data:
                if not os.path.exists(data['path']):
                    os.mkdir(data['path']) 
            if "filename" in data and  "path" in data and "quality" in data and "id" in data:
                self.DownloadFrame['text']="正在下载："+data['filename']
                downloadMusicById(data['path'],data['filename'],getProvider(self.Provider),code,data['id'],data['quality'])
            if data['download_lrc'] :
                downloadFile(data['path'],re.sub(r'[\/:*?"<>|]','-',(data['singer']+"-"+data['name']+".lrc")),data['lrc'])
            if data['download_pic']:
                downloadFile(data['path'],re.sub(r'[\/:*?"<>|]','-',(data['singer']+"-"+data['name']+".jpg")),data['pic'])
            if 'mp3' in data['filename']:
                data_playing.append(data.copy())
                insertDataToListbox(data.copy(),self.PlayList,END)
            if len(self.PlayList.curselection())<1 and self.PlayList.size()>0:
                    self.PlayList.select_set(0)  

        self.downloadUnLock()  
        self.DownloadFrame['text']="正在下载："  

    def Player(self,event=None):
        if(self.PlayList.size()<1 or len(self.PlayList.curselection())<1):
            self.Play['text']="播放"
            return
        pygame.mixer.init()
        current_index=self.PlayList.curselection()[0]
        songtime=0
        lrc={}
        lrcword=""
        while self.Play['text']!="播放" and len(self.PlayList.curselection())>0:    
            if   pygame.mixer.music.get_busy()==False and self.PlayList.size()>0 and self.Play['text']!="播放": 
                if pygame.mixer.music.get_busy() != False:
                    try:
                        pygame.mixer.music.stop()
                    except Exception as e:
                        print(e)
                    return
                if self.PlayList.size() < 1:
                    try:
                        pygame.mixer.music.stop()

                    except Exception as e:
                        print(e)
                        return
                if self.Play['text'] == "播放":
                    try:
                        pygame.mixer.music.stop()

                    except Exception as e:
                        print(e)
                        return
                lrc={}
                lrcword=""
                if current_index==-1:
                    self.Play['text']="播放"
                    continue
                song=data_playing[self.PlayList.curselection()[0]]
                songtime=int(song['time'])
                try:
                    pygame.mixer.music.load(song['path']+song['filename'])
                    if os.path.exists(song['path']+(song['singer']+"-"+song['name']+".lrc")):
                        lrc=getLrc(song['path']+re.sub(r'[\/:*?"<>|]','-',(song['singer']+"-"+song['name']+".lrc")))
                    if "00:00:00" in lrc:
                        lrcword=lrc["00:00:00"]
                    if "00:00.00" in lrc:
                        lrcword=lrc["00:00.00"]
                    pygame.mixer.music.play(loops=0, start=0.0)
                    pygame.mixer.music.set_volume(1) 
                except Exception as e:
                    print(e)
                if self.PlayList.curselection()[0]<self.PlayList.size():
                    if self.PlayList.size()-1 == self.PlayList.curselection()[0]:
                        self.PlayList.select_set(0)
                    else:
                        self.PlayList.select_set(self.PlayList.curselection()[0]+1)
                else:
                    self.PlayList.select_set(0)    


            else:
                time.sleep(0.1)
                if songtime<=0 or songtime ==None :
                    continue
                ntime=int(pygame.mixer.music.get_pos())
                
                for i in range(0,99):
                    atime=ntime+i*10   
                    stime="%02d:%02d.%02d" % (int(atime/60000), int(atime/1000)%60, (atime/10)%100)
                    dtime="%02d:%02d:%02d" % (int(atime/60000), int(atime/1000)%60, (atime/10)%100)
                    if str(stime) in lrc:
                        lrcword=lrc[str(stime)]
                    if str(dtime) in lrc:
                        lrcword=lrc[str(dtime)]
                self.PlayFrame['text']="正在播放："+song['filename']+"  "+str(lrcword)
        self.Play['text']="播放" 
        return 

    def searchUnLock(self,event=None):
        self.Download_All['text']='下载所有'
        self.Download_All.config(state="NORMAL")
        self.Download_Selected.config(state="NORMAL")
        self.CreatSingerPath.config(state="NORMAL")
        self.DownloadAlbumPic.config(state="NORMAL")
        self.DownloadLrc.config(state="NORMAL")
        self.HighQuality.config(state="NORMAL")
        self.MidQuality.config(state="NORMAL")
        self.LowQuality.config(state="NORMAL")
        self.SearchWord.config(state="NORMAL")
        self.SearchTpye.config(state="NORMAL")
        self.Provider.config(state="NORMAL")
        self.setFileFormartAndSettings()

    def searchLock(self,event=None):
        self.Download_All['text']='搜索中'  
        self.Download_All.config(state="disable")
        self.Download_Selected.config(state="disable")
        self.SearchWord.config(state="disable")
        self.SearchTpye.config(state="disable")
        self.Provider.config(state="disable")
        if self.ResaultList.size()>0:
            if self.ResaultList.get(0)=="ResaultList":
                self.ResaultList.delete(0,END)

    def downloadLock(self,event=None):
        self.Download_All['text']='下载中...'
        self.Download_Selected['text']='下载中...'
        self.Download_All.config(state="disable")
        self.CreatSingerPath.config(state="disable")
        self.DownloadAlbumPic.config(state="disable")
        self.DownloadLrc.config(state="disable")
        self.Download_Selected.config(state="disable")
        self.SearchWord.config(state="disable")
        self.SearchTpye.config(state="disable")
        self.Provider.config(state="disable")
        if self.DownloadList.size()>0:
            if self.DownloadList.get(0)=="DownloadList":
                self.DownloadList.delete(0,END)
    
    def downloadUnLock(self,event=None):
        self.Download_All['text']='下载所有'
        self.Download_Selected['text']='下载选中'
        self.Download_All.config(state="NORMAL")
        self.Download_Selected.config(state="NORMAL")
        self.CreatSingerPath.config(state="NORMAL")
        self.DownloadAlbumPic.config(state="NORMAL")
        self.DownloadLrc.config(state="NORMAL")
        self.HighQuality.config(state="NORMAL")
        self.MidQuality.config(state="NORMAL")
        self.LowQuality.config(state="NORMAL")
        self.SearchWord.config(state="NORMAL")
        self.SearchTpye.config(state="NORMAL")
        self.Provider.config(state="NORMAL")
        self.setFileFormartAndSettings()

    def clearResaultList(self,event=None):
        self.ResaultList.delete(0,END)

    def clearDownloadList(self,event=None):
        self.DownloadList.delete(0,END)

    def SettingVolume(self,event=None):
        print(self.Volume.get())
        if  self.Play['text']=="播放":
            pass
        else:
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.set_volume((self.Volume.get()/100))
            except:
                print("StopERR PlayINgStop")
                
                pass

    def setFileFormartAndSettings(self,event=None):
        if self.Provider.current() ==0  and self.SearchTpye.current()==0:
          
            self.HighQuality.config(state="NORMAL")
            self.MidQuality.config(state="NORMAL")
            self.LowQuality.config(state="NORMAL")
            self.HighQuality['text']="FLAC"
            self.MidQuality['text']="APE"
            self.LowQuality['text']="MP3 320K"
            #  128000 192000 320000 999000
            self.checkFileFormartAndSettings()
            return
        if self.Provider.current() ==0  and self.SearchTpye.current()==3:
            self.HighQuality.config(state="NORMAL")
  
            self.MidQuality.config(state="NORMAL")
            self.LowQuality.config(state="NORMAL")
            self.HighQuality['text']="MP4 1080p"
            self.MidQuality['text']="MP4 720p"
            self.LowQuality['text']="MP4 480p"
            #   视频大小类型：1:360 2：480 3:720 4:1080
            self.checkFileFormartAndSettings()
            return
        if self.Provider.current() ==1 and self.SearchTpye.current()==0:
            self.HighQuality.config(state="NORMAL")
 
            self.MidQuality.config(state="NORMAL")
            self.LowQuality.config(state="NORMAL")
            self.HighQuality['text']="MP3 320K"
            self.MidQuality['text']="MP3 192K"
            self.LowQuality['text']="MP3 128K"
            #  128000 192000 320000 999000
            self.checkFileFormartAndSettings()
            return
        if self.Provider.current() ==1  and self.SearchTpye.current()==3:
            self.HighQuality.config(state="NORMAL")
 
            self.MidQuality.config(state="NORMAL")
            self.LowQuality.config(state="NORMAL")
            self.HighQuality['text']="MP4 1080p"
            self.MidQuality['text']="MP4 720p"
            self.LowQuality['text']="MP4 480p"
            self.checkFileFormartAndSettings()
            return
            #  视频大小类型：1080 720 480 240
        self.HighQuality['text']="高质量"
        self.MidQuality['text']="一般质量"
        self.LowQuality['text']="试听质量"
        self.HighQuality.config(state="disable")
        self.MidQuality.config(state="disable")
        self.LowQuality.config(state="disable")
        self.Download_All.config(state="disable")
        self.Download_Selected.config(state="disable")
        self.checkFileFormartAndSettings()
        
    def checkFileFormartAndSettings(self,event=None):

        if self.ResaultList.size()<1:
            self.Download_All.config(state="disable")
            self.Download_Selected.config(state="disable")
             
        elif len(self.ResaultList.curselection())<1:
            self.Download_Selected.config(state="disable")
            self.Download_All.config(state="NORMAL")
             
        else:
            self.Download_All.config(state="NORMAL")
            self.Download_Selected.config(state="NORMAL")
          
        if  not self.HighQualityVar.get() :
            if not  self.MidQualityVar.get()  :
                if  not   self.LowQualityVar.get():
                    if  not self.HighQualityVar.get() :
                        self.Download_All.config(state="disable")
                        self.Download_Selected.config(state="disable")
                        
        if self.DownloadList.size()<1:
            self.CancelDownload.config(state="disable")
            self.ClearDownload.config(state="disable")
            self.SetDownloadPath.config(state="NORMAL")

        if "中" in self.Download_All['text']:
            self.Download_All.config(state="disable")
            self.Download_Selected.config(state="disable")
            self.CancelDownload.config(state="NORMAL")
            self.ClearDownload.config(state="NORMAL")
            self.SetDownloadPath.config(state="disable")
            self.CreatSingerPath.config(state="disable")
            self.DownloadAlbumPic.config(state="disable")
            self.DownloadLrc.config(state="disable")
            self.HighQuality.config(state="disable")
            self.MidQuality.config(state="disable")
            self.LowQuality.config(state="disable")
            self.SearchWord.config(state="disable")
            self.SearchTpye.config(state="disable")
            self.Provider.config(state="disable")

    def SearchWordLeftClick(self, event=None):
        print("SearchWordLeftClick")
        if self.SearchWord.get()=="关键字":
            self.SearchWordVar = StringVar(value='')
        pass

    def Search_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Search_Cmd")
        if not self.Download_All['text']=="搜索中" and self.Download_All['text']=="下载所有":
            # # 创建一个线程来检索，当前主线程用来接收用户操作
            self.searchLock()
            s = threading.Thread(target=self.Searcher)
            s.start()
        else:
            self.searchUnLock()
            time.sleep(2)
            return 
        pass

    def ProviderChecked(self, event=None):
        #TODO, Please finish the function here!
        # current = self.Provider.current()
        # value = self.ProviderList[current]
        # print("current:", current, "value:", value)
        self.setFileFormartAndSettings()
        pass

    def SearchTpyeChecked(self, event=None):
        #TODO, Please finish the function here!
        # current = self.SearchTpye.current()
        # value = self.SearchTpyeList[current]
        # print("current:", current, "value:", value)
        self.setFileFormartAndSettings()
        pass

    def PlayListDoubleClick(self, event=None):
        #TODO, Please finish the function here!
        print("PlayListDoubleClick")
        if  self.Play['text']=="播放":
            self.Play['text']="停止"
            p = threading.Thread(target=self.Player)
            p.start()
            pass
        else:
            
             
            try:
                if pygame.mixer.music.get_busy():
                     
                   
                    pygame.mixer.music.stop()
            except Exception as e:
                print(e)
                print("StopERR PlayINgStop")
                self.Play['text']=="播放"

                try:                     
                    pygame.mixer.quit()
                except Exception as e2:
                    print(e2)
                pass
        pass


    def ResaultListDoubleClick(self, event=None):
        #TODO, Please finish the function here!
        print("ResaultListDoubleClick")
        self.Download_Selected_Cmd()
        pass

    def ResaultListLeftClick(self, event=None):
        #TODO, Please finish the function here!
        print(self.ResaultList.size())
        print("ResaultListLeftClick")
        print(self.ResaultList.curselection())
        # num=int(self.ResaultList.curselection()[0])
        # print(num)
        # print(self.ResaultList.get(num))
        # self.ResaultList.itemconfig(num,fg="#FFFFFF")
        # self.ResaultList.itemconfig(num,bg="#6600FF")
        pass

    def CancelDownload_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("CancelDownload_Cmd")
        if   ("中" in self.Download_All['text']):
            self.downloadUnLock()
            self.Download_All['text']='下载所有'
            self.Download_Selected['text']='下载选中'
            self.CancelDownload['text']="继续下载"
        else:
            self.CancelDownload['text']="停止下载"

    def SetDownloadPath_Cmd(self, event=None):
        #TODO, Please finish the function here!
        global download_path,tmp_path
        folder = tkFileDialog.askdirectory()
        if not folder:
            return
        else:
            download_path=folder+"/"
            tmp_path = download_path+"/tmp/"
            print( folder)
            print(download_path)
            print(tmp_path)
        pass
        self.DownloadPathInfo['text']="当前目录："+download_path

    def ClearDownload_Cmd(self, event=None):
        #TODO, Please finish the function here!
        self.CancelDownload_Cmd()
        self.DownloadList.delete(0,END)
        pass

    def Download_Selected_Cmd(self, event=None):
        global data_resault,data_download,data_playing
        print(self.ResaultList.curselection())
        print("Download_Selected_Cmd")
        if not ("中" in self.Download_All['text']):
            self.downloadLock()
            for num in self.ResaultList.curselection():
                data=[]
                data.append(data_resault[num].copy())
                data.append(data_resault[num].copy())
                data.append(data_resault[num].copy())
                if self.Provider.current() ==0  and self.SearchTpye.current()==0:
                    data[0]['quality']="flac"
                    data[1]['quality']="ape"
                    data[2]['quality']="320"
                    data[0]['extension']="flac"
                    data[1]['extension']="ape"
                    data[2]['extension']="mp3"
                if self.Provider.current() ==0  and self.SearchTpye.current()==3:
                    data[0]['quality']="4"
                    data[1]['quality']="3"
                    data[2]['quality']="2"
                    data[0]['extension']="mp4"
                    data[1]['extension']="mp4"
                    data[2]['extension']="mp4"
                if self.Provider.current() ==1  and self.SearchTpye.current()==0:
                    data[0]['quality']="999000"
                    data[1]['quality']="320000"
                    data[2]['quality']="128000"
                    data[0]['extension']="mp3"
                    data[1]['extension']="mp3"
                    data[2]['extension']="mp3"
                if self.Provider.current() ==1  and self.SearchTpye.current()==3:
                    data[0]['quality']="1080"
                    data[1]['quality']="720"
                    data[2]['quality']="480"
                    data[0]['extension']="mp4"
                    data[1]['extension']="mp4"
                    data[2]['extension']="mp4"
                if self.CreatSingerPathVar.get():
                    data[0]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[0]['singer'])+"/"
                    data[1]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[1]['singer'])+"/"
                    data[2]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[2]['singer'])+"/"
                    data[0]['filename']=re.sub(r'[\/:*?"<>|]','-',data[0]['name']+"."+data[0]['extension'])
                    data[1]['filename']=re.sub(r'[\/:*?"<>|]','-',data[1]['name']+"."+data[1]['extension'])
                    data[2]['filename']=re.sub(r'[\/:*?"<>|]','-',data[2]['name']+"."+data[2]['extension'])
                else:
                    data[0]['path']=download_path
                    data[1]['path']=download_path
                    data[2]['path']=download_path
                    data[0]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[0]['singer']+"-"+data[0]['name']+"."+data[0]['extension']))
                    data[1]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[1]['singer']+"-"+data[1]['name']+"."+data[1]['extension']))
                    data[2]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[2]['singer']+"-"+data[2]['name']+"."+data[2]['extension']))      
                data[0]['download_pic']=self.DownloadAlbumPicVar.get()
                data[0]['download_lrc']=self.DownloadLrcVar.get()
                data[0]['creat_path']=self.CreatSingerPathVar.get()
                data[1]['download_pic']=self.DownloadAlbumPicVar.get()
                data[1]['download_lrc']=self.DownloadLrcVar.get()
                data[1]['creat_path']=self.CreatSingerPathVar.get()
                data[2]['download_pic']=self.DownloadAlbumPicVar.get()
                data[2]['download_lrc']=self.DownloadLrcVar.get()
                data[2]['creat_path']=self.CreatSingerPathVar.get()
                if self.HighQualityVar.get():
                    data_download.append(data[0])
                    insertDataToListbox(data[0],self.DownloadList,END)
                if self.MidQualityVar.get():
                    data_download.append(data[1])
                    insertDataToListbox(data[1],self.DownloadList,END)
                if self.LowQualityVar.get():
                    data_download.append(data[2])
                    insertDataToListbox(data[2],self.DownloadList,END)
            d= threading.Thread(target=self.Downloader)
            d.start()
        else:
   
            return 
        pass

    def Download_All_Cmd(self, event=None):
        global data_resault,data_download,data_playing
  
        print("Download_Selected_Cmd")
        if not ("中" in self.Download_All['text']):
            self.downloadLock()
            for num in range(0,len(data_resault)):
                data=[]
                data.append(data_resault[num].copy())
                data.append(data_resault[num].copy())
                data.append(data_resault[num].copy())
                if self.Provider.current() ==0  and self.SearchTpye.current()==0:
                    data[0]['quality']="flac"
                    data[1]['quality']="ape"
                    data[2]['quality']="320"
                    data[0]['extension']="flac"
                    data[1]['extension']="ape"
                    data[2]['extension']="mp3"
                if self.Provider.current() ==0  and self.SearchTpye.current()==3:
                    data[0]['quality']="4"
                    data[1]['quality']="3"
                    data[2]['quality']="2"
                    data[0]['extension']="mp4"
                    data[1]['extension']="mp4"
                    data[2]['extension']="mp4"
                if self.Provider.current() ==1  and self.SearchTpye.current()==0:
                    data[0]['quality']="999000"
                    data[1]['quality']="320000"
                    data[2]['quality']="128000"
                    data[0]['extension']="mp3"
                    data[1]['extension']="mp3"
                    data[2]['extension']="mp3"
                if self.Provider.current() ==1  and self.SearchTpye.current()==3:
                    data[0]['quality']="1080"
                    data[1]['quality']="720"
                    data[2]['quality']="480"
                    data[0]['extension']="mp4"
                    data[1]['extension']="mp4"
                    data[2]['extension']="mp4"
                if self.CreatSingerPathVar.get():
                    data[0]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[0]['singer'])+"/"
                    data[1]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[1]['singer'])+"/"
                    data[2]['path']=download_path+re.sub(r'[\/:*?"<>|]','-',data[2]['singer'])+"/"
                    data[0]['filename']=re.sub(r'[\/:*?"<>|]','-',data[0]['singer']+"-"+data[0]['name']+"."+data[0]['extension'])
                    data[1]['filename']=re.sub(r'[\/:*?"<>|]','-',data[1]['singer']+"-"+data[1]['name']+"."+data[1]['extension'])
                    data[2]['filename']=re.sub(r'[\/:*?"<>|]','-',data[2]['singer']+"-"+data[2]['name']+"."+data[2]['extension'])
                else:
                    data[0]['path']=download_path
                    data[1]['path']=download_path
                    data[2]['path']=download_path
                    data[0]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[0]['singer']+"-"+data[0]['name']+"."+data[0]['extension']))
                    data[1]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[1]['singer']+"-"+data[1]['name']+"."+data[1]['extension']))
                    data[2]['filename']=re.sub(r'[\/:*?"<>|]','-',(data[2]['singer']+"-"+data[2]['name']+"."+data[2]['extension']))      
                data[0]['download_pic']=self.DownloadAlbumPicVar.get()
                data[0]['download_lrc']=self.DownloadLrcVar.get()
                data[0]['creat_path']=self.CreatSingerPathVar.get()
                data[1]['download_pic']=self.DownloadAlbumPicVar.get()
                data[1]['download_lrc']=self.DownloadLrcVar.get()
                data[1]['creat_path']=self.CreatSingerPathVar.get()
                data[2]['download_pic']=self.DownloadAlbumPicVar.get()
                data[2]['download_lrc']=self.DownloadLrcVar.get()
                data[2]['creat_path']=self.CreatSingerPathVar.get()
                if self.HighQualityVar.get():
                    data_download.append(data[0].copy())
                    insertDataToListbox(data[0].copy(),self.DownloadList,END)
                if self.MidQualityVar.get():
                    data_download.append(data[1]).copy()
                    insertDataToListbox(data[1].copy(),self.DownloadList,END)
                if self.LowQualityVar.get():
                    data_download.append(data[2].copy())
                    insertDataToListbox(data[2].copy(),self.DownloadList,END)
            d= threading.Thread(target=self.Downloader)
            d.start()
        else:
   
            return 
        pass

    def Stop_Cmd(self, event=None):
        #TODO, Please finish the function here!
        if  self.Play['text']=="播放":
             
            pass
        else:
            self.Play['text']=="播放"
            try:
                if pygame.mixer.music.get_busy():
                    self.Play['text']="播放"
                    self.PlayList.delete(0,END)
                    pygame.mixer.music.stop()
            except Exception as e:
                print(e)
                print("StopERR PlayINgStop")
                self.Play['text']=="播放"

                try:                     
                    pygame.mixer.quit()
                except Exception as e2:
                    print(e2)
                pass
        pass

    def Next_Song_Cmd(self, event=None):
        #TODO, Please finish the function here!
        if(self.PlayList.size()<1 or len(self.PlayList.curselection())<1):
            self.Play['text']="播放"
            return
        if (self.PlayList.curselection()[0]+2 )>self.PlayList.size():
            self.PlayList.select_set(0)  
        else:
            self.PlayList.select_set(self.PlayList.curselection()[0]+1)
            if  self.Play['text']=="播放":
                self.Play['text']="停止"
                p = threading.Thread(target=self.Player)
                p.start()
                pass
            else:
                
                self.Play['text']=="播放"
                try:
                    if pygame.mixer.music.get_busy():
                        self.Play['text']="播放"
                    
                        pygame.mixer.music.stop()
                except Exception as e:
                    print(e)
                    print("StopERR PlayINgStop")
                    self.Play['text']=="播放"

                    try:                     
                        pygame.mixer.quit()
                    except Exception as e2:
                        print(e2)
                     
             
         

         
 
    def Pre_Song_Cmd(self, event=None):
        #TODO, Please finish the function here!
        if(self.PlayList.size()<1 or len(self.PlayList.curselection())<1):
            self.Play['text']="播放"
            return
        if (self.PlayList.curselection()[0]-1 )<0:
            self.PlayList.select_set(0)  
        else:
            self.PlayList.select_set(self.PlayList.curselection()[0]-1)
            if  self.Play['text']=="播放":
                self.Play['text']="停止"
                p = threading.Thread(target=self.Player)
                p.start()
                pass
            else:
                
                self.Play['text']=="播放"
                try:
                    if pygame.mixer.music.get_busy():
                        self.Play['text']="播放"
                    
                        pygame.mixer.music.stop()
                except Exception as e:
                    print(e)
                    print("StopERR PlayINgStop")
                    self.Play['text']=="播放"

                    try:                     
                        pygame.mixer.quit()
                    except Exception as e2:
                        print(e2)

    def Pause_Cmd(self, event=None):
        #TODO, Please finish the function here!
        self.Play_Cmd()
        pass

    def Play_Cmd(self, event=None):
        #TODO, Please finish the function here!
        if  self.Play['text']=="播放":
            self.Play['text']="停止"
            p = threading.Thread(target=self.Player)
            p.start()
            pass
        else:
            
            self.Play['text']=="播放"
            try:
                if pygame.mixer.music.get_busy():
                    self.Play['text']="播放"
                   
                    pygame.mixer.music.stop()
            except Exception as e:
                print(e)
                print("StopERR PlayINgStop")
                self.Play['text']=="播放"

                try:                     
                    pygame.mixer.quit()
                except Exception as e2:
                    print(e2)
                pass
        pass



    def Open_Path_Cmd(self, event=None):
        #TODO, Please finish the function here!
        os.startfile(os.path.abspath(download_path))
        pass

def insertDataToListbox(data,box,position):
    
    datastr = ""
    if "singer" in data:
        datastr = datastr+str(word_align(data['singer'], 30, 'L'))
    if "name" in data:
        datastr = datastr+str(word_align(data['name'], 30, 'L'))
    if "title" in data:
        datastr = datastr+str(word_align(data['title'], 30, 'L'))
    if "artist" in data:
        datastr = datastr+str(word_align(data['artist']['name'], 30, 'L'))
    if "creator" in data:
        datastr = datastr+str(word_align(data['creator']['nickname'], 30, 'L'))
    if "creator" in data and "userName" in data[0]:
        datastr = datastr + \
            str(word_align(data['creator'][0]['userName'], 30, 'L'))
    if "dj" in data:
        datastr = datastr+str(word_align(data['dj']['nickname'], 30, 'L'))
    if "nickname" in data:
        datastr = datastr+str(word_align(data['nickname'], 30, 'L'))
    if "description" in data:
        datastr = datastr+str(word_align(data['description'], 30, 'L'))
    if "ar" in data:
        datastr = datastr+str(word_align(data['ar'][0]['name'], 30, 'L'))
    if "time" in data:
        datastr = datastr+str(word_align(str(data['time'])+"秒", 8, 'L'))
    if "quality" in data:
        datastr = datastr+word_align(str(data['quality']), 8, 'L')
    box.insert(position, datastr)
    

def insertDatasToListbox(datas,box,position):
    if len(datas)<1:
        return
    for data in datas:
       insertDataToListbox(data.copy(),box,position)

def word_align(_string, _length, _type='L'):
    __String=_string
    if len(_string)> _length/2 and _length>10:
        __String=_string[0:int(_length/2)-3]+"...."
    
    
    _str_len = len(str(__String))
    for _char in __String:
        if u'\u4e00' <= _char <= u'\u9fa5':
            _str_len += 1
    _space = _length-_str_len
    if _type == 'L':  
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space//2
        _right = _space-_left
    return ' '*_left + __String + ' '*_right

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
        if s=="." : continue
        return True
    return False

def downloadMusicById(path,filename,p,code,mid,bps):
    if not os.path.exists(path):
        os.mkdir(path)   
    url="https://api.itooi.cn/music/%s/url?key=%s&id=%s&br=%s"%(str(p),str(code),str(mid),str(bps))
    downloadFile(path,filename,url)
    
def downloadFile(path,filename,url):
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    if not os.path.exists(path):
        os.mkdir(path)   
    if(url == None or "http" not in url):
        print("urlerr:"+str(url))
        return 3
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests':'1'}
    if  os.path.exists(path+filename):
        print("已存在：文件大小："+str(os.path.getsize(path+filename)))
        if os.path.getsize(path+filename) < 1024000:
            print("小于1MB的重新下载中")
        else:
            return 0    
    response = requests.get(url, headers=headers)
    try:
        with open((path+filename).encode('UTF-8').decode("UTF-8"), 'wb') as f:
            f.write(response.content)
            f.flush()
            f.close()
            return 0
    except Exception as e:
        print(e)
        pass

def searchMusicList(path,p,code,lid):
    if not os.path.exists(path):
        os.mkdir(path)   
    r_file=None
    url="https://api.itooi.cn/music/%s/songList?key=%s&id=%s"%(p,code,lid)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    if data['code']==2333 or len(data['data'])<1: 
        return []
    if not os.path.exists(path+str(p)+"-list-"+str(lid) ):
        try:
            r_file = open((path+str(p)+"-list-"+str(lid) ), "w", encoding="utf-8")
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
            with open(tmp_path+str(p)+"-list-"+str(lid) , "r", encoding="utf-8") as r_file:
                data=json.load(r_file)
                print(data)
        except Exception as  e:
            print(e)
        finally:
            # print(data['data']['songs'])
            return data['data']['songs']
        return data

def searchMusicAlbum(path,p,aid,key):
    if not os.path.exists(path):
        os.mkdir(path)   
    r_file=None
    url="https://api.itooi.cn/music/%s/album?key=%s&id=%s"%(p,code,aid)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}" +":"+mainPageUrl)
    # print(f"text = {responseRes.text}")
    if data['code']==2333 or len(data['data'])<1: 
        return []
    if not os.path.exists(path+str(p)+"-album-"+str(aid)):
        try:
            r_file = open((path+str(p)+"-album-"+str(aid)), "w", encoding="utf-8")
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
            with open(tmp_path+str(p)+"-album-"+str(aid), "r", encoding="utf-8") as r_file:
                data=json.load(r_file)
                print(data)
        except Exception as  e:
            print(e)
        finally:
            # print(data['data'])
            return data['data']
        return data

def searchMusic(path,p,keyword,wtype,limit,offset):
    if not os.path.exists(path):
        os.mkdir(path)   

    #搜索音乐/专辑/歌词/歌单/MV/用户/歌手/电台搜索
    r_file=None
    url=" https://api.itooi.cn/music/%s/search?key=%s&s=%s&type=%s&limit=%s&offset=%s"%(p,code,keyword,wtype,limit,offset)
    responseRes=webSession.get(url,  headers = ajaxheaders)
    data = json.loads(responseRes.text)
    if data['code'] != 2333 and data['data']!= None and data['data']!='null':
        if not os.path.exists(path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)) :
            try:
                r_file = open((path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)), "w", encoding="utf-8")
                r_file.write(str(data))
                r_file.flush()
            except Exception as  e:
                print(e)
            finally:
                r_file.close()
        else:
            try:
                with open((path+str(p)+"-"+str(code)+"-"+str(keyword)+"-"+str(wtype)+"-"+str(limit)+"-"+str(offset)), "r", encoding="utf-8") as r_file:
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

def getSongDetialById(path,p,key,sid):
    if not os.path.exists(tmp_path+str(p)+"-song-"+str(key)+"-"+str(sid)):
        url="https://api.itooi.cn/music/%s/song?key=%s&id=%s"%(p,key,sid)
        responseRes=webSession.get(url,  headers = ajaxheaders)
        data = json.loads(responseRes.text)
        try:
            r_file = open((path+str(p)+"-song-"+str(key)+"-"+str(sid)), "w", encoding="utf-8")
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
            with open((path+str(p)+"-song-"+str(key)+"-"+str(sid)), "r", encoding="utf-8") as r_file:
                data= json.load(r_file)
            return data['data']
        except Exception as  e:
            print(e)
        finally:
            r_file.close()
            return data['data']
    return data

def getTypeByStr(data):
    if data=="音乐搜索": 
        return  "song" 
        
    if data=="歌手搜索": 
        return "singer"            
         
    if data=="专辑搜索": 
        return "album"            
         
    if data=="歌单搜索": 
        return "list"            
         
    if data=="视频搜索": 
        return "video"            
         
    if data=="电台搜索": 
        return "radio"            
         
    if data=="用户搜索": 
        return "user"
         
    if data=="歌词搜索": 
        return "lrc"
         
    return "song" 

def getProvider(box):
    if box.get()=="QQ音乐": 
        return  "tencent" 
    if box.get()=="网易云音乐": 
        return "netease"
    return "netease"

def getLrc(filename):  
    lrc_dict = {}
    try:
        file = open(filename, "r", encoding="utf-8")
        lrc_list = file.readlines()
        for i in lrc_list:
            lrc_word = i.replace("[", "]").strip().split("]")
            for j in range(len(lrc_word) - 1):
                if lrc_word[j]:
                    lrc_dict[lrc_word[j]] = lrc_word[-1]
        return lrc_dict
    except Exception as e:
            print(e)    
    finally:
        file.close()
        return lrc_dict

def getTypeByCombobox(box):
    if box.get()=="音乐搜索": 
        return  "song" 
    if box.get()=="歌手搜索": 
        return "singer"
    if box.get()=="专辑搜索": 
        return "album"
    if box.get()=="歌单搜索": 
        return "list"
    if box.get()=="视频搜索": 
        return "video"
    if box.get()=="电台搜索": 
        return "radio"
    if box.get()=="用户搜索": 
        return "user"
    if box.get()=="歌词搜索": 
        return "lrc"
    return "song" 

def getKeyWordByText(text):
    return str(text.get()).encode("utf-8").decode("utf-8")

def getDownLoadPath(checkbox,song):
    print()
    # if()

def getSongFilename(song):
    print(song)
    return re.sub(r'[\/:*?"<>|]','-',song['singer']+"-"+song['name']+".mp3")

def stopThreads():
    print("to do stopthreads")
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
    except Exception as e:
        print(e)
        
        try:                     
            pygame.mixer.quit()
        except Exception as e2:
            print(e2)

def closeWindow():
    try:
        print( 'killing...')
        time.sleep(1)
        sys.exit(0)
    except Exception as e:
        print(e)
        print( 'Going Die...')
        time.sleep(1)
        os._exit(0)
    finally:
        print( 'Finish Exit')



if __name__ == "__main__":
    top = Tk()
    top.protocol('WM_DELETE_WINDOW', closeWindow)
    Application(top).mainloop()
    try: top.destroy()
    except: pass
