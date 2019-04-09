#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author WangZhen <wangzhenjjcn@gmail.com> MIT Licenses
import datetime
import json
import os
import re
import sys
import threading
import time
import tkinter
import tkinter.filedialog

import pygame
import requests

try:
    import cookielib
    print(f"python2.")
except:
    import http.cookiejar as cookielib
    print(f"python3.")

downloadall = "init"
songList = {}
webSession = requests.session()
webSession.cookies = cookielib.LWPCookieJar(filename="cookie.txt")
download_path = "./download/"
provider = "netease"
ptname = "网易云音乐"
defaulturl = "http://music.sonimei.cn/"

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


def searchMusicById(mid):
    global ptname, provider, download_path
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
    global ptname, provider, download_path
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


def searchMusicListByKeyWord(word):
    global ptname, provider, download_path, downloadall
    print("当前平台："+str(ptname)+"-"+str(provider)+"关键字："+str(word))
    datas = []
    page = 1
    data = searchMusicByTitle(word, page)
    downloadall = "init"
    while(len(data) > 0):
        for song in data:
            espace = ""
            for n in range(1, 60-len(song['author'])):
                espace += " "
            print(song['author']+espace+song['title'])
        datas.extend(data)
        print("added:"+str(len(data))+"  NowPages:" +
              str(page)+"  AllDatas:"+str(len(datas)))
        if downloadall == "all" and downloadall != "init":
            page += 1
            data = searchMusicByTitle(word, page)
        else:
            print("继续搜索请按回车,任意字符回车取消继续检索，不再提示请输入all")
            key = input()
            if len(key) > 0:
                if(key == "all"):
                    downloadall = "all"
                    page += 1
                    data = searchMusicByTitle(word, page)
                else:
                    data = []
            else:
                page += 1
                data = searchMusicByTitle(word, page)
        for song in data:
            if word not in song['author'] and word not in song['title']:
                data.remove(song)
    print("当前平台："+str(ptname)+"-"+str(provider) +
          "关键字："+str(word)+"一共检测到："+str(len(datas))+"条")
    for song in datas:
        if word not in song['author'] and word not in song['title']:
            datas.remove(song)
    return datas


def downloadMusicByHttpRequest(filename, url):
    global ptname, provider, download_path
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    if(url == None or "http" not in url):
        print("urlerr:"+str(url))
        return 3
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Upgrade-Insecure-Requests': '1'}
    _filename = download_path+re.sub(r'[\/:*?"<>|]', '-', filename)
    if os.path.exists(_filename):
        print("已存在：文件大小："+str(os.path.getsize(_filename)))
        if os.path.getsize(_filename) > 1024000:
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


def downloadMusicByPowerShell(filename, url):
    global ptname, provider, download_path
    if(url == None or "http" not in url):
        print("urlerr:"+url)
        return 3
    _filename = download_path+re.sub(r'[\/:*?"<>|]', '-', filename)
    # _filename = filename.replace(u'\xa0', u' ').replace(",", "+").replace("'", "").replace("’", "").replace("!", "+").replace("@", "+").replace("#", "+").replace("$", "+").replace("%", "+").replace("^", "+").replace(
    #     "&", "+").replace("*", "+").replace(":", "").replace("：", "").replace(" ", " ").replace('\n', '').replace(' ', '').replace(':', '-').replace('：', '-').replace('>', '）').replace('<', '（').replace('(', '`(').replace(')', '`)')
    if os.path.exists(_filename):
        return 0
    try:
        c = "powershell -Command \"Invoke-WebRequest %s -OutFile %s\"" % (
            url, _filename.encode('UTF-8').decode("UTF-8"))
        if(url == None):
            return
        print(c)
        return os.system(c)
    except Exception as e:
        print(e)
        return e


def downloadMusicList(data):
    global ptname, provider, download_path
    if len(data) < 1:
        return "None"
    for song in data:
        filename = song['author']+"-"+song['title']+".mp3"
        url = song['url']
        # status = downloadMusicByPowerShell(filename, url)
        status = downloadMusicByHttpRequest(filename, url)
        espace = ""
        for n in range(1, 70-len(filename)):
            espace += " "
        if str(status) == "3":
            print("下载:   "+filename+espace + str(status).replace("0",
                                                                 "下载已完成").replace("1", "下载错误").replace("3", "地址错误"))
            print(url)
            print()
            if song['type'] == "netease":
                print("尝试下载128Kbps版本")
                print()
                url = 'http://music.163.com/song/media/outer/url?id=' + \
                    str(song['songid']) + '.mp3'
                status = downloadMusicByHttpRequest(filename, url)
        print("下载:"+espace+filename+espace + str(status).replace("0",
                                                                 "下载已完成").replace("1", "下载错误").replace("3", "地址错误"))
    return "Done"


def downloadAllSongByKeyWord(keyword):
    downloadMusicList(searchMusicListByKeyWord(keyword))


def downloadMusicById(mid):
    data = searchMusicById(str(mid))
    downloadMusicList(data)
    return "Done"


def getPlay163ShareSongList(url):
    print("open:"+url)
    mList = []
    try:
        responseRes = webSession.get(url,  headers=defaultHeader)
        webSession.cookies.save()
        data = responseRes.text
        datas = data.split("<li><a href=\"/song?id=")
        print("一共查询到"+str(len(datas))+"个歌曲")
        for i in range(1, len(datas)):
            value = datas[i].split("\"")[0]
            mList.append(value)
    except Exception as e:
        print(e)
    finally:
        return mList


def download163SharePlayList(url):
    plist = getPlay163ShareSongList(url)
    for songId in plist:
        downloadMusicById(songId)



















































