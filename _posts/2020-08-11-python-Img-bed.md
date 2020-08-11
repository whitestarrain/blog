---
title: python调用图床替换链接
layout: post
categories:
    - Python
    - Spider
description: 博客图片自动上传图床并替换链接,自动完成第三方图床的使用，提高访问速度。
---

使用python进行实现。
在以游客身份通过爬虫方式和登录后使用官方api两种情况下调用了imgbb的api。但最终使用的是阿里图床。imgbb两种面向探索过程。如果单纯想查看调用阿里api请查看ali图床部分

实现了图床图片url和相对路径url的互换。
<!-- more -->

# 1. imgbb

## 1.1. 游客身份

### 1.1.1. 上传图片请求分析

![](https://ae01.alicdn.com/kf/Hb274dc13551242f4bd7e6ee47b094693V.jpg)

- 请求体中一共有五个参数，多次上传图片后分析可得
    - source:二进制文件，就是图片数据
    - type: file,固定值
    - action: upload,固定值
    - timestamp: 时间戳，在请求时通过python可以获得。`int(time.time())`
    - auth_token：也就是token，用于验证，**需要进行获取**

### 1.1.2. token获取

在全部文件中搜索token，若未发现token的值，刷新页面重新搜索
> token应该从服务器获取的，如果打开开发者工具太晚可能无法捕捉到之前资源

可以发现auth_token的值。位于首页页面。通过正则表达式可以提取
```python
token = re.findall(r"PF.obj.config.auth_token=\"(\w*)\"", html_str)[0]
```
![](https://ae01.alicdn.com/kf/H9bf53dccfb43424b828fe888a0fdc14fC.jpg)


### 1.1.3. 响应分析

搜索上传图片后跳转页面显示的连接，可以发现与响应的json数据中的该条相同
![](https://ae01.alicdn.com/kf/H9161959232084b6aac149ed226125489q.jpg)
通过解析json字符串即可获得

### 1.1.4. 代码

```python

def img_to_url(self, path=""):
    """ 将img上传到图床并返回URL。
    """
    print("正在上传图片-----%s",path)
    file_name = ""

    # 获取token
    if(self.token == None):
        self.get_token()
    
    # 获得文件名
    if path.find("/") != -1:
        file_name = path.split("/")[-1:][0]
    else:
        file_name = path.split("\\")[-1:][0]

    # 设置请求体参数
    data = {
        "type": "file",
        "action": "upload",
        "timestamp": int(time.time()),
        "auth_token": self.__class__.token
    }

    # 设置上传文件
    file = {
        "source": (file_name, open(path, "rb"), "image/jpeg"),
    }

    # 进行请求
    response = requests.post(
        self.__class__.upload_url, headers=self.__class__.headers, files=file, data=data)
    
    # 解析json
    json_o = json.loads(response.content.decode("utf-8"))

    # 返回路径
    return json_o["image"]["display_url"]

```

## 1.2. 官方api

### 1.2.1. 分析

在imgbb进行注册后，点击左上角关于，进入官方api文档
![](https://ae01.alicdn.com/kf/H00a3d692f3c24bed81ed5878f0987bc1J.jpg)

- 参数：
    - key:注册后可以在上方生成。必选
    - image:base64编码后的图片数据
    - name:图片名称，可选
    - expiraion:图片描述，可选

- 响应json数据结构api文档下方已给出

### 1.2.2. 代码调用

```python
def img_to_url_api(self,path):
    """ 通过api接口上传到图床并返回url """
    print("正在上传图片-----%s",path)

    # 获得文件名
    file_name = ""
    if path.find("/") != -1:
        file_name = path.split("/")[-1:][0]
    else:
        file_name = path.split("\\")[-1:][0]
    
    with open(path,"rb") as file:

        # 设置请求体
        data = {
            "key":self.__class__.key,
            "name":file_name,
            "image":base64.b64encode(file.read())
        }

        # 请求响应
        response = requests.post( self.__class__.api_url, data = data)
    # 解析json
    json_o = json.loads(response.content.decode("utf-8"))
    return json_o["data"]["image"]["url"]
```

### 1.2.3. 问题

在第一次访问图片有时会发生链接跳转，导致嵌入到md中后图片无法正常显示

fidder抓包后可以发现两次请求完全相同，但结果不同。未发现解决方式。


# 2. ali图床

## 2.1. api文档

官方未提供api，此处使用第三方提供api
[api文档](https://api.wfblog.net/apidetail/21.html)
> 接口地址中有两个api接口，一个cn，一个us，根据需求选择

## 2.2. 代码调用

```python

api_url = "https://cn1.api.wfblog.net/ali.pic.php"
def img_to_url_api(self,path):
    """ 通过api接口上传到图床并返回url """
    print("正在上传图片-----%s" % path)
    with open(path,"rb") as file_:
        file = {
            "file":file_
        }
        response = requests.post(self.__class__.api_url,files = file)
    json_o = json.loads(response.content.decode("utf-8"))
    return json_o["data"]["url"]
```

# 3. url和path互相转换

在每次获得url地址后，都将path和url存储到json文件mapper.json中。不断更新mapper.json

通过正则获取md文件中的图片路径，并进行替换

- 转换为url路径
    ```python
    def update_md_file(self,path,json_dict):
        print("***开始更新文件***")
        url_or_path_list = None

        # 打开md文件
        with open(path, "r+", encoding="utf-8") as md_file:
            text = md_file.read()

            # 获得所有图片路径
            url_or_path_list = re.findall(r"!\[.*\]\((.*)\)", text)

            # 获得本地图片格式的路径
            path_list = [i for i in url_or_path_list if i.startswith("..")]
            if(len(path_list)==0):
                print("      无需替换更新")
                return
            print("     正在更新文件")

            # 读取mapper.json中文件内容进行替换
            for i in path_list:
                text = text.replace(i,json_dict[i])
                print("     >>>>替换图片%s--->%s" % (i,json_dict[i]))

            # 重新写入
            md_file.seek(0)
            md_file.truncate()
            md_file.write(text)
        print("***更新文件完成***")
    ```
- 转换为path路径
    ```python
    def a_file_to_path(self, path):
        print("***开始更新文件%s***" % path)

        # 此处读取mapper.json文件
        if self.__class__.json_dict == None:
            with open("./mapping.json", "r") as json_file:
                self.__class__.json_dict = json.load(json_file)
        json_dict = self.__class__.json_dict

        url_or_path_list = None

        # 打开md文件
        with open(path, "r+", encoding="utf-8") as md_file:
            text = md_file.read()

            # 获得所有图片路径
            url_or_path_list = re.findall(r"!\[.*\]\((.*)\)", text)
            url_list = [i for i in url_or_path_list if i.startswith("http")]
            if(len(url_list) == 0):
                print("      无需替换更新")
                return
            print("      正在更新文件")

            # 将url替换为path
            for i in url_list:
                j = list(json_dict.keys())[list(json_dict.values()).index(i)]
                text = text.replace(i,j)
                print("      >>>>>替换图片%s--->%s" % (i,j))
            
            # 重新写入
            md_file.seek(0)
            md_file.truncate()
            md_file.write(text)
        print("---该文件完成---")
    ```




