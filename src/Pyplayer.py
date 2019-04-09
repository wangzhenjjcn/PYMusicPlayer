#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys,time,pygame,threading,re,datetime,json
try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
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
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    import tkinter.simpledialog as tkSimpleDialog    #askstring()
    import tkinter

folder = ''
res = []
num = 0
now_music = ''





class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Myazure音乐播放器DesignedByWangZhen<wangzhenjjcn@gmail.com>')
        self.master.geometry('837x494')
        self.master.resizable(0,0)
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

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
        self.Text1.place(relx=0., rely=0., relwidth=0.909, relheight=0.051)

        self.style.configure('Search.TButton',font=('宋体',9))
        self.Search = Button(self.top, text='搜索', command=self.Search_Cmd, style='Search.TButton')
        self.Search.place(relx=0.908, rely=0., relwidth=0.102, relheight=0.054)

        self.ResaultBoxVar = StringVar(value='ResaultBox')
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



def searchKeywords(word):
    
    return word

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
                
    def __init__(self, master=None):
        Application_ui.__init__(self, master)

    def Player(self,event=None):
        global num,res,playing
        playing = True
        self.Play['text']='暂停'
        if len(res):
            pygame.mixer.init()
        while playing:
            if not pygame.mixer.music.get_busy():
                nextMusic = res[num]
                print("now:"+str(num)+"     "+str(nextMusic))
                try:
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
                print('playing....' + ''.join(nextMusic))
            else:
                time.sleep(0.1)
                # print("Sleeeeeeeeping")

    def NextSong_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("NextSong_Cmd")
        global playing
        playing = False
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
            # pygame.mixer.quit()
        except:
            pass
        # pygame.mixer.quit()
        global num
        if len(res) == num:
            num = 0
        playing = True
        self.Play['text']='暂停'
        t = threading.Thread(target=self.Player)
        t.start()
        pass

    def PreSong_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("PreSong_Cmd")
        global playing
        playing = False
        try:
            # 停止播放，如果已停止，
            # 再次停止时会抛出异常，所以放在异常处理结构中
            pygame.mixer.music.stop()
            # pygame.mixer.quit()
        except:
            pass
        global num
        if num == 0:
            num = len(res)-2
        elif  num == len(res) -1:
            num -=2
        else:
            num -=2
        print("Pre"+str(num))
        playing = True
        self.Play['text']='暂停'
        # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        t = threading.Thread(target=self.Player)
        t.start()
        pass

    def Stop_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Stop_Cmd")
        pass

    def Play_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Play_Cmd")
        self.NextSong['state'] = 'normal'
        self.PreSong['state'] = 'normal'
        # 选择要播放的音乐文件夹
        if self.Play['text'] == '播放':
            self.Play['text']='暂停'
            global folder,res
            if not folder:
                folder = tkFileDialog.askdirectory()
                musics = [folder + '\\' + music
                    for music in os.listdir(folder) \
                            \
                    if music.endswith(('.mp3', '.wav', '.ogg'))]
                res = musics
                self.Set_ResaultBox(res)
            if not folder:
                return
            global playing
            playing = True
            # 创建一个线程来播放音乐，当前主线程用来接收用户操作
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

    def OpenPath_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("OpenPath_Cmd")
        global folder
        global res
        global playing
        global num
        playing = False
        print(folder)
        folder = tkFileDialog.askdirectory()
        if not folder:
            return
        musics = [folder + '\\' + music
            for music in os.listdir(folder) \
                    \
            if music.endswith(('.mp3', '.wav', '.ogg'))]
        res = musics
        self.Set_ResaultBox(res)
        t = threading.Thread(target=self.Player)
        t.start()

    def Search_Cmd(self, event=None):
        #TODO, Please finish the function here!
        print("Search_Cmd")
        pass

    
    def Set_ResaultBox(self,res,event=None):
        # clear all recent values
        self.ResaultBox.delete(0,END)
        # add song name to box
        for item in res:
            self.ResaultBox.insert(END,item)
            if self.ResaultBox.size() > 1:
                self.ResaultBox.itemconfig(0,fg="#4B0082")  
            else:
                self.ResaultBox.itemconfig(self.ResaultBox.size()-1,bg="#EDEDED")
 
    def ResaultBoxDoubleClick(self, event):
        #获取所点击的文件的名称
        print(self.ResaultBox.curselection()[0] ) 
        filename =  self.ResaultBox.get(self.ResaultBox.curselection())
        print(filename)
        global playing
        # playing = False
        global num,res
        if len(res) == num:
            num = 0
        else:
            num=int(self.ResaultBox.curselection()[0])
            print("NUM:self.ResaultBox.curselection()++++ "+str(num))
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
        # playing = True
        # # 创建一个线程来播放音乐，当前主线程用来接收用户操作
        # t = threading.Thread(target=self.Player)
        # t.start()

if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()
    try: top.destroy()
    except: pass
