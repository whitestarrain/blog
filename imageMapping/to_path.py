import re
import os
import json
""" 将md中的url路径转换为本地路径
    避免图床原因导致博客瘫痪
"""


class to_path:
    json_dict = None

    def a_file_to_path(self, path):
        print("***开始更新文件%s***" % path)
        if self.__class__.json_dict == None:
            with open("./mapping.json", "r") as json_file:
                self.__class__.json_dict = json.load(json_file)
        json_dict = self.__class__.json_dict
        url_or_path_list = None
        with open(path, "r+", encoding="utf-8") as md_file:
            text = md_file.read()
            url_or_path_list = re.findall(r"!\[.*\]\((.*)\)", text)
            url_list = [i for i in url_or_path_list if i.startswith("http")]
            if(len(url_list) == 0):
                print("      无需替换更新")
                return
            print("      正在更新文件")

            for i in url_list:
                j = list(json_dict.keys())[list(json_dict.values()).index(i)]
                text = text.replace(i,j)
                print("      >>>>>替换图片%s--->%s" % (i,j))
            md_file.seek(0)
            md_file.truncate()
            md_file.write(text)
        print("---该文件完成---")

    def all_files_to_path(self):
        i,j,k= os.walk("../_posts/").__next__()
        files = list()
        for a in range(len(k)):
            files.append(os.path.join(i,k[a]))
        print(files)
        for file in files:
            self.a_file_to_path(file)

if __name__=="__main__":
    o = to_path()
    o.all_files_to_path()