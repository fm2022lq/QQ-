# -*- coding: utf-8 -*-
# @Samp: pip install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple
# @Time: 2025/4/15 20:32
# @Author: jef.ld
# @Project: qq_space
# @File: download_coroutine
import time
import os
import aiohttp
import asyncio
import aiofiles
import functools
from utils.utils import QQSpace
from aiohttp import ClientError, ConnectionTimeoutError, ClientConnectorError
from asyncio.exceptions import TimeoutError
from yarl import URL


def excute_time(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time() - start_time
        print("【{}】 总计耗时:{:.2f} s".format(func.__name__, end_time))

    return wrap


class Down(QQSpace):
    def __init__(self):
        self.qqconfig = self.read_config(filepath=("config",), filename="config.ini", encoding="utf-8")
        self.rep_count = self.qqconfig.getint("qq_space", "rep_count")
        self.timeout = self.qqconfig.getint("qq_space", "timeout")

        self.api_info = self.read_yaml(filepath=("config",), filename="api_info.yaml")

    async def client(self, data_list):
        headers = self.api_info["Common"]["headers"]

        semaphore = asyncio.Semaphore(10)  # 设置信号量
        async with aiohttp.ClientSession(headers=headers) as session:
            vd_total = len(data_list)
            suc_num = 1
            print("[*] 待下载任务:[{}]".format(vd_total))
            tasks = [asyncio.create_task(self.down(semaphore, session, **dt)) for dt in data_list]
            for task in asyncio.as_completed(tasks):
                ret = await task
                print("[*] 已完成: [{}/{}] 下载路径:{}".format(suc_num, vd_total, ret))
                suc_num += 1

    async def down(self, semaphore, session, **dt):
        await asyncio.sleep(0.5)
        async with semaphore:
            print("开始下载:[{}]".format(dt["truncate_name"]))
            for rep in range(1, self.rep_count + 1):
                try:
                    async with session.request(method="GET", url=URL(dt["url"], encoded=True),
                                               timeout=self.timeout) as resp:
                        if resp.status == 200:
                            async with aiofiles.open(dt["filepath"], mode="wb") as f:
                                async for b in resp.content.iter_chunked(1024 * 1024):
                                    if b:
                                        await f.write(b)
                            if os.path.isfile(dt["filepath"]) and os.path.getsize(dt["filepath"]) > 0:
                                return dt["filepath"]
                            else:
                                return "[{}] 下载失败~".format(dt["truncate_name"])
                        else:
                            print("[{}] 请求失败:".format(dt["truncate_name"], resp.status))
                            print("重试中...{}/{}".format(rep, self.rep_count))
                except (ClientError, ConnectionTimeoutError, ClientConnectorError) as e:
                    print("[{}] 下载文件时出错\n:{}".format(dt["truncate_name"], e))
                    print("等待 2 秒后重试...{}/{}".format(rep, self.rep_count))
                    await asyncio.sleep(2)  # 延迟后重试
                except TimeoutError as e:
                    print("[{}] 下载文件时超时\n:{}".format(dt["truncate_name"], repr(e)))
                    print("等待 2 秒后重试...{}/{}".format(rep, self.rep_count))
                    await asyncio.sleep(2)  # 延迟后重试
                except Exception as e:
                    print("[{}] 其它异常\n:{}".format(dt["truncate_name"], e))
                    return "[{}] 下载异常~".format(dt["truncate_name"])
            else:
                return "[{}] 下载失败~".format(dt["truncate_name"])

    def data_parser(self):
        filepath = self.qqconfig.get("download_info", "download_path")  # 保存作品的路径
        read_filepath = self.qqconfig.get("download_info", "read_file_path")  # 读取文件数据的路径
        filename = self.qqconfig.get("download_info", "read_file_name")  # 待读取excel的文件名
        sheet_name = self.qqconfig.get("download_info", "read_sheet_name")  # 待读取excel文件的工作表
        data = self.read_excel(filepath=(read_filepath,), filename=filename, sheet_name=sheet_name)

        authorname = sheet_name  # 获取QQ号

        # 创建目录
        date = time.localtime()
        videos = self.get_current_path(
            filepath=(filepath, "%s年_异步下载" % (date.tm_year,), "%s月%s日" % (date.tm_mon, date.tm_mday), authorname,
                      "videos"))
        self.folders_create(filepath=(videos,))
        images = self.get_current_path(
            filepath=(filepath, "%s年_异步下载" % (date.tm_year,), "%s月%s日" % (date.tm_mon, date.tm_mday), authorname,
                      "images"))
        self.folders_create(filepath=(images,))

        all_opus = []  # 所有作品
        for n, vd in enumerate(data["data_list"]):
            aname = self.teshu(vd["aname"] or authorname)
            pname = self.teshu(vd["pname"] or authorname)
            is_video = vd["is_video"]
            pic_format = vd["pic_format"]
            size1 = vd.get("size1")
            pic_url = vd["pic_url"]
            if is_video == "False":
                """图片处理"""
                self.folders_create(filepath=(images, aname))  # 存储图片的文件夹
                fname = "%s_%04d.%s" % (pname, n + 1, pic_format or "png")
                img_file = self.get_current_path(filepath=(images, aname), filename=fname)
                if not os.path.isfile(img_file):
                    all_opus.append(
                        {"url": pic_url, "filepath": img_file, "type": "image", "size1": size1,
                         "video_name": "{}".format(fname),
                         "truncate_name": "{}".format(self.truncate_string(fname, 30))})
            elif is_video == "True":
                """视频处理"""
                self.folders_create(filepath=(videos, aname))  # 存储视频的文件夹
                fname = "%s_%04d.%s" % (pname, n + 1, pic_format or "mp4")
                video_file = self.get_current_path(filepath=(videos, aname), filename=fname)
                if not os.path.isfile(video_file):
                    all_opus.append(
                        {"url": pic_url, "filepath": video_file, "type": "video",
                         "size1": size1, "video_name": fname,
                         "truncate_name": self.truncate_string(fname, 30)})
            else:
                print("类型错误")
                return

        return all_opus

    @excute_time
    def main(self):
        data = self.data_parser()
        if not data:
            return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.client(data))
        self.down_check(data)


if __name__ == '__main__':
    down = Down()
    down.main()
