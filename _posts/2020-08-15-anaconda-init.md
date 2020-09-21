---
title: Anaconda+vscode环境搭建
layout: post
tags:
- Python
description: Anaconda+vscode基础环境搭建
---

记录Anaconda的安装过程和基础命令，并通过vscode调用Anaconda创建的虚拟环境。

在新版的Anaconda中官方已经不建议配置环境变量了，网上教程过于老旧，因此在安装完成后记录一下。
<!-- more -->

# 1. 下载

如果不方便翻墙的，可以到清华大学的[镜像站](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)下载，除了选择下安装安装位置，其他一路点下去即可

按照镜像站的说明，在指定位置新建配置文件并添加国内镜像源到配置文件中

文中将以本文当前最新版本`Anaconda3-2020.07-Windows-x86_64`为例进行说明


# 2. Anaconda

## 2.1. 所有程序

安装后的window开始菜单栏（左下角的那个）所有应用：
![](https://source.acexy.cn/view/XSuPIdz)

> 后面多了个(anaconda3)的快捷方式和没有的是同一个，只是名称不同而已

- Anaconda Navigator：用于管理工具包和环境的图形用户界面，后续涉及的众多管理命令也可以在 Navigator 中手工实现。
- Anaconda Prompt (anaconda3)：就是一个以特定方式打开的cmd的链接。后面会仔细说明
- Anaconda Powershell Prompt (anaconda3)：以特定方式打开的shell的链接。
- Jupyter Notebook：基于web的交互式计算环境，可以编辑易于人们阅读的文档，用于展示数据分析的过程。
- Spyder (anaconda3)：一个使用Python语言、跨平台的、科学运算集成开发环境。
- Reset Spyder Settings (anaconda3)：重置spyder设置

> 一开始推荐先学习命令，比较简单容易上手

## 2.2. 为何不用设置环境变量

查看Anaconda Prompt (anaconda3)的目标:
![](https://source.acexy.cn/view/XSuPIqA)

- 目标代码： `%windir%\System32\cmd.exe "/K" D:\learn\anaconda3\Scripts\activate.bat D:\learn\anaconda3`
- 分析
    - %windir%\System32\cmd.exe为cmd所在位置
        - %windir%：指向Windows目录，一般为C:\Windows
    - cmd /k dir 是执行完dir命令后不关闭命令窗口。 
        > 保证之后窗口不会闪现
    - D:\learn\anaconda3\Scripts\activate.bat：为点击该快捷方式时执行的命令
    - D:\learn\anaconda3：传入参数，代表命令anaconda命令所在目录

- 演示
    > ![](https://source.acexy.cn/view/XSuPI2c)
    - 右侧为执行Anaconda Promp
    - 左侧为普通cmd，无法查询到python和pip所在位置
        - 但执行Anaconda Prompt快捷方式中的命令后会和Anaconda Prompt相同

> 结论：也就是说，Anaconda通过Anaconda Prompt (anaconda3)中的代码，设置了程序查找路径，从而代替了环境变量的设置。

## 2.3. 虚拟环境

### 2.3.1. 创建环境：

所谓虚拟环境，就是一个个独立的python环境，从文件上看就是一个个python安装后的文件夹，但因为并没有配置环境变量，所以他们只是文件。
一开始会在一个`base`环境，通过下面一条命令创建一个新的环境
```
# 创建新的名为 learn_python 的版本为3.8.5的python环境
conda create -n learn_python python=3.8.5

# 跳转到新的环境：
activate learn_python
```

### 2.3.2. 目录结构

**python目录结构**

![](https://source.acexy.cn/view/XSuPJBx)

- DLLs： Python 自己使用的动态库
- Doc： 自带的 Python 使用说明文档（如果上面安装时不选择，应该会没有，这个没具体试过）
- include： 包含共享目录
- Lib： 库文件，放自定义模块和第三方包
- libs： 编译生成的Python 自己使用的静态库
- Scripts： 各种包/模块对应的可执行程序。安装时如果选择了pip。那么pip的可执行程序就在此！
- tcl： 桌面编程包

设置python环境变量一般都会这只python.exe所在目录以及python下的script(存放pip包安装工具，autopep8格式化工具，pylint代码检查工具等)

**虚拟环境目录结构**

`安装目录/envs`下存放所有虚拟环境

每个虚拟环境都和python目录结构类似。
> 自己翻到目录那里看看

### 2.3.3. vscode设置虚拟环境

#### 2.3.3.1. 解析器

1. 添加python插件
2. 点击右下角选择解析器(vscode会自动查找)
3. 选择工作空间以及对应解析器
![](https://source.acexy.cn/view/XSuPJNp)

此时，ctrl+shift+` 新建终端，会发现自动进入虚拟环境。
程序执行时也会在指定虚拟环境中执行。
![](https://source.acexy.cn/view/XSuPJru)


#### 2.3.3.2. 代码检查+格式化

> 推荐直接使用base环境下的程序，避免因删除虚拟环境而重新配置

setting.json中添加：
```json
/* !!! 要写自己的目录 !!!*/
"python.linting.pylintPath": "安装目录\\anaconda3\\Scripts\\pylint.exe",
"python.formatting.autopep8Path": "安装目录\\anaconda3\\Scripts\\autopep8.exe"
```
# 3. 常用命令

- activate：切换到base环境
- conda create -n learn_python python=3： 创建一个名为learn_python的环境并指定python版本为3(的最新版本)
- conda remove -n learn_python --all： 删除learn_python环境及下属所有包
- activate 环境名：切换虚拟环境
- conda env list：查看虚拟环境列表
- conda install <包名> 或 pip install <包名>： 安装指定包
- conda remove <包名> 或 pip uninstall <包名> ： 移除指定包
- conda update <包名> ： 更新指定包
- conda list ：列出所有包
- conda env export > environment.yaml ：导出虚拟环境设置
- conda env create -f environment.yaml：通过配置文件创建虚拟环境
- conda clean -p      //删除没有用的包
- conda clean -t      //tar打包
- conda clean -y -all //删除所有的安装包及cache
