#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author WangZhen <wangzhenjjcn@gmail.com> MIT Licenses
import sys
import time
import datetime
import os
import requests
import json
import re

try:
    import cookielib
    print(f"python2.")
except:
    import http.cookiejar as cookielib
    print(f"python3.")

downloadall="init"
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
    global ptname, provider, download_path,downloadall
    print("当前平台："+str(ptname)+"-"+str(provider)+"关键字："+str(word))
    datas = []
    page = 1
    data = searchMusicByTitle(word, page)
    downloadall="init"
    while(len(data) > 0):
        for song in data:
            espace = ""
            for n in range(1, 60-len(song['author'])):
                espace += " "
            print(song['author']+espace+song['title'])
        datas.extend(data)
        print("added:"+str(len(data))+"  NowPages:"+str(page)+"  AllDatas:"+str(len(datas)))        
        if downloadall=="all" and downloadall!="init":
            page += 1
            data = searchMusicByTitle(word, page)
        else:
            print("继续搜索请按回车,任意字符回车取消继续检索，不再提示请输入all")
            key = input()
            if len(key)>0 :
                if(key=="all"):
                    downloadall="all"
                    page += 1
                    data = searchMusicByTitle(word, page)    
                else:
                    data=[]
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



def downloadMusicByHttpRequest(filename,url):
    global ptname, provider, download_path
    if not os.path.exists(download_path):
        os.mkdir(download_path)
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
        

def downloadMusicByPowerShell(filename, url):
    global ptname, provider, download_path
    if(url == None or "http" not in url):
        print("urlerr:"+url)
        return 3
    _filename = download_path+re.sub(r'[\/:*?"<>|]','-',filename)
    # _filename = filename.replace(u'\xa0', u' ').replace(",", "+").replace("'", "").replace("’", "").replace("!", "+").replace("@", "+").replace("#", "+").replace("$", "+").replace("%", "+").replace("^", "+").replace(
    #     "&", "+").replace("*", "+").replace(":", "").replace("：", "").replace(" ", " ").replace('\n', '').replace(' ', '').replace(':', '-').replace('：', '-').replace('>', '）').replace('<', '（').replace('(', '`(').replace(')', '`)')
    if  os.path.exists(_filename):
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
        espace=""
        for n in range(1, 70-len(filename)):
                espace += " "
        if str(status)=="3":
            print("下载:   "+filename+espace+ str(status).replace("0","下载已完成").replace("1","下载错误").replace("3","地址错误"))
            print(url)
            print()
            if song['type']=="netease":
                print("尝试下载128Kbps版本")
                print()
                url = 'http://music.163.com/song/media/outer/url?id=' +str(song['songid'])+ '.mp3'
                status =downloadMusicByHttpRequest(filename,url)
        print("下载:"+espace+filename+espace+ str(status).replace("0","下载已完成").replace("1","下载错误").replace("3","地址错误"))
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


