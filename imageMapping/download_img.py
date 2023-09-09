import json
import urllib.request

img_dict = {}
indent = " " * 4

if __name__ == "__main__":
    with open("./mapping.json", "r") as json_file:
        img_dict = json.load(json_file)

    for path, url in img_dict.items():
        file_type = path.split(".")[-1]
        if file_type not in ["jpg", "png", "gif"]:
            continue
        print("start download", path)
        with urllib.request.urlopen(url) as img:
            with open(path, "wb") as img_file:
                print(indent, "start get binary data")
                binary_data = img.read()
                print(indent, "end get binary data")
                img_file.write(binary_data)
                print(indent, "end wirte file")
