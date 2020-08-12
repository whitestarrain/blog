import requests
import base64
import re
import time
import json
import os
""" 将md中的本地路径转换为url路径
    避免图床原因导致博客瘫痪
"""


class to_url:
    # home_page = "https://imgbb.com"
    # upload_url = "https://imgbb.com/json"
    # token = ""
    # api_url = "https://api.imgbb.com/1/upload"
    api_url = "https://cn1.api.wfblog.net/ali.pic.php"
    key = "6ab530ea11787a1577297c059c113960"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
    }

    # def get_token(self):
    #     """ 获得token
    #     """
    #     html_str = requests.get(
    #         self.__class__.home_page, headers=self.__class__.headers).content.decode("utf-8")
    #     token = re.findall(r"PF.obj.config.auth_token=\"(\w*)\"", html_str)[0]
    #     self.__class__.token = token
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
    # def img_to_url_api(self,path):
    #     """ 通过api接口上传到图床并返回url """
    #     print("正在上传图片-----%s",path)

    #     # 获得文件名
    #     file_name = ""
    #     if path.find("/") != -1:
    #         file_name = path.split("/")[-1:][0]
    #     else:
    #         file_name = path.split("\\")[-1:][0]
        
    #     with open(path,"rb") as file:
    #         data = {
    #             "key":self.__class__.key,
    #             "name":file_name,
    #             "image":base64.b64encode(file.read())
    #         }
    #         response = requests.post( self.__class__.api_url, data = data)
    #     json_o = json.loads(response.content.decode("utf-8"))
    #     return json_o["data"]["image"]["url"]
    

    # def img_to_url(self, path=""):
    #     """ 将img上传到图床并返回URL。已弃用
    #     """
    #     print("正在上传图片-----%s",path)
    #     file_name = ""
    #     if(self.token == None):
    #         self.get_token()
    #     if path.find("/") != -1:
    #         file_name = path.split("/")[-1:][0]
    #     else:
    #         file_name = path.split("\\")[-1:][0]

    #     data = {
    #         "type": "file",
    #         "action": "upload",
    #         "timestamp": int(time.time()),
    #         "auth_token": self.__class__.token
    #     }
    #     file = {
    #         "source": (file_name, open(path, "rb"), "image/jpeg"),
    #     }
    #     response = requests.post(
    #         self.__class__.upload_url, headers=self.__class__.headers, files=file, data=data)
    #     json_o = json.loads(response.content.decode("utf-8"))
    #     return json_o["image"]["display_url"]

    def get_image_path_or_url(self, path):
        """ 获得一个md文件中的图片地址 """
        url_list = None
        with open(path, "r", encoding="utf-8") as md_file:
            url_list = re.findall(r"!\[.*\]\((.*)\)", md_file.read())
        return url_list

    def read_json(self):
        """ 读取json数据返回python数据类型 """
        json_dict = ""
        with open("./mapping.json", "r") as json_file:
            json_dict = json.load(json_file)
        return json_dict

    def update_json_file(self, json_str):
        """ 更新当前目录下的json文件 """
        print("正在更新json")
        with open("./mapping.json","w") as file:
            file.write(json_str)
    def update_md_file(self,path,json_dict):
        print("***开始更新文件***")
        url_or_path_list = None
        with open(path, "r+", encoding="utf-8") as md_file:
            text = md_file.read()
            url_or_path_list = re.findall(r"!\[.*\]\((.*)\)", text)
            path_list = [i for i in url_or_path_list if i.startswith("..")]
            if(len(path_list)==0):
                print("      无需替换更新")
                return
            print("     正在更新文件")
            for i in path_list:
                text = text.replace(i,json_dict[i])
                print("     >>>>替换图片%s--->%s" % (i,json_dict[i]))
            md_file.seek(0)
            md_file.truncate()
            md_file.write(text)
        print("***更新文件完成***")

    def convert_a_file(self,path):
        """ 转换一个文件 """
        print("******开始转换******-----%s" % path)
        url_or_path_list = self.get_image_path_or_url(path)
        path_list = [i for i in url_or_path_list if i.startswith("..")]
        json_dict = self.read_json()
        new_image = 0
        for i in path_list:
            if not i in json_dict:
                new_image+=1
                json_dict[i] = self.img_to_url_api(i)
        json_str = json.dumps(json_dict,indent=4)
        if new_image>0:
            self.update_json_file(json_str)
        self.update_md_file(path,json_dict)
        print("~~~~~~转换完成~~~~~~")
    
    def convert_all_file(self):
        # files = [os.path.join(a,k[i]) for a,j,k in os.walk("../_posts/") for i in range(len(k))]
        i,j,k= os.walk("../_posts/").__next__()
        files = list()
        for a in range(len(k)):
            files.append(os.path.join(i,k[a]))
        for f in files:
            self.convert_a_file(f)

if __name__ == "__main__":
    o = to_url()
    o.convert_all_file()
    pass
