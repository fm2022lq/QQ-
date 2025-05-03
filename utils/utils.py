# -*- coding: utf-8 -*-
# @Samp: pip install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple
# @Time: 2025/4/15 13:03
# @Author: jef.ld
# @Project: qq_space
# @File: utils
import configparser
import os
import re
import json
import yaml
import chardet
import traceback
import time
import openpyxl
import pandas
from openpyxl.styles import Alignment, numbers, Font, PatternFill
from typing import List, Dict, Any
from collections import defaultdict


class QQSpace:
    # 获取当前路径
    @classmethod
    def get_current_path(cls, filepath: tuple[str, ...], filename=None):
        """
        获取上级目录，然后通过参数进行拼接获取目标路径
        """
        if not isinstance(filepath, tuple):
            print("filepath error 请传元组对象")
            raise TypeError

        curr = os.path.dirname(__file__)
        curr = os.path.abspath(os.path.join(curr, ".."))
        if filename is None:
            curr = os.path.join(curr, *filepath)
        else:
            curr = os.path.join(curr, *filepath, filename)
        return curr

    @classmethod
    def read_yaml(cls, filepath: tuple[str, ...], filename, encoding=None):
        """
        指定config目录下
        filepath: 完整的文件名，如：api_info.yaml
        """
        if encoding is None:
            ecod = cls.detect_file_encoding(filepath, filename)
            if ecod is None:
                print("获取文件编码失败，文件不存在")
                return ecod
        else:
            ecod = encoding
            print("指定文件编码格式：{}".format(ecod))

        file = cls.get_current_path(filepath, filename)
        try:
            with open(file, mode="r", encoding=ecod) as f:
                data = yaml.load(f.read(), Loader=yaml.FullLoader)
            return data
        except UnicodeDecodeError:
            ecod = cls.detect_file_encoding(filepath, filename, is_full=True)
            with open(file, mode="r", encoding=ecod) as f:
                data = yaml.load(f.read(), Loader=yaml.FullLoader)
            return data
        except Exception as e:
            print(e)
            return None

    @classmethod
    def write_data_to_yaml(cls, filepath: tuple[str, ...], filename, d, encoding="utf-8"):
        """
        指定config目录下
        d: 需要保存的数据
        覆盖保存
        """
        cls.folders_create(filepath)
        file = cls.get_current_path(filepath, filename)
        with open(file, "w", encoding=encoding) as f:
            yaml.dump(data=d, stream=f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        # log.info("{}保存完成".format(filename))
        print("{}保存完成".format(file))

    @classmethod
    def folders_create(cls, filepath: tuple[str, ...]):
        """
        用于创建目录
        :return:
        """
        path = cls.get_current_path(filepath=filepath)
        if not os.path.exists(path):
            os.makedirs(path)
            # log.info("创建目录：{}".format(path))
            print("创建目录：{}".format(path))

    @classmethod
    def read_config(cls, filepath: tuple[str, ...], filename, encoding=None):
        """
        读取配置文件
        :return:
        """
        if encoding is None:
            ecod = cls.detect_file_encoding(filepath, filename)
            if ecod is None:
                print("获取文件编码失败，文件不存在")
                return ecod
        else:
            ecod = encoding
            print("指定文件编码格式：{}".format(ecod))
        file = cls.get_current_path(filepath, filename)
        conf = configparser.RawConfigParser()

        try:
            conf.read(file, encoding=ecod)
            return conf
        except UnicodeDecodeError:
            ecod = cls.detect_file_encoding(filepath, filename, is_full=True)
            conf.read(file, encoding=ecod)
            return conf
        except Exception as e:
            print(e)
            return None

    # 获取文件的编码
    @classmethod
    def detect_file_encoding(cls, filepath: tuple[str, ...], filename, is_full=False):
        """
        主要是用来获取不同文件的编码，方便读取
        :param is_full:
        :param filename:
        :param filepath:
        :return:
        """
        stack = traceback.extract_stack()
        caller = stack[-2]  # 上一层栈帧

        file = cls.get_current_path(filepath, filename)
        if not os.path.isfile(file):
            # log.error("No such file or directory: {}".format(filename))
            print("No such file or directory: {}".format(file))
            return None

        with open(file, mode="rb") as f:
            # raw_data = f.read() # 这种效率有点慢，对于大文件时
            if is_full:
                print("读取全部文件获取编码:{}".format(caller))
                raw_data = f.read()
            else:
                print("按部分文件获取编码:{}".format(caller))
                raw_data = f.read()[0:10240]  # 只截取一部分
            result = chardet.detect(raw_data)
            return result["encoding"]

    @classmethod
    def read_file(cls, filepath: tuple, filename, encoding=None):
        if encoding is None:
            ecod = cls.detect_file_encoding(filepath, filename)
            if ecod is None:
                print("获取文件编码失败，文件不存在")
                return ecod
        else:
            ecod = encoding
            print("指定文件编码格式：{}".format(ecod))
        file = cls.get_current_path(filepath, filename)
        try:
            with open(file, mode="r", encoding=ecod) as f:
                data = f.read()
            return data
        except UnicodeDecodeError:
            ecod = cls.detect_file_encoding(filepath, filename, is_full=True)
            with open(file, mode="r", encoding=ecod) as f:
                data = f.read()
            return data

    @staticmethod
    def data_parse(start, end, data):
        # 解析返回数据，转换成json字典格式
        s_json = re.search(start + "(.*?)" + end, data, re.S)
        if s_json:
            return json.loads(s_json.group(1))

    @staticmethod
    def format_time(timestamp: int):
        # 时间格式化
        timestamp = int(str(timestamp)[:10])
        format_time = time.strftime("%Y年%m月%d日 %H时%M分%S秒", time.localtime(timestamp))
        return format_time

    @staticmethod
    def get_size(data_size: int):
        # 文件大小类型转换
        if data_size < 1024:
            return "%s B" % data_size  # 字节
        elif data_size < 1024 ** 2:
            return "%s KB" % (round(data_size / 1024 ** 1, 2))  # KB
        elif data_size < 1024 ** 3:
            return "%s MB" % (round(data_size / 1024 ** 2, 2))  # MB
        elif data_size < 1024 ** 4:
            return "%s GB" % (round(data_size / 1024 ** 3, 2))  # GB
        elif data_size < 1024 ** 5:
            return "%s TB" % (round(data_size / 1024 ** 4, 2))  # 太字节
        elif data_size < 1024 ** 6:
            return "%s PB" % (round(data_size / 1024 ** 5, 2))  # 拍字节
        elif data_size < 1024 ** 7:
            return "%s EB" % (round(data_size / 1024 ** 6, 2))  # 艾兆字节
        else:
            return "%s ZB" % (round(data_size / 1024 ** 7, 2))  # 泽字节

    def save_data_to_temp(self, filepath: tuple[str, ...], filename, data_list):
        # 临时保存照片、视频信息
        file = self.get_current_path(filepath, filename)
        with open(file, mode="a", encoding="utf-8") as f:
            for d in data_list:
                f.write(json.dumps(d, ensure_ascii=False))
                f.write("\n")
        print("{} 临时数据保存完成".format(filename))

    def save_userinfo_to_temp(self, filepath: tuple[str, ...], filename, d, encoding="utf-8"):
        # 临时保存用户信息
        file = self.get_current_path(filepath, filename)
        with open(file, mode="w", encoding=encoding) as f:
            f.write(json.dumps(d, ensure_ascii=False))
        print("{} 用户信息已保存".format(filename))

    def read_userinfo_from_temp(self, filepath: tuple[str, ...], filename, encoding="utf-8"):
        # 从临时文本中读取用户信息
        file = self.get_current_path(filepath, filename)
        if not os.path.isfile(file):
            print("{} 不存在~".format(filename))
            return None
        with open(file, mode="r", encoding=encoding) as f:
            return json.load(fp=f)

    def read_data_from_temp(self, filepath: tuple[str, ...], filename, encoding="utf-8"):
        # 从临时文本中读取数据
        data_list = []
        file = self.get_current_path(filepath, filename)
        if not os.path.isfile(file):
            print("{} 不存在~".format(filename))
            return None
        with open(file, mode="r", encoding=encoding) as f:
            for d in f.readlines():
                data_list.append(json.loads(d))
        return data_list

    def file_delete(self, filepath: tuple[str, ...], filename):
        # 删除临时文件
        file = self.get_current_path(filepath, filename)
        if os.path.isfile(file):
            os.remove(file)
            print(file, "已删除")

    @staticmethod
    def teshu(sstr):
        new_str = re.sub(r'[?<>|\\/:：!&#*\[\]\n\s\t]', '_', sstr)
        if len(new_str) > 31:
            new_str = new_str[0:31]
        return new_str

    # 特殊字符处理 - 针对excel的
    @classmethod
    def teshu2(cls, sstr):
        new_str = re.sub(r'[?<>|\\/:：!&#*\[\]\n\s\t]', '_', sstr)
        if len(new_str) > 31:
            new_str = new_str[0:31]
        return new_str

    # 保存数据到excel文件中
    @classmethod
    def write_excel(cls, data_list: list, title, filepath: tuple = ("data",), filename="douyin.xlsx",
                    sheet_name="douyin",
                    name="author_name"):
        """
        :param filename:
        :param name:
        :param data_list: [{},{}]
        :param title: ["字段1","字段2"]
        :param filepath: 文件路径如：("data", "test.xlsx")
        :param sheet_name: 工作表名
        :return:
        """

        sheet_name = cls.teshu2(sheet_name)
        cls.creat_excel(name=name, title=title, filepath=filepath, sheet_name=sheet_name, filename=filename)
        # 打开文件
        path = cls.get_current_path(filepath, filename)
        sheet_name = sheet_name
        wb = openpyxl.load_workbook(path)
        # 对指定sheet操作
        sheet = wb[sheet_name]

        alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
        r = 3  # 从第三行开始写入数据
        for L in data_list:
            # L 是字典
            c = 1
            for v in L.values():
                sheet.cell(row=r, column=c, value=str(v)).number_format = numbers.FORMAT_TEXT
                sheet.cell(row=r, column=c).alignment = alignment
                c += 1
            r += 1

        cls.set_all(sheet=sheet)
        cls.set_width(sheet)
        wb.save(path)
        # log.info("数据保存完毕")
        print("数据保存完毕")

    @classmethod
    def creat_excel(cls, title, name="临时名字", filepath: tuple = ("data",), filename="douyin.xlsx",
                    sheet_name="douyin"):
        """
        :param filename:
        :param title: 字段，标题。列表
        :param name: 第一行的名字
        :param filepath: 文件路径，如：("data", "test.xlsx")，这个拼接后就是 xxx/data/test.xlsx
        :param sheet_name: 创建的工作表名
        :return:
        """
        # cookie的key
        key_list = title

        cls.folders_create(filepath)  # 创建文件夹
        path = cls.get_current_path(filepath, filename)
        if not os.path.exists(path):
            wb = openpyxl.Workbook()
            del wb["Sheet"]
            wb.create_sheet(sheet_name)
            wb.save(path)

        # 打开文件
        wb = openpyxl.load_workbook(path)
        # 判断要操作的sheet是否存在,存在则删除重新创建
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]
            wb.create_sheet(sheet_name)
        else:
            wb.create_sheet(sheet_name)
        # 对指定sheet操作
        sheet = wb[sheet_name]

        # 居中样式
        align = Alignment(horizontal='center', vertical='center', wrap_text=False)  # wrap_text=True 是否自动换行
        font = Font(name="仿宋", color="FF0000", bold=True)
        # 颜色填充
        fill_y = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # 黄色
        fill_b = PatternFill(start_color="C5D9F1", end_color="C5D9F1", fill_type="solid")  # 浅蓝色

        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(key_list))  # 合并居中 1 行 n 列
        sheet["A1"].alignment = align
        sheet["A1"] = name
        sheet["A1"].font = font
        sheet["A1"].fill = fill_y

        for k in range(1, len(key_list) + 1):
            sheet.cell(row=2, column=k, value=key_list[k - 1]).alignment = align
            sheet.cell(row=2, column=k).font = font  # 字体颜色
            sheet.cell(row=2, column=k).fill = fill_b

        wb.save(path)
        # log.info("Excel文件创建完毕")
        print("Excel文件创建完毕")

    @classmethod
    def set_all(cls, sheet):
        from openpyxl.styles import Side, Border

        start = "A1"
        end = sheet.cell(row=sheet.max_row, column=sheet.max_column).coordinate
        r_row = len(sheet[start:end])
        c_col = len(sheet[start:end][0])
        # log.info("行：{} 列：{}".format(r_row, c_col))
        print("行：{} 列：{}".format(r_row, c_col))

        for v in sheet[start:end]:
            for i in v:
                i.border = Border(top=Side(border_style="thin", color="FF000000"),
                                  bottom=Side(border_style="thin", color="FF000000"),
                                  left=Side(border_style="thin", color="FF000000"),
                                  right=Side(border_style="thin", color="FF000000")
                                  )

    @classmethod
    def set_width(cls, sheet):
        from openpyxl.utils import get_column_letter
        temp_c = {}  # {'column_1':{'column': 1,'width':set()}}
        for c in range(1, sheet.max_column + 1):
            temp_c[f"column_{c}"] = {'column': c, 'width': set()}
            for r in range(3, sheet.max_row + 1):
                value_ = sheet.cell(row=r, column=c).value
                if value_ is None:
                    temp_c[f"column_{c}"]["width"].add(0)
                else:
                    v_len = len(str(value_))  # 由于可能存在int类型，故转换str方能获取长度
                    temp_c[f"column_{c}"]["width"].add(v_len)
                    if v_len >= 45:
                        # 当单元格值长度大于等于45时，就不需要再往后检索了，节省时间
                        break
        # 获取列单元格的最大值 与 标题的长度进行对比  获取最终的值
        for k in temp_c:
            title = sheet.cell(row=2, column=temp_c[k]["column"]).value
            max_v = max(temp_c[k]["width"])
            if title is None:
                title_len = 0
            else:
                title_len = len(str(title))
            # 单元格值长度和标题长度都小于等于45，取较大者
            # 在基础长度上加一定的长度后观感会好一些，这里加 10
            if (max_v <= 45) and (title_len <= 45):
                temp_c[k]["width"] = max_v + 10 if max_v >= title_len else title_len + 10
            elif max_v <= 45:
                temp_c[k]["width"] = max_v + 10
            elif title_len <= 45:
                temp_c[k]["width"] = 35
            # 两者长度都大于45，值设为45
            else:
                temp_c[k]["width"] = 45

        # 设置每一列的宽度
        for k in temp_c:
            sheet.column_dimensions[get_column_letter(temp_c[k]["column"])].width = temp_c[k]["width"]
        # log.info("列宽设置完毕...")
        print("列宽设置完毕...")

    def read_excel(self, filepath: tuple[str, ...], filename, sheet_name):
        file = self.get_current_path(filepath, filename)
        try:
            dataframe = pandas.read_excel(io=file, header=None, sheet_name=sheet_name)
        except FileNotFoundError as e:
            print(e)
            return None
        except ValueError as e:
            print(e)
            return None
        # 空白行转成空字符串  nan-->""
        dataframe = dataframe.fillna("")

        name = dataframe.iloc[0].values[0]
        data = {"name": name, "sheet_name": sheet_name, "data_list": []}

        # 以第二行作为键，第三行以后作为值
        new_columns = dataframe.iloc[1]
        # 设置新列名
        dataframe.columns = new_columns
        # 重置索引，从第三行开始作为数据
        dataframe = dataframe.iloc[2:].reset_index(drop=True)

        for n, v in dataframe.iterrows():
            data["data_list"].append(dict(v))
        print("excel数据读取完成")
        return data

    @staticmethod
    def replace_space(str_dt):
        # 去除空白字符
        if isinstance(str_dt, str):
            str_dt = str_dt
        else:
            str_dt = "%s"%(str_dt,)

        new_str_dt = re.sub("[\s\n]", "", str_dt)
        return new_str_dt

    @staticmethod
    def truncate_string(s: str, max_length: int):
        if max_length <= 4:
            return "%s..." % (s[:3])
        elif len(s) > max_length:
            half_length = max_length // 3
            # 不包括省略号，需要包括的话再减3
            end_length = max_length - half_length

            if end_length == 0:
                ed_str = ""
            elif end_length < 0:
                ed_str = s[end_length:]
            else:
                ed_str = s[-end_length:]
            return "%s...%s" % (s[:half_length], ed_str)
        else:
            return s

    @staticmethod
    def down_check(file_info: List[Dict[str, Any]]):
        total = defaultdict(int)
        suc_total = defaultdict(int)
        for f in file_info:
            filepath = f["filepath"]
            size1 = f.get("size1")  # 只有两种结果，空字符或数字
            if isinstance(size1, str) and size1.isdigit():
                size1 = int(size1)
            else:
                size1 = None

            file_type = f["type"]
            total[file_type] += 1

            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                if size1 is None:
                    if size > 0:
                        suc_total[file_type] += 1
                    else:
                        os.remove(filepath)
                else:
                    if size == size1:
                        suc_total[file_type] += 1
                    else:
                        os.remove(filepath)

        print("{:*^30}".format("最终下载情况"))
        print("Expected download:")
        print("video: - {} - image: - {}".format(total["video"], total["image"]))
        print("Success:")
        print("video: - {} - image: - {}".format(suc_total["video"], suc_total["image"]))
        print("Failed:")
        print("video: - {} - image: - {}".format(total["video"] - suc_total["video"],
                                                 total["image"] - suc_total["image"]
                                                 ))