root = tkinter.Tk()
root.title('WangZhenPlayer V0.0.0.0.0.0')
#窗口大小及位置
root.geometry('800x600+500+100')
root.resizable(True, True)
folder = ''
res = []
num = 0
now_music = ''
#添加文件函数
def buttonChooseClick():
    # 选择要播放的音乐文件夹
    global folder
    global res
    if not folder:
        folder = tkinter.filedialog.askdirectory()
        musics = [folder + '\\' + music

                  for music in os.listdir(folder) \
                        \
                  if music.endswith(('.mp3', '.wav', '.ogg'))]
        #res = musics
        #print(res)
        ret = []
        for i in musics:
            ret.append(i.split('\\')[1:])
            res.append(i.replace('\\','/'))
        var2 = tkinter.StringVar()
        var2.set(ret)
        lb = tkinter.Listbox(root, listvariable=var2)
        lb.place(x=50, y=100, width=260, height=300)
    if not folder:
        return
    global playing
    playing = True
    # 根据情况禁用和启用相应的按钮
    buttonPlay['state'] = 'normal'
    buttonStop['state'] = 'normal'
    #buttonPause['state'] = 'normal'
    pause_resume.set('播放')
#播放音乐函数
def play():
    # 初始化混音器设备
    if len(res):
        pygame.mixer.init()
        global num
        while playing:
            if not pygame.mixer.music.get_busy():
                # 随机播放一首歌曲
                nextMusic = res[num]
                print(nextMusic)
                print(num)
                pygame.mixer.music.load(nextMusic.encode())
                # 播放一次
                pygame.mixer.music.play(1)
                #print(len(res)-1)
                if len(res)-1 == num:
                    num = 0
                else:
                    num = num + 1
                nextMusic = nextMusic.split('\\')[1:]
                musicName.set('playing....' + ''.join(nextMusic))
            else:
                time.sleep(0.1)
#点击播放
def buttonPlayClick():
    buttonNext['state'] = 'normal'

    buttonPrev['state'] = 'normal'
    # 选择要播放的音乐文件夹
    if pause_resume.get() == '播放':
        pause_resume.set('暂停')
        global folder

        if not folder:
            folder = tkinter.filedialog.askdirectory()

        if not folder:
            return

        global playing

        playing = True

        # 创建一个线程来播放音乐，当前主线程用来接收用户操作

        t = threading.Thread(target=play)

        t.start()

    elif pause_resume.get() == '暂停':
        #pygame.mixer.init()
        pygame.mixer.music.pause()

        pause_resume.set('继续')

    elif pause_resume.get() == '继续':
        #pygame.mixer.init()
        pygame.mixer.music.unpause()

        pause_resume.set('暂停')

#停止播放
def buttonStopClick():
    global playing

    playing = False

    pygame.mixer.music.stop()

#下一首
def buttonNextClick():
    global playing

    playing = False

    pygame.mixer.music.stop()
    #
    # pygame.mixer.quit()
    global num
    # num += 1
    # num -= 1
    if len(res) == num:
        num = 0
    # elif num < 0:
    #     num = 0
    #buttonPlayClick()
    # global playing
    #
    playing = True

    # 创建一个线程来播放音乐，当前主线程用来接收用户操作

    t = threading.Thread(target=play)

    t.start()
 #关闭窗口
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

    root.destroy()

#声音控制
def control_voice(value=0.5):
    # 设置背景音乐的音量。取值从0.0到1.0。在新的音乐加载前设置,音乐加载时生效。
    #注意; 音乐加载时生效
    pygame.mixer.music.set_volume(float(value))

#上一首
def buttonPrevClick():
    global playing

    playing = False

    pygame.mixer.music.stop()
    #
    # pygame.mixer.quit()
    global num
    # num += 1
    # num -= 1
    if num == 0:
        num = len(res)-2
        #num -= 1
    elif  num == len(res) -1:
        num -=2
    else:
        num -=2
        #num -= 1
    print(num)

    playing = True

    # 创建一个线程来播放音乐，当前主线程用来接收用户操作

    t = threading.Thread(target=play)

    t.start()

root.protocol('WM_DELETE_WINDOW', closeWindow)

buttonChoose = tkinter.Button(root,text='添加',command=buttonChooseClick)

buttonChoose.place(x=50, y=10, width=50, height=20)

#buttonChoose['state'] = 'disabled'
#播放按钮
# now_music = res
#print(res)
pause_resume = tkinter.StringVar(root, value='播放')
buttonPlay = tkinter.Button(root,textvariable=pause_resume,command=buttonPlayClick)

buttonPlay.place(x=190, y=10, width=50, height=20)
buttonPlay['state'] = 'disabled'
#停止播放
buttonStop = tkinter.Button(root,text='停止',command=buttonStopClick)

buttonStop.place(x=120, y=10, width=50, height=20)

buttonStop['state'] = 'disabled'

#下一首
buttonNext = tkinter.Button(root,text='下一首',command=buttonNextClick)

buttonNext.place(x=260, y=10, width=50, height=20)

buttonNext['state'] = 'disabled'
#上一首
buttonPrev = tkinter.Button(root,text='上一首',command=buttonPrevClick)

buttonPrev.place(x=330, y=10, width=50, height=20)

buttonPrev['state'] = 'disabled'


musicName = tkinter.StringVar(root,value='暂时没有播放音乐...')

labelName = tkinter.Label(root,textvariable=musicName)

labelName.place(x=10, y=30, width=260, height=20)


# HORIZONTAL表示为水平放置，默认为竖直,竖直为vertical
s = tkinter.Scale(root, label='音量', from_=0, to=1, orient=tkinter.HORIZONTAL,
             length=240, showvalue=0, tickinterval=2, resolution=0.1, command=control_voice)
s.place(x=400, y=10 ,width=200)
# 启动消息循环
root.mainloop() 