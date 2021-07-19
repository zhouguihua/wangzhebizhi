#!/user/bin/env python
# -*- coding:utf-8 -*-
# 作者：周桂华
# 开发时间: 2021/7/19 14:56

from urllib.parse import unquote
import requests
import json
from multiprocessing import Process
import os
import re
import time


class DownHonorOfKingsPictures(Process):

    def __init__(self, name, page, save_path):
        super().__init__()
        self.name = name
        self.page = page
        self.save_path = save_path
        self.pic_name = None
        self.url = "https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi?" \
                   "activityId=2735&sVerifyCode=ABCD&sDataType=JSON&iListNum=20&totalpage=0&page={}&iOrder=0&iSortNumClose" \
                   "=1&jsoncallback=jQuery171008570727224179198_1626671803638&iAMSActivityId=51991&_everyRead=" \
                   "true&iTypeId=2&iFlowId=267733&iActId=2735&iModuleId=2735&_=1626671803731".format(self.page)
        self.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5"
                                      "37.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    def run(self):
        # 请求图片接口
        resp = requests.get(self.url, headers=self.headers)
        if resp.status_code == 200:
            # 提取数据
            pic_infoList = json.loads(re.match(".*?\((.*?)\)", resp.text).group(1))["List"]
            if not pic_infoList:
                print("---第 {} 页无壁纸信息".format(self.page))
            else:
                self.parse_PicList(pic_infoList)
        else:
            print("---错误信息：页数为：{}的请求返回状态码：{}".format(self.page, resp.status_code))

    def parse_PicList(self, picList):
        total = len(picList)
        print("---开始处理第 {} 页".format(self.page))
        print("---第 {} 页有 {} 张壁纸".format(self.page, total))
        count = 0
        for pic in picList:
            self.pic_name = re.sub(r'[【】:.<>|·@#$%^&() ]', "", unquote(pic["sProdName"]))
            pic_url = unquote(pic["sThumbURL"])
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            save_path = os.path.join(self.save_path, self.pic_name+".jpg")
            if os.path.exists(save_path):
                print("---{}出现重复".format(save_path))
                continue
            count += 1
            self.download_bizhi(save_path, pic_url.replace("/200", "/0"), count, total)

    def download_bizhi(self, path, url, count, total):
        resp = requests.get(url)
        fp = open(path, "wb")
        fp.write(resp.content)
        fp.close()
        print("---正在下载第 {} 页， {} 壁纸 进度{}/{}.....".format(self.page, self.pic_name, count, total))


if __name__ == '__main__':
    print("------开始下载王者荣耀壁纸------")
    start_time = time.perf_counter()
    start = 0
    end = 4
    while start < 26:
        pList = []
        for i in range(start, end):
            p = DownHonorOfKingsPictures(str(i), i, os.path.join(os.path.dirname(__file__), "hero"))
            pList.append(p)
        for p in pList:
            p.start()
        for p in pList:
            p.join()
        start += 4
        end += 4
    end_time = time.perf_counter()
    print("---执行时间为 {} 秒".format(end_time - start_time))


