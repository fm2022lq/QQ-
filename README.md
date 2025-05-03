# QQ空间个人相册信息采集

需要的依赖：

```tex
aiohttp
aiofiles
requests
PyYAML
chardet
openpyxl
pandas

```

配置文件[config.ini]说明

```tex
[qq_space]
rep_count = 5 超时重试次数
timeout = 30 超时

[excel_file_info]
save_file_path = 保存Excel文件的路径，如：D:\xxx\xxx
save_file_name = Excel文件名，如：xxx.excel
read_file_path = 读取Excel文件的路径，如：D:\xxx\xxx
read_file_name = Excel文件名，如：xxx.excel
read_sheet_name = 你的QQ号

[download_info]
read_file_name = Excel文件名，如：xxx.excel
read_file_path = 读取Excel文件的路径，如：D:\xxx\xxx
read_sheet_name = 你的QQ号_pic_vid

download_path = 保存图片、视频的路径，如：D:\xxx
```

配置cookie

```tex
cookie: p_skey=[登录QQ空间后在cookie中复制p_skey];p_uin=o0[你的QQ号];uin=o0[你的QQ号]
如：
cookie: p_skey=xxxxxxxx;p_uin=o05239999520;uin=o05239999520
```

运行qq_space_request.py

```tex
指定文件编码格式：utf-8
user_info_temp.txt 用户信息已保存
[1].获取相册信息 - [2].获取相册下载信息 - [3].获取图片视频信息 - [4].只获取图片信息
:
```