def fucMain():
    global ptname, provider, download_path
    print("选择你要的功能，输入数字回车即可，例如：1")
    print()
    print("1.通过关键字检索歌曲")
    print("2.修改下载平台，支持的平台有默认网易、QQ、酷狗、酷我、虾米、百度、一听、咪咕、荔枝、蜻蜓、喜马拉雅、全民K歌、5sing原创、5sing翻唱等")
    print("3.通过用户分享的播放列表下载歌曲（例如【https://music.163.com/#/playlist?id=140988826&userid=114431055】）")
    print("4.通过音乐ID下载歌曲  （例如http://music.163.com/#/song?id=185721中的【185721】）")
    print("5.全平台关键字下载")
    print()
    print()
    fid = input()
    if fid == "1":
        print("当前下载平台是【"+str(ptname)+"】")
        print("输入你需要检索的歌曲关键字然后回车：")
        print()
        key = input()
        print("正在查询关键字【"+str(key)+"】相关的歌曲，请稍候")
        data = searchMusicListByKeyWord(key)
        for song in data:
            print(str(song['songid'])+" : "+str(song['title']) +
                  "         "+str(song['author']))
        pass
        print("是否全部下载，如果要全部下载请输入yes回车，如果不是全部下载，请输入要下载的歌曲id回车，返回请直接按回车")
        print()
        cid = input()
        if cid == "yes":
            downloadMusicList(data)
        elif len(cid) > 2:
            print("当前下载平台是【"+str(ptname)+"】")
            print("正在下载ID为【"+str(cid)+"】的歌曲，请稍候")
            downloadMusicById(cid)
        else:
            pass

    if fid == "2":
        print("当前下载平台是【"+str(ptname)+"】")
        print("输入你需要切换的平台对应的ID然后回车：")
        print("【默认：1网易】、2QQ、3酷狗、4酷我、5虾米、6百度、7一听、8咪咕、9荔枝、10蜻蜓、11喜马拉雅、12全民K歌、13-5sing原创、14-5sing翻唱等")
        print()
        key = input()
        if key == "1":
            ptname = "网易云音乐"
            provider = "netease"
            print("已经切换到"+str(ptname)+"下载")
        if key == "2":
            ptname = "QQ音乐"
            provider = "qq"
            print("已经切换到"+str(ptname)+"下载")
        if key == "3":
            ptname = "酷狗音乐"
            provider = "kugou"
            print("已经切换到"+str(ptname)+"下载")
        if key == "4":
            ptname = "酷我音乐"
            provider = "kuwo"
            print("已经切换到"+str(ptname)+"下载")
        if key == "5":
            ptname = "虾米音乐"
            provider = "xiami"
            print("已经切换到"+str(ptname)+"下载")
        if key == "6":
            ptname = "百度云音乐"
            provider = "baidu"
            print("已经切换到"+str(ptname)+"下载")
        if key == "7":
            ptname = "一听云音乐"
            provider = "1ting"
            print("已经切换到"+str(ptname)+"下载")
        if key == "8":
            ptname = "咪咕音乐"
            provider = "migu"
            print("已经切换到"+str(ptname)+"下载")
        if key == "9":
            ptname = "荔枝音乐"
            provider = "lizhi"
            print("已经切换到"+str(ptname)+"下载")
        if key == "10":
            ptname = "蜻蜓音乐"
            provider = "qingting"
            print("已经切换到"+str(ptname)+"下载")
        if key == "11":
            ptname = "喜马拉雅"
            provider = "ximalaya"
            print("已经切换到"+str(ptname)+"下载")
        if key == "12":
            ptname = "全民K歌"
            provider = "kg"
            print("已经切换到"+str(ptname)+"下载")
        if key == "13":
            ptname = "5sing原创"
            provider = "5singyc"
            print("已经切换到"+str(ptname)+"下载")
        if key == "14":
            ptname = "5sing翻唱"
            provider = "5singfc"
            print("已经切换到"+str(ptname)+"下载")
    if fid == "3":
        print("当前下载平台是【"+str(ptname)+"】")
        print("输入你需要下载的歌曲列表链接然后回车：")
        print("比如：https://music.163.com/playlist?id=140988826&userid=114431055")
        print()
        key = input()
        print("正在下载【"+str(key)+"】列表的歌曲，请稍候")
        download163SharePlayList(key)
    if fid == "4":
        print("当前下载平台是【"+str(ptname)+"】")
        print("输入你需要下载的歌曲ID然后回车：")
        print("比如：316686 ")
        print()
        key = input()
        print("正在下载ID为【"+str(key)+"】的歌曲，请稍候")
        downloadMusicById(key)
    if fid == "5":
        print("输入你需要检索的歌曲关键字然后回车：")
        print()
        key = input()
        print("输入你需要检索的歌曲的歌手名字然后回车（不限的话留空）：")
        print()
        singer = input()
        print()
        print("正在查询关键字【"+str(key)+"】相关的歌曲，请稍候")
        data = []
        ptname = "网易云音乐"
        provider = "netease"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "QQ音乐"
        provider = "qq"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "酷狗音乐"
        provider = "kugou"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "酷我音乐"
        provider = "kuwo"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "虾米音乐"
        provider = "xiami"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "百度云音乐"
        provider = "baidu"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "一听云音乐"
        provider = "1ting"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "咪咕音乐"
        provider = "migu"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "荔枝音乐"
        provider = "lizhi"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "蜻蜓音乐"
        provider = "qingting"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "喜马拉雅"
        provider = "ximalaya"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "全民K歌"
        provider = "kg"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "5sing原创"
        provider = "5singyc"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        ptname = "5sing翻唱"
        provider = "5singfc"
        print("已经切换到"+str(ptname)+"下载")
        data.extend(searchMusicListByKeyWord(key))
        datatodownload = []
        for song in data:
            author = str(song['author']).replace(" ", "").replace("\n", "")
            if (len(singer) > 1 and (singer not in author)):
                continue
            print(str(song['songid'])+" : "+str(song['title']) +
                  "         "+str(song['author']))
            datatodownload.append(song)
        downloadMusicList(datatodownload)


if __name__ == "__main__":
    # webSession.cookies.load()
    # print(webSession.cookies)
    while True:
        fucMain()
