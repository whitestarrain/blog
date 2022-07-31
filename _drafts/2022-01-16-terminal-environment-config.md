---
layout: post
title: "终端环境搭建"
description: "用于编程，笔记，用于摆脱win10资源管理器进行的终端操作环境搭建"
tags:
  - environement

---

用于编程，笔记，用于摆脱win10资源管理器进行的终端操作环境搭建。
周六日的时候抽时间配置的， 大多是时间花在了vim配置的重构和lsp上。
详细配置结果可以看下方的图片展示。

<!-- more -->

# 配置结果

## 效果展示


### vim

- 通过不同配置powershell,不同nvim命令会选择性启动不同的插件

  ![2022-01-16-terminal-environment-2](../images/2022-01-16-terminal-environment-2.png)

- nvim-qt 与 终端nvim 的适配

  ![2022-01-16-terminal-environment-10](../images/2022-01-16-terminal-environment-10.png)

  ![2022-01-16-terminal-environment-11](../images/2022-01-16-terminal-environment-11.png)

- react开发示例

  ![2022-01-16-terminal-environment-3](../images/2022-01-16-terminal-environment-3.png)

  ![2022-01-16-terminal-environment-5](../images/2022-01-16-terminal-environment-5.png)

- latex编辑示例

  - 补全

    ![2022-01-16-terminal-environment-6](../images/2022-01-16-terminal-environment-6.png)
    ![2022-01-16-terminal-environment-8](../images/2022-01-16-terminal-environment-8.png)

  - 目录，snippet

    ![2022-01-16-terminal-environment-7](../images/2022-01-16-terminal-environment-7.png)

  - 实时编译

    ![2022-01-16-terminal-environment-9](../images/2022-01-16-terminal-environment-9.png)

- 其他示例与gif（有时间继续补充示例）
  - float terminal
  - 颜色显示
  - which-key
  - 快捷打开
  - 快捷搜索
  - markdown 剪切板 图片粘贴
  - telescope模糊搜索
  - ...


### terminal

- 总览

  ![2022-01-16-terminal-environment-1](../images/2022-01-16-terminal-environment-1.png)
- z 命令
- fzf
- PSReadline



## dotfiles

[dotfiles](https://github.com/whitestarrain/dotfiles)

# 软件管理--scoop

- [你需要掌握的Scoop技巧和知识](https://zhuanlan.zhihu.com/p/135278662)

## 前置软件

## 其他软件推荐

# 终端配置

## powershell 7 安装

## 美化

### 字体

### oh-my-posh

### 文件图标

## 命令行提示

### fzf

### z

### PSReadLine

## 终端模拟器推荐

### windows terminal

这个没有试，win10版本太低，装不了。

### fluent terminal

### alacritty

- 优点：
  - gui加速，快
- 缺点：
  - win10 1803下，透明效果失效
    > (issue里面作者说太老的windows版本没有测试，可惜我用的就是1803)
  - win10 1803下，vim开启`termguicolors`后，在vim页面滚动时会卡顿
    > 解决方法没找到
  - 没有tab，一个窗口就能开一个页面。win10上面没有类似tmux的软件进行搭配使用

### wezterm(推荐)

- 优点
  - gui加速，快
  - 没有alacritty的缺点
  - 有tab，甚至能分屏
- 缺点
  - <del>wezterm窗口聚焦时，其他两个常用软件：utools和snipaste，使用时偶尔有卡顿情况。但基本不影响使用</del>(nightly版本中修复，2022-03-18)
  - <del>光标下文字颜色显示有一点儿问题</del>(nightly版本中修复，2022-03-18)
   > ![2022-01-16-terminal-environment-config-1](../images/2022-01-16-terminal-environment-config-1.png)

# vim配置

## 重构结构

## 外观配置

## 插件配置

## coc or lsp

## 选择性配置

### vi

### vim

### nvim[lang]

#### C++配置

#### javascript配置

#### go配置

### nvimpower

# 参考资料
