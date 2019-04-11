#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
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

folder = ''
res = []
num = 0
searching=False
now_music = ''
playing=False
urls=[]
names=[]
songList = {}
webSession = requests.session()
download_path = "./download/"
tmp_path = "./tmp/"
provider = "qq"
ptname = "网易云音乐"
defaulturl = "http://music.sonimei.cn/"
if not os.path.exists(download_path):
    os.mkdir(download_path)
if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)
webSession.cookies = cookielib.LWPCookieJar(filename=tmp_path+"cookie.txt")

defaultHeader = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache"
}
ajaxheaders = {
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'dnt': "1",
    'accept-encoding': "gzip, deflate",
    'x-requested-with': "XMLHttpRequest",
    'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    'cache-control': "no-cache",
    'accept': "application/json, text/javascript, */*; q=0.01",
}
 



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

        self.ProgressBar1Var = StringVar(value='')
        self.ProgressBar1 = Progressbar(self.top, orient='horizontal', maximum=100, variable=self.ProgressBar1Var)
        self.ProgressBar1.place(relx=0.153, rely=0.955, relwidth=0.833, relheight=0.034)

        self.ProviderList = ['qq','网易云音乐','酷狗','酷我','虾米','百度',]
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
        self.ResaultBoxFont = Font(font=('宋体',9))
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

# def searchKeywords(word):
# TODO add FUnC
#     return word

def searchMusicById(mid):
    global ptname, provider, download_path,tmp_path
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    postData = {
        "input": str(mid),
        "filter": "id",
        "type": provider,
        "page": 1,
    }
    responseRes = webSession.post(
        defaulturl, data=postData, headers=ajaxheaders, verify=False)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}"+":"+defaulturl)
    if responseRes.status_code != 200:
        return []
    #print(f"text = {responseRes.text.encode('utf-8').decode('unicode_escape')}")
    try:
        r_file = open("./tmp/"+str(data['data'][0]['songid']) +
                      "-"+str(data['data'][0]['type']), "w", encoding="utf-8")
        r_file.write(str(data))
        r_file.flush()
        return data['data']
    except:
        responseRes.text
        return data['data']
    finally:
        r_file.close()
        return data['data']


def searchMusicByTitle(title, page):
    global ptname, provider, download_path,tmp_path
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    postData = {
        "input": str(title),
        "filter": "name",
        "type": provider,
        "page": page,
    }
    responseRes = webSession.post(
        defaulturl, data=postData, headers=ajaxheaders, verify=False)
    data = json.loads(responseRes.text)
    # print(f"statusCode = {responseRes.status_code}"+":"+defaulturl)
    # print(f"text = {responseRes.text.encode('utf-8').decode('unicode_escape')}")

    if responseRes.status_code != 200:
        return []
    try:
        r_file = open("./tmp/"+str(title)+"-"+str(page)+"-" +
                      str(provider), "w", encoding="utf-8")
        r_file.write(str(data))
        r_file.flush()
        return data['data']
    except:
        return data['data']
    finally:
        r_file.close()
        return data['data']

    
