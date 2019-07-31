# -*- coding:utf-8 -*-

import re
import os
import sys
import time

import requests

from urllib.parse import unquote,quote
from concurrent.futures import ThreadPoolExecutor

HEAD = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zh;q=0.9",
	"AlexaToolbar-ALX_NS_PH": "AlexaToolbar/alx-4.0.3",
	"Cache-Control": "max-age=0",
	"Connection": "keep-alive",
	"Cookie": "_uuid=37D43DC7-D2FE-8AF5-7D9A-9BA45E3C551665947infoc; buvid3=BE7E47DB-CC20-4EE8-B097-07F4B085E5B7190967infoc; LIVE_BUVID=AUTO1415645720387067; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1",
	"Host": "search.bilibili.com",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

NOT_FOUND = "肥肠抱歉，没有找到你要的内容 T_T"

ERROR = "出错啦"

word = ""

def getEndPage():
	"""
	获取最后一页页数
	"""
	global word
	url = "https://search.bilibili.com/all?keyword="+quote(word)
	req = requests.get(url, headers=HEAD)

	if NOT_FOUND in req.text:
		print(NOT_FOUND)
		return NOT_FOUND
	if ERROR in req.text:
		print(ERROR)
		return ERROR

	endPage = re.findall("class=\"pagination-btn\">(\d+)<", req.text)[0]
	return endPage

def spider(page):
	"""
	爬虫主程序
	"""

	global word
	url = "https://search.bilibili.com/all?keyword="+quote(word)+"&page="+str(page)
	req = requests.get(url, headers=HEAD)
	print("Spider page is", page)
	regex_data = re.findall("__INITIAL_STATE__=(.*?);\(function\(\)", req.text)[0].replace("false", "False").replace("true", "True").replace("null", "None")
	json_data = eval(regex_data) # 将字符串转为data
	data_generator = parserData(json_data)
	for dict_data in data_generator:
		str_data = ""
		for k,v in dict_data.items():
			print(k, v)
			str_data += str(k)+" "+str(v)+"\n"
		print("="*50)
		download("./", word+".txt", str_data+("="*50)+"\n", "a+")



def download(path, filename, data, opentype):
	"""
	下载数据
	"""
	file = path+os.sep+filename
	if not os.path.exists(file):
		f = open(file, "w")
		f.close()
	with open(file, opentype) as f:
		f.write(data)

def parserData(json_data):
	"""
	解析数据
	"""
	videos_data = json_data["allData"]["video"]

	for video in videos_data:
		avid = video["id"]
		title = video["title"].replace("<em class=\"keyword\">", "").replace("</em>", "")
		author = video["author"]
		m,s = video["duration"].split(":")
		if int(m) >= 60: # 时长计算
			h = str(int(m)//60)
			m,s = ("%.2f"%(float(m+"."+s)%3600%60)).split(".")
			duration = "{}:{}:{}".format(h.zfill(2), m.zfill(2), s.zfill(2))
		else:
			duration = "{}:{}".format(m.zfill(2), s.zfill(2))
		mid = video["mid"]
		play = video["play"]
		description = video["description"]
		tag = video["tag"]
		video_review = video["video_review"]
		favorites = video["favorites"]
		typename = video["typename"]
		pubdate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(video["pubdate"]))

		yield {
			"[AV号]": avid,
			"[视频标题]": title,
			"[作者昵称]": author,
			"[时长]": duration,
			"[作者ID]": mid,
			"[播放]": play,
			"[视频简介]": description,
			"[标签]": tag,
			"[弹幕]": video_review,
			"[收藏]": favorites,
			"[类型]": typename,
			"[上传时间]": pubdate,
		}

def main():
	global word
	if len(sys.argv) >= 2:
		word = sys.argv[1]
	else:
		word = input("Please input search content: ")
	
	if not word:
		print("Search content is empty.")
		return

	allPage = getEndPage()
	if allPage == NOT_FOUND or allPage == ERROR:
		return
	else:
		allPage = int(allPage)
		print("共{}页.".format(allPage))
		while 1:
			print("[Default: Spider All Page.]")

			startPage = input("Please input start page[Start/input]: ")
			if not startPage.isdigit():
				if startPage != "":
					print(startPage, "Not is a number.")
					continue
				else:
					startPage = 1
			else:
				startPage = int(startPage)

			endPage = input("Please input start page[End/input]: ")
			if not endPage.isdigit():
				if endPage != "":
					print(endPage, "Not is a number.")
					continue
				else:
					endPage = allPage
			else:
				endPage = int(endPage)

			if startPage < 1 or endPage > allPage:
				print("开始页小于１或结束页大于总页数.")
				continue

			break

	with ThreadPoolExecutor(10) as p:
		[p.submit(spider, i) for i in range(startPage, endPage+1)]
	# [spider(i) for i in range(startPage, endPage+1)]

if __name__ == '__main__':
	main()