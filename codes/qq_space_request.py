# -*- coding: utf-8 -*-
# @Samp: pip install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple
# @Time: 2025/4/15 12:59
# @Author: jef.ld
# @Project: qq_space
# @File: qq_space_request

import requests
import random
import time
from utils.utils import QQSpace


class QQ(QQSpace):
    def __init__(self):
        self.session = requests.Session()
        # 不使用代理
        self.session.trust_env = False
        self.api_info = self.read_yaml(filepath=("config",), filename="api_info.yaml")
        self.qq_info = self.get_g_tk2()
        self.qqconfig = self.read_config(filepath=("config",), filename="config.ini", encoding="utf-8")

        self.class_list = self.api_info["Api"]["class_list"]
        self.anonymity_list = self.api_info["Api"]["anonymity_list"]

        # 相册信息
        self.album_info = {"qq": self.qq_info["qq"], "albunm_list": []}
        # 相册下载信息
        self.album_down_info = {"qq": self.qq_info["qq"], "albunm_down_list": []}
        # 图片、视频信息
        self.pic_vid_info = {"qq": self.qq_info["qq"], "pic_vid_list": []}
        # 只获取图片信息
        self.pic_info = []
        # 相册翻页，总数
        self.totals = 0

    def get_visitor_simple(self):
        """获取访客信息"""
        api = self.api_info["Api"]["get_visitor_simple"]
        url = api["url"]
        method = api["method"]
        params = api["params"]
        headers = api["headers"]
        headers["referer"] = "https://user.qzone.qq.com/{}/main".format(self.qq_info["qq"])
        headers["cookie"] = self.api_info["Common"]["headers"]["cookie"]
        params["uin"] = self.qq_info["qq"]
        params["g_tk"] = self.qq_info["tk"]

        resp = self.session.request(method, url=url, params=params, headers=headers)
        data = self.data_parse("_Callback\(", "\);", resp.text)
        count = data["data"]["count"]
        items = data["data"]["items"]

        print("访客总数:{:*^30}".format(count))
        for it in items:
            qzone_level = it["qzone_level"]
            name = it["name"]
            uin = it["uin"]
            print("访客:{} - QQ号:{} - 空间等级:{}".format(name, uin, qzone_level))

    def fcg_list_album_v3(self, page_start: int, page_num=30):
        """获取相册"""
        api = self.api_info["Api"]["fcg_list_album_v3"]
        url = api["url"]
        method = api["method"]
        params = api["params"]
        headers = api["headers"]
        headers["cookie"] = self.api_info["Common"]["headers"]["cookie"]

        params["uin"] = self.qq_info["qq"]
        params["hostUin"] = self.qq_info["qq"]
        params["g_tk"] = self.qq_info["tk"]
        params["t"] = self.get_sign()
        params["_"] = round(time.time() * 1000)
        params["pageStart"] = page_start
        params["pageNum"] = page_num  # 每页返回数量
        resp = self.session.request(method, url=url, params=params, headers=headers)
        data = self.data_parse("shine3_Callback\(", "\);", resp.text)
        if data["code"] != 0:
            print(data["message"])
            return {"totals": "", "next_page_start": "", "success": False}

        album_list_mode_sort = data["data"]["albumList"]

        next_page_start = data["data"]["nextPageStart"]
        total = data["data"]["albumsInUser"]

        if (len(album_list_mode_sort)) < page_num or (next_page_start == total):
            next_page_start = None
        else:
            next_page_start = next_page_start

        for n, album in enumerate(album_list_mode_sort):
            allow_access = album["allowAccess"]
            anonymity = album["anonymity"]
            anonymity_name = self.anonymity_list.get(anonymity) or "未知"
            classid = album["classid"]
            classname = self.class_list.get(classid) or "其它"
            createtime = self.format_time(album["createtime"])
            desc = album["desc"]
            pid = album["id"]
            lastuploadtime = self.format_time(album["lastuploadtime"])
            modifytime = self.format_time(album["modifytime"])
            name = album["name"]
            order = album["order"]
            pre = album["pre"]
            total = album["total"]
            viewtype = album["viewtype"]
            pfmt = "[{}].{:*^40}\ndesc:{}\npre:{}\nid:{}\ntotal:{} - order:{} - classid:{}".format(n, name, desc, pre,
                                                                                                   pid, total, order,
                                                                                                   classid)
            print(pfmt)
            self.album_info["albunm_list"].append(
                {"name": name or "-", "anonymity_name": anonymity_name, "desc": desc or "-", "pre": pre,
                 "allow_access": allow_access,
                 "viewtype": viewtype,
                 "total": total, "pid": pid, "order": order, "classid": classid, "classname": classname,
                 "createtime": createtime,
                 "lastuploadtime": lastuploadtime, "modifytime": modifytime})

            # 达到一定数量后进行保存到临时文件中
            if len(self.album_info["albunm_list"]) > 30:
                self.save_data_to_temp(filepath=("data",), filename="albunm_list_temp.txt",
                                       data_list=self.album_info["albunm_list"])
                self.album_info["albunm_list"].clear()
            self.totals += 1

        return {"totals": total, "next_page_start": next_page_start, "success": True}

    def cgi_list_photo(self, pid, num: int):
        """只能获取图片"""
        api = self.api_info["Api"]["cgi_list_photo"]
        url = api["url"]
        method = api["method"]
        params = api["params"]
        headers = api["headers"]
        headers["cookie"] = self.api_info["Common"]["headers"]["cookie"]

        params["uin"] = self.qq_info["qq"]
        params["hostUin"] = self.qq_info["qq"]
        params["g_tk"] = self.qq_info["tk"]
        params["t"] = round(time.time() * 1000)
        params["_"] = round(time.time() * 1000)
        params["topicId"] = pid

        resp = self.session.request(method, url=url, params=params, headers=headers)
        data = self.data_parse("shine3_Callback\(", "\);", resp.text)

        if data["code"] != 0:
            print(data["message"])
            return {"success": False}

        photo_list = data["data"]["photoList"]
        if not photo_list:
            return {"success": True}
        pic_key = photo_list[0]["lloc"]
        name = data["data"]["topic"]["name"]
        desc = data["data"]["topic"]["desc"]

        self.album_down_info["albunm_down_list"].append(
            {"name": "{}_{:0>5}".format(name or "相册", num), "desc": desc or "-", "pic_key": pic_key, "pid": pid})

        if len(self.album_down_info["albunm_down_list"]) > 30:
            self.save_data_to_temp(filepath=("data",), filename="albunm_down_list_temp.txt",
                                   data_list=self.album_down_info["albunm_down_list"])
            self.album_down_info["albunm_down_list"].clear()
        return {"success": True}

    def cgi_list_photo2(self, num: int, page_start: int, page_num=30, **photo_info):
        """只能获取图片"""
        api = self.api_info["Api"]["cgi_list_photo"]
        url = api["url"]
        method = api["method"]
        params = api["params"]
        headers = api["headers"]
        headers["cookie"] = self.api_info["Common"]["headers"]["cookie"]

        params["uin"] = self.qq_info["qq"]
        params["hostUin"] = self.qq_info["qq"]
        params["g_tk"] = self.qq_info["tk"]
        params["t"] = round(time.time() * 1000)
        params["_"] = round(time.time() * 1000)
        params["topicId"] = photo_info["pid"]
        params["pageStart"] = page_start
        params["pageNum"] = page_num

        resp = self.session.request(method, url=url, params=params, headers=headers)
        data = self.data_parse("shine3_Callback\(", "\);", resp.text)

        if data["code"] != 0:
            print(data["message"])
            return {"success": False}

        total_in_album = data["data"]["totalInAlbum"]
        total_in_page = data["data"]["totalInPage"]
        if (total_in_page == total_in_album) or (total_in_page < page_num):
            last = False
        else:
            last = True

        photo_list = data["data"]["photoList"]
        if not photo_list:
            return {"last": False}
        pic_format = "png"

        for n, pics in enumerate(photo_list):
            desc = pics["desc"]
            is_video = pics["is_video"]
            name = pics["name"]
            modifytime = self.format_time(pics["modifytime"])
            uploadtime = pics["uploadtime"]
            pic_url = pics["url"]

            print("{}.{:*^20}\nname:{}\nis_video:{}\nmodifytime:{}\npic_url:{}".format(n + 1, desc, name, is_video,
                                                                                       modifytime, pic_url))
            self.pic_info.append(
                {"aname": "{}_{:0>5}".format(photo_info["name"] or "相册", num), "adesc": desc or "-", "pname": name,
                 "pdesc": desc, "pic_url": pic_url, "is_video": is_video, "size1": "-",
                 "pic_format": pic_format, "uploadtime": uploadtime})

        if len(self.pic_info) > 30:
            self.save_data_to_temp(filepath=("data",), filename="pic_info_temp.txt",
                                   data_list=self.pic_info)
            self.pic_info.clear()

        return {"last": last}

    def cgi_floatview_photo_list_v2(self, is_first, **photo_info):
        """获取图片和视频"""
        api = self.api_info["Api"]["cgi_floatview_photo_list_v2"]
        url = api["url"]
        method = api["method"]
        params = api["params"]
        headers = api["headers"]
        headers["cookie"] = self.api_info["Common"]["headers"]["cookie"]
        headers["referer"] = "https://user.qzone.qq.com/{}/main".format(self.qq_info["qq"])

        params["uin"] = self.qq_info["qq"]
        params["hostUin"] = self.qq_info["qq"]
        params["g_tk"] = self.qq_info["tk"]
        params["t"] = self.get_sign()
        params["_"] = round(time.time() * 1000)
        params["topicId"] = photo_info["pid"]
        params["picKey"] = photo_info["pic_key"]
        params["isFirst"] = is_first

        resp = self.session.request(method, url=url, params=params, headers=headers)
        data = self.data_parse("viewer_Callback\(", "\);", resp.text)
        if data["code"] != 0:
            print(data["message"])
            return {"success": False}

        photos = data["data"]["photos"]
        last = data["data"]["last"]  # 1 表示最后一页
        last_pid_key = photos[-1]["picKey"]

        for n, photo in enumerate(photos):
            desc = photo["desc"]
            is_video = photo["is_video"]
            name = photo["name"]
            owner_name = photo["ownerName"]
            upload_time = photo["uploadTime"]
            # topic_name = photo["topicName"]

            if is_video:
                # 预览
                pre_url = photo["url"]
                # 下载
                pic_url = photo["video_info"]["download_url"]
                size1 = photo["video_info"]["size"]
                size2 = self.get_size(photo["video_info"]["size"])
                pic_format = "mp4"
            else:
                pre_url = "-"
                pic_url = photo["url"]
                size1 = "-"
                size2 = "-"
                pic_format = "png"
            print("{}.{:*^20}\nowner_name:{}\nname:{}\nis_video:{}\nupload_time:{}\npic_url:{}\nsize:{}".format(n, desc,
                                                                                                                owner_name,
                                                                                                                name,
                                                                                                                is_video,
                                                                                                                upload_time,
                                                                                                                pic_url,
                                                                                                                size1))
            self.pic_vid_info["pic_vid_list"].append(
                {"aname": photo_info["name"], "adesc": photo_info["desc"], "pname": name or "-", "pdesc": desc or "-",
                 "pre_url": pre_url, "is_video": is_video, "pic_url": pic_url,
                 "size1": size1, "size2": size2, "pic_format": pic_format, "upload_time": upload_time})

            if len(self.pic_vid_info["pic_vid_list"]) > 30:
                self.save_data_to_temp(filepath=("data",), filename="pic_vid_list_temp.txt",
                                       data_list=self.pic_vid_info["pic_vid_list"])
                self.pic_vid_info["pic_vid_list"].clear()

        return {"last": last, "last_pid_key": last_pid_key}

    @staticmethod
    def get_sign():
        rand_num = random.random()
        str_num = f"{rand_num:.16f}"

        sign = str_num[-9:]
        if sign.startswith("0"):
            sign = "9" + sign[1:]
        return sign

    def get_g_tk2(self):
        """第二种，通过python算法实现"""
        hash_val = 5381

        cookie_info = self.cookie_parse()
        skey = cookie_info["p_skey"]
        for char in skey:
            hash_val += (hash_val << 5) + ord(char)
        return {"qq": cookie_info["uin"][2:], "tk": hash_val & 0x7FFFFFFF}

    def cookie_parse(self):
        cookie = self.api_info["Common"]["headers"]["cookie"]
        cookie = self.replace_space(cookie)
        ck_spt = cookie.split(";")
        ck_kv = {kv.split("=")[0]: kv.split("=")[1] for kv in ck_spt}
        return ck_kv

    def main(self):
        save_file_path = self.qqconfig.get("excel_file_info", "save_file_path")
        save_file_name = self.qqconfig.get("excel_file_info", "save_file_name")
        read_file_path = self.qqconfig.get("excel_file_info", "read_file_path")
        read_file_name = self.qqconfig.get("excel_file_info", "read_file_name")
        sheet_name = self.qqconfig.get("excel_file_info", "read_sheet_name")

        # 保存用户的信息，如qq号
        self.save_userinfo_to_temp(filepath=("data",), filename="user_info_temp.txt", d={"user_qq": self.qq_info["qq"]})
        md = input("[1].获取相册信息 - [2].获取相册下载信息 - [3].获取图片视频信息 - [4].只获取图片信息\n:")
        if md == "1":
            # 获取相册信息，并保存数据
            page_start = 0
            while True:
                ret = self.fcg_list_album_v3(page_start)
                page_start = ret["next_page_start"]
                if (ret["totals"] == self.totals) or (page_start is None):
                    print("获取结束")
                    break
                if ret["success"] is False:
                    print("cookie失效了")
                    break
                time.sleep(round(random.uniform(1, 3), 2))

            if self.album_info["albunm_list"]:
                self.save_data_to_temp(filepath=("data",), filename="albunm_list_temp.txt",
                                       data_list=self.album_info["albunm_list"])

            user_info = self.read_userinfo_from_temp(filepath=("data",), filename="user_info_temp.txt")
            data_list = self.read_data_from_temp(filepath=("data",), filename="albunm_list_temp.txt")
            title = ['name', 'anonymity_name', 'desc', 'pre', 'allow_access', 'viewtype', 'total', 'pid', 'order',
                     'classid',
                     'classname', 'createtime', 'lastuploadtime', 'modifytime']
            if not (user_info and data_list):
                return
            self.write_excel(data_list=data_list, title=title, sheet_name=str(user_info["user_qq"]),
                             name="{}的相册".format(user_info["user_qq"]),
                             filepath=(save_file_path,),
                             filename=save_file_name)
            self.file_delete(filepath=("data",), filename="user_info_temp.txt")
            self.file_delete(filepath=("data",), filename="albunm_list_temp.txt")

        elif md == "2":
            if sheet_name != self.qq_info["qq"]:
                print("请检查配置文件中需要获取数据的QQ号是否正确~[{}] != [{}]".format(sheet_name, self.qq_info["qq"]))
                return
            # 获取相册下载信息，并保存数据
            data = self.read_excel(filepath=(read_file_path,), filename=read_file_name, sheet_name=sheet_name)
            for n, dt in enumerate(data["data_list"]):
                ret = self.cgi_list_photo(dt["pid"], n + 1)
                if ret["success"] is False:
                    print("cookie失效了~")
                    break
                else:
                    print("[{}]-[{}] 获取成功~".format(dt["name"], dt["pid"]))
                time.sleep(round(random.uniform(1, 3), 2))
            if self.album_down_info["albunm_down_list"]:
                self.save_data_to_temp(filepath=("data",), filename="albunm_down_list_temp.txt",
                                       data_list=self.album_down_info["albunm_down_list"])
            title = ['name', 'desc', 'pic_key', 'pid']
            user_info = self.read_userinfo_from_temp(filepath=("data",), filename="user_info_temp.txt")
            data_list = self.read_data_from_temp(filepath=("data",), filename="albunm_down_list_temp.txt")

            if not (user_info and data_list):
                return
            self.write_excel(data_list=data_list, title=title, sheet_name=str(user_info["user_qq"]) + "_download_info",
                             name="{}的下载信息".format(user_info["user_qq"]),
                             filepath=(save_file_path,),
                             filename=save_file_name)
            self.file_delete(filepath=("data",), filename="user_info_temp.txt")
            self.file_delete(filepath=("data",), filename="albunm_down_list_temp.txt")

        elif md == "3":
            if sheet_name != self.qq_info["qq"]:
                print("请检查配置文件中需要获取数据的QQ号是否正确~[{}] != [{}]".format(sheet_name, self.qq_info["qq"]))
                return
            # 获取图片、视频信息，并保存数据
            data = self.read_excel(filepath=(read_file_path,), filename=read_file_name,
                                   sheet_name="{}_download_info".format(sheet_name))

            is_next = True  # 是否继续
            for dt in data["data_list"]:
                is_last = 0
                is_first = 1  # 是否包含第一个，0不包含，1包含
                while is_last == 0:
                    ret = self.cgi_floatview_photo_list_v2(is_first, **dt)
                    if ret.get("success") is False:
                        print("cookie失效了~")
                        is_next = False
                        break
                    is_last = ret["last"]
                    is_first = 0
                    # 从这个开始往后获取
                    dt["pic_key"] = ret["last_pid_key"]
                    time.sleep(round(random.uniform(1, 3), 2))
                if not is_next:
                    break

            if self.pic_vid_info["pic_vid_list"]:
                self.save_data_to_temp(filepath=("data",), filename="pic_vid_list_temp.txt",
                                       data_list=self.pic_vid_info["pic_vid_list"])
            title = ['aname', 'adesc', 'pname', 'pdesc', 'pre_url', 'is_video', 'pic_url', 'size1', 'size2',
                     'pic_format',
                     'upload_time']
            user_info = self.read_userinfo_from_temp(filepath=("data",), filename="user_info_temp.txt")
            data_list = self.read_data_from_temp(filepath=("data",), filename="pic_vid_list_temp.txt")
            if not (user_info and data_list):
                return
            self.write_excel(data_list=data_list, title=title, sheet_name=str(user_info["user_qq"]) + "_pic_vid",
                             name="{}的图片和视频".format(user_info["user_qq"]),
                             filepath=(save_file_path,),
                             filename=save_file_name)
            self.file_delete(filepath=("data",), filename="user_info_temp.txt")
            self.file_delete(filepath=("data",), filename="pic_vid_list_temp.txt")
        elif md == "4":
            if sheet_name != self.qq_info["qq"]:
                print("请检查配置文件中需要获取数据的QQ号是否正确~[{}] != [{}]".format(sheet_name, self.qq_info["qq"]))
                return
            data = self.read_excel(filepath=(read_file_path,), filename=read_file_name, sheet_name=sheet_name)
            is_next = True
            for n, dt in enumerate(data["data_list"]):
                last = True
                page_start = 0
                page_num = 30
                while last:
                    ret = self.cgi_list_photo2(n + 1, page_start, page_num, **dt)
                    if ret.get("success") is False:
                        is_next = False
                        break
                    last = ret["last"]
                    page_start += page_num
                    time.sleep(round(random.uniform(1, 3), 2))
                if not is_next:
                    break

            if self.pic_info:
                self.save_data_to_temp(filepath=("data",), filename="pic_info_temp.txt",
                                       data_list=self.pic_info)
            title = ['aname', 'adesc', 'pname', 'pdesc', 'pic_url', 'is_video', 'size1', 'pic_format',
                     'uploadtime']
            user_info = self.read_userinfo_from_temp(filepath=("data",), filename="user_info_temp.txt")
            data_list = self.read_data_from_temp(filepath=("data",), filename="pic_info_temp.txt")
            if not (user_info and data_list):
                return
            self.write_excel(data_list=data_list, title=title,
                             sheet_name=str(user_info["user_qq"]) + "_pic",
                             name="{}的图片信息".format(user_info["user_qq"]),
                             filepath=(save_file_path,),
                             filename=save_file_name)
            self.file_delete(filepath=("data",), filename="user_info_temp.txt")
            self.file_delete(filepath=("data",), filename="pic_info_temp.txt")

        else:
            print("输入有误~")


if __name__ == '__main__':
    qq = QQ()
    qq.main()