def downloadMusicByHttpRequest(filename,url):
    global ptname, provider, download_path,tmp_path
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
    _filename = download_path+re.sub(r'[\/:*?"<>|]','-',filename)
    if  os.path.exists(_filename):
        print("已存在：文件大小："+str(os.path.getsize(_filename)))
        if os.path.getsize(_filename)>1024000:
            return 0    
        else:
            print("小于1MB的重新下载中")
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


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。              
    def __init__(self, master=None):
        Application_ui.__init__(self, master)

    def checkProvider(self,event=None):
        global ptname, provider
        print("checkProvider")
        # self.Provider

    def Searcher(self,event=None):
        global num,res,playing,searching,urls,names
        urls=[]
        names=[]
        searching = True
        self.Search['text']='搜索中'
        while searching:
            global ptname, provider, download_path,downloadall,musics,res
            musics=[]
            res=[]
            self.ResaultBox.delete(0,END)
            word= self.Text1.get()
            print(word)
            print("当前平台："+str(ptname)+"-"+str(provider)+"关键字："+str(word))
            datas = []
            page = 1
            data = searchMusicByTitle(word, page)
            for song in data:
                if word not in song['author'] and word not in song['title']:
                    data.remove(song)
            while(len(data) > 0) and searching:
                for song in data:
                    espace = ""
                    for n in range(1, 30-len(song['author'])):
                        espace += " "
                    print(song['author']+espace+song['title'])
                    self.ResaultBox.insert(END,song['author']+espace+song['title'])
                    url=song['url']
                    if (song['url'] == None or "http" not in song['url']):
                        print("urlerr:"+str(song['url']))
                        url = 'http://music.163.com/song/media/outer/url?id=' +str(song['songid'])+ '.mp3'
                        if provider !="netease":
                            continue
                    urls.append(url)
                    names.append(str(song['author']+"-"+song['title']+".mp3"))
                    # downloadMusicByHttpRequest(str(song['author']+"-"+song['title']+".mp3"),url)
                    musics.append(download_path+str(song['author']+"-"+song['title']+".mp3"))
                    res=musics
                    print(song['url'])
                datas.extend(data)
                page += 1
                data = searchMusicByTitle(word, page)
                for song in data:
                    if word not in song['author'] and word not in song['title']:
                        data.remove(song)
                print("当前平台："+str(ptname)+"-"+str(provider) +
                    "关键字："+str(word)+"一共检测到："+str(len(datas))+"条")
                if self.ResaultBox.size() > 1:
                    for i in range(0,self.ResaultBox.size()):
                        self.ResaultBox.itemconfig(i,bg="#999999")  
                        self.ResaultBox.itemconfig(i,fg="#000000")
            searching=False
            self.Search['text']='搜索'

    def Player(self,event=None):
        global num,res,playing
        playing = True
        self.Play['text']='暂停'
        if len(res):
            pygame.mixer.init()
        while playing:
            if not pygame.mixer.music.get_busy():
                nextMusic = res[num]
                try:
                    downloadMusicByHttpRequest(names[num],urls[num])
                except :
                    print("dlerr")
                print("now:"+str(num)+"     "+str(nextMusic))
                try:
                    if self.ResaultBox.size() > 1:
                        for i in range(0,self.ResaultBox.size()):
                            self.ResaultBox.itemconfig(i,bg="#999999")  
                            self.ResaultBox.itemconfig(i,fg="#000000")
                    else:
                        self.ResaultBox.itemconfig(self.ResaultBox.size()-1,bg="#999999")
                        self.ResaultBox.itemconfig(self.ResaultBox.size()-1,fg="#000000")
                    self.ResaultBox.itemconfig(num,fg="#FFFFFF")
                    self.ResaultBox.itemconfig(num,bg="#6600FF")
                    pygame.mixer.music.load(nextMusic.encode())
                    pygame.mixer.music.play(1)
                except :
                    print("ERRR")
                if len(res)-1 == num:
                    num = 0
                else:
                    num = num + 1
                print("all:"+str(len(res)-1))
                print("next:"+str(num)+"   "+res[num])
                nextMusic = nextMusic.split('\\')[1:]
                try:
                    downloadMusicByHttpRequest(names[num],urls[num])
                except :
                    print("dlerr")
                print('playing....' + ''.join(nextMusic))
            else:
                time.sleep(0.1)
                seta=num-1
                if len(res)-1 == num:
                    seta = 0
                if seta==-1:
                    seta=0
                if seta> self.ResaultBox.size():
                    seta=0
                if num!=0:
                    self.ResaultBox.itemconfig(seta,fg="#FFFFFF")
                    self.ResaultBox.itemconfig(seta,bg="#6600FF")
                # print("Sleeeeeeeeping")
        print("Plaing:Stoped-ALL Thread Destorying")
        return 

    def NextSong_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("NextSong_Cmd")
        global playing
        playing = False
        # pygame.mixer.quit()
        global num
        if len(res) == num:
            num = 0
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
            # pygame.mixer.quit()
        except:
            pass
        if not playing:
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            playing = True
            self.Play['text']='暂停'
            t = threading.Thread(target=self.Player)
            t.start()
        return 

    def PreSong_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("PreSong_Cmd")
        global playing
        playing = False
        global num
        if num == 0:
            num = len(res)-2
        elif  num == len(res) -1:
            num -=2
        else:
            num -=2
        print("Pre"+str(num))
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
            # pygame.mixer.quit()
        except:
            pass
        if not playing:
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            playing = True
            self.Play['text']='暂停'
            t = threading.Thread(target=self.Player)
            t.start()
        return 

    def Stop_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Stop_Cmd")
        global playing
        playing = False
        self.Play['text']='播放'
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
        
        except:
            print("ERRRRRRRRR")
            pass
        return 

    def Play_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Play_Cmd")
        self.NextSong['state'] = 'normal'
        self.PreSong['state'] = 'normal'
        # 选择要播放的音乐文件夹
        global folder,res
        if self.Play['text'] == '播放':
            folder = tkFileDialog.askdirectory()
            if not folder:
                return
            self.Play['text']='暂停'
            musics = [folder + '\\' + music
                for music in os.listdir(folder) \
                        \
                if music.endswith(('.mp3', '.wav', '.ogg'))]
            res = musics
            self.Set_ResaultBox(res)
            global playing
            playing = True
            # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            self.Play['text']='暂停'
            t = threading.Thread(target=self.Player)
            t.start()
        elif self.Play['text'] == '暂停':
            #pygame.mixer.init()
            pygame.mixer.music.pause()
            self.Play['text']='继续'
        elif self.Play['text'] == '继续':
            #pygame.mixer.init()
            pygame.mixer.music.unpause()
            self.Play['text']='暂停'
            pass
        if not playing:
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            playing = True
            self.Play['text']='暂停'
            t = threading.Thread(target=self.Player)
            t.start()
        return 

    def OpenPath_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("OpenPath_Cmd")
        global folder
        global res
        global playing
        global num
        folder = tkFileDialog.askdirectory()
        playing = False
        print(folder)
        if not folder:
            return
        musics = [folder + '\\' + music
            for music in os.listdir(folder) \
                    \
            if music.endswith(('.mp3', '.wav', '.ogg'))]
        res = musics
        print(res)
        self.Set_ResaultBox(res)
        if not playing:
            self.Set_ResaultBox(res)
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            playing = True
            self.Play['text']='暂停'
            t = threading.Thread(target=self.Player)
            t.start()
        return 

    def Search_Cmd(self, event=None):
        global searching
        #TODO, Please finish the function here!
        print("Search_Cmd")
        if not searching:
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            searching = True
            self.Search['text']='搜索中'
            s = threading.Thread(target=self.Searcher)
            s.start()
        else:
            searching=False
        return 
    
    def Set_ResaultBox(self,res,event=None):
        # clear all recent values
        self.ResaultBox.delete(0,END)
        # add song name to box
        for item in res:
            self.ResaultBox.insert(END,item.split('\\')[1:])
            # if self.ResaultBox.size() > 1:
            #     self.ResaultBox.itemconfig(0,fg="#4B0082")  
            # else:
            #     self.ResaultBox.itemconfig(self.ResaultBox.size()-1,bg="#EDEDED")
        return 
 
    def ResaultBoxDoubleClick(self, event):
        #获取所点击的文件的名称
        
        print(self.ResaultBox.curselection()[0] ) 
        filename =  self.ResaultBox.get(self.ResaultBox.curselection())
        print(filename)
        global playing
        # playing = False
        global num,res,names,urls
        if len(res) == num:
            num = 0
        else:
            num=int(self.ResaultBox.curselection()[0])
            print("NUM:self.ResaultBox.curselection()++++ "+str(num))
            try:
                downloadMusicByHttpRequest(names[num],urls[num])
            except :
                print("dlerr")            
            if num>len(res)-1:
                print("err num > max")
                num=0
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
            # pygame.mixer.quit()
        except:
            print("ERRRRRRRRR")
            pass
        if not playing:
            # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
            print("创建一个线程来播放音乐，当前主线程用来接收用户操作")
            playing = True
            t = threading.Thread(target=self.Player)
            t.start()
            pass
        return 

    def Download_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Download_Cmd")
        global urls,names
        self.Download['text']='下载中'
        for i in range(0,len(urls)):
            downloadMusicByHttpRequest(names[i],urls[i])
            pass
        pass
    
def closeWindow():
    # 修改变量，结束线程中的循环
    global playing
    playing = False
    time.sleep(0.3)
    try:
        # 停止播放，如果已停止，
        # 再次停止时会抛出异常，所以放在异常处理结构中
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass
    try:
        sys.exit(0)
    except:
        print( 'die')
        os._exit(0)
    finally:
        print( 'cleanup')
    
  


if __name__ == "__main__":
    top = Tk()
    top.protocol('WM_DELETE_WINDOW', closeWindow)
    Application(top).mainloop()
    try: top.destroy()
    except: 
        print("MAIN ERR")
        pass
