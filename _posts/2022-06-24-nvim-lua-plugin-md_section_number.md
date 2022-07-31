---
layout: post
title: "neovim的lua插件编写入门"
description: 对neovim的lua接口，插件结构进行简单说明。
tags:
  - vim
  - lua
---

个人编辑笔记，写博客，写一些代码等已经从 vscode 转移到 nvim 上很久了。  
其中 vscode 有一个为 markdown 标题编号的插件[auto-markdown-toc](https://marketplace.visualstudio.com/items?itemName=huntertran.auto-markdown-toc)用了挺长时间，一般会搭配 chrome 上自带侧边栏的[markdown viewer](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk)插件浏览自己的 markdown 笔记。
但是 vim 上找了许久，也没有找到为标题编号的插件。这两天看了一下 nvim 的接口，用 lua 写了一个插件实现了功能。简单记录一下。

**_:help 与你同在_**

<!-- more -->

# 前言

因为比较习惯 vim 键位，vscode 上一直装着 vim 插件，一开始用得挺舒服得，但用得越久感觉越要命。
主要问题出在 vscode 的 vim 插件上，当然也不排除轻薄本 cpu 太差的原因。

- 在编辑文件时，如果一直按下，松手之后，还能看见光标跑一会儿
  - 可能是在调快了按住键盘后重复输入字符频率导致的
- 在编辑大文件，如 1000+行的 markdown 时，编辑的延迟非常大，光标的移动速度和编辑位置也非常容易和实际操作对不上。
  - 体验异常之差
- 在格式化文件后，使用`u`的时候，vscode 的 vim 插件会一步一步得撤销格式化。
  - 有一次再格式化一行很长的 json 之后，按了一下`u`，等了 5s 以上才撤销好
  - 迫不得已把`u`映射成了 vscode 中的`undo`
- 无法像 vim 一样简单定义一些小功能
  - `json`配置的确比较方便，但是 **找需要的命令太费劲了** ，同时也不敢保证所有命令能满足需求
  - 一个小功能核心代码就几句，搞一个插件不太值得，插件本来就多，再搞就成插件地狱了。

忍受不了，转到了 vim 上，基本满足日常需求。

在 vscode 上需要的的所有功能，都能通过配置 vim 或者添加 vim 插件的方式实现。
同时也通过简单脚本配置的方式，实现了很多 vscode 上想要但是没办法实现的小功能。
唯一一个为 markdown 标题添加编号的功能一直没有找到插件，期间配置了一个使用 vscode 打开当前文件的快捷键凑活着用。
前两天看了看 nvim 的一些 lua api，写了一个插件实现需求。

其实也可以使用 vscode 插件 auto-markdown-toc 的代码改成一个命令行程序，
不过单纯一个小功能还需要 node 依赖就有大材小用，就干脆用 lua 代码自己手动实现了。

**注意：本文中的 vim 指的是 nvim，版本为 0.7**

# vim 的插件加载机制

## runtimepath

**插件其实是一个当 Vim 启动的时候能被自动执行的脚本** 。

vim 启动时，会自动寻找`runtimepath`下的脚本进行加载。首先对`runtimepath`的组成进行说明。

vim 和 nvim 的插件加载路径并不相同，以 nvim 为例，windows 下默认加载以下路径，并按照顺序执行以下目录中的脚本：

- ~\AppData\Local\nvim
- ~\AppData\Local\nvim-data\site
- [install path]\share\nvim\runtime
- [install path]\lib\nvim
- ~\AppData\Local\nvim-data\site\after
- ~\AppData\Local\nvim\after

可以通过以下命令查询`runtimepath`：

```vim
:echo &runtimepath
" 或者
:set runtimepath
```

## 脚本加载

- 查看 vim 加载的脚本

  ```vim
  :scriptnames
  ```

vim 支持把插件分割为多个文件。
vim 加载的脚本除了`.vimrc`(vim)或者`init.vim`，以及配置文件中 source 与 runtime 的脚本外，
还会从`runtimepath`的所有目录中自动搜索并加载特定子文件夹下的脚本。

需要搜索执行的所有子文件夹可以通过`help runtimepath`查看，这里只对常用的几个进行说明：

- colors/
  - 会查找该文件夹下的所有 vim 文件并执行，每个 vim 文件中应该包括生成一个配色方案的所有命令。
- plugin/
  - 在每次 vim 启动的时候执行。存放全局插件(`:help plugin`)脚本，不受编辑的文件类型影响。
- ftplugin/
  - 仅用于特定类型的文件，且仅对当前缓冲区有效。
  - 当 Vim 把一个缓冲区的 filetype 设置成某个值时，会执行 ftplugin/下对应的文件。
  - 根据文件类型吧脚本设置分布到不同文件中。
- indent/
  - 类似 ftplugin 下的文件，也只加载类型对应的脚本文件，且仅对当前缓冲区有效。
  - 该文件夹下的文件用来设置文件类型相关的缩进。
- compiler/
  - 只加载类型对应的脚本文件。
  - 定义如何运行各种编译器或格式化工具，以及如何解析其输出。
  - 可以在多个 ftplugins 之间共享。且不会自动执行，必须通过 :compiler 调用。
- after/
  - 与`plugin`类似，同样也是全局加载
  - 但会在`plugin`加载了之后加载，往往用来覆盖一些默认值。较少用到
- autoload/
  - 延迟加载的一种方式，仅仅在调用指定方法时会进行自动加载。
  - 比如脚本中调用`somefile#hello()`，vim 会加载 runtimepath 下的`autoload/somefile`文件，然后调用其中定义的`somefile#hello()`方法
- pack/
  - 放置需要加载的软件包
  - 内置插件加载方式中进行说明。
- doc/
  - 存放文档

有一点需要注意：  
每个文件夹中脚本的内容并没有强制规定。
在`ftplugin`中写全局相关的命令，或者在`indent`中写与`indent`无关的命令都没有问题，但是会让可读性变低，
最好按照功能的实现将代码放到对应的脚本目录下。

## vim 插件的加载安装方式

### 直接添加脚本文件

把脚本放到`runtimepath`中指定文件夹的目录中去。

在仅仅添加一两个脚本的时候没什么问题，但是如果使用别人发布的脚本，需要逐一并且正确的得放置每一个脚本，
并且难以对插件进行更新以及无法处理不同插件的同名文件。

### 修改 runtimepath

在配置文件中，将插件目录添加到`runtimepath`中：

```vim
let &runtimepath = &runtimepaht .. "," .. "<path_to_plugin>"
```

只要插件按照 vim 指定的之前说明的文件夹路径放置脚本呢，就会自动加载指定脚本。

### 使用插件管理器插件

插件管理器的本质也是修改`runtimepath`，只不过往往在此基础上提供了自动 clone，更新等功能。。

最早的插件管理器如`vim-pathogen`提供了较为简单的`runtimepath`注入功能，只要将插件 clone 到指定目录下即可。

当前(2022-06)使用较多的 vimscript 实现的插件管理器为`vim-plug`，而使用较多的 lua 实现的的插件管理器为`packer.nvim`，
两者都可以加载 vimscript 实现的插件以及 lua 实现的插件。可以根据自己喜好进行选择。

个人使用的是`vim-plug`，使用 autocmd 的方式，将每个的插件安装命令和插件的配置脚本放到一个脚本文件中，
再通过自定义命令`LoadScript`和`LoadLua`的方式指定要在加载的插件。

详情可以参考个人的[`dotfiles`](https://github.com/whitestarrain/dotfiles)。

个人不清楚`packer.nvim`是否可以实现这种效果(`startup`是否可以调用多次)，并且有些 vim 实现的插件用 lua 配置起来也不是很方便，
也就还没有转到`packer.nvim`，有时间再折腾。

### vim 内置插件包管理方法

和之前提到的插件管理器类似，只不过需要把插件放到`<runtimepath>/pack/`的子路径下。

因为使用较少，此处不进行详细说明，有兴趣的可以参考这篇文章自行配置:[vim8 原生内置(naive)插件安装](https://blog.csdn.net/qq_27825451/article/details/100557133)

## nvim 中的 lua 脚本

### init.lua

可能自动加载的 lua 脚本有两种，一种是`init.lua`，用来代替`init.vim`，且无法与`init.vim`共同存在(`:help init.lua`)。

`init.lua` 文件是完全可选的。Neovim 仍然支持从 init.vim 加载配置，且 Neovim 的一些功能还没有 100% 暴露给 Lua 模块部分。

### lua 模块

在 lua 脚本中，使用`require('module)`会从`runtimepath/lua/`下寻找 lua 脚本(`help lua-require`)。可以看作 lua 版本的`autoload`。

同时，与 vimscript 很像，前面提到的`plugin`,`indent`等特殊目录下的 lua 脚本也会被自动加载，只不过 vim 脚本会先于 lua 脚本加载。

### 模块下的 init.lua

在文件夹下如果包括`init.lua`的话，可以直接引用该文件夹而不必指定该文件的名称，
这是 nvim 中加载 lua 的特性，一般的 lua 解析器并没有这种模块加载方式。

插件[`nvim-tree.nvim`](https://github.com/kyazdani42/nvim-tree.lua)中就有使用这种方式加载模块。

# vim 插件的 lua 开发环境

windows 上终端开发环境的配置其实以前就开始写了，写了 1/4 之后时间原因就一直放着，近期尽量写完放上来。

这里只对 lua 开发环境搭建进行一下简单说明。

![2022-06-24-nvim-lua-plugin-md_section_number](https://source.acexy.cn/view/YJTNnqQ)

- 导航栏：tagbar
- 文件浏览：nvim-tree
- 内部终端：[floaterm](https://github.com/voldikss/vim-floaterm)
- lua lsp:[sumneko_lua](https://github.com/sumneko/lua-language-server)
- nvim 内置 lsp api 配置：[nivm-lspconfig](https://github.com/neovim/nvim-lspconfig)
- nvim 自动补全：[nvim-cmp](https://github.com/hrsh7th/nvim-cmp)
- nvim 内置 lua api 补全：[lua-dev.nvim](https://github.com/folke/lua-dev.nvim)
  - lua-dev 是对 sumneko_lua 进行了包装，把 nvim 的 api 信息提供给 lsp
  - 也可以使用[cmp-nvim-lua](https://github.com/hrsh7th/cmp-nvim-lua)，但改插件只会提示字段名称，并不会有文档提示以及 hover 提示等。
- 实时脚本测试执行插件：[nvim-luapad](https://github.com/rafcamlet/nvim-luapad)
  - 实时执行输入的 lua 脚本(相当于文件修改时便执行一次 luafile)，并将执行结果显示在编辑界面上
  - 提供新开`luapad`，以及 toggle luapad 等 api 进行使用。
  - 测试一些语法或 api，以及调试一些方法的时候特别好用。

  ![](https://source.acexy.cn/view/YJTNoSS)

  ```lua
  -- lua脚本中添加改句，确保luapad可以查找到当前文件夹下的模块。
  package.path = package.path .. ";./?.lua" .. ";./lua/?.lua"
  ```

- 插件测试
  - vim 中执行该行保证可以查找到当前文件夹下的 lua 模块

    ```vim
    let &runtimepath.="," . getcwd()
    ```
  - `require(module).function()`调用暴露出来的接口进行测试

# vim 的常用 lua 接口说明

neovim 暴露了一个全局变量`vim`来作为 lua 调用 vim api 的入口。按照`help lua.txt`进行划分，一些常用的函数和子模块如下：

- `:h lua-stdlib`:一些 lua 的“标准库”，包括一些函数和子模块
  - `vim.regex`: 在 Lua 中使用 Vim 正则表达式
  - `vim.loop`: Neovim 的 event lopp 模块（使用 LibUV)
  - `vim.api`: 暴露 vim 的 API(:h API) 的模块（别的远程调用也是调用同样的 API)。包括获取与修改 buffer 内容，添加，删除高亮等。
  - `vim.fn`: 暴露一些 vim 的内建函数。(:h eval.txt)
- `:h lua-vim`：主要提供一些通用 lua 的方法，比如`startwith`,`deepcopy`,`list_slice`等。
  - `vim.inspect`: 把 Lua 对象以更易读的方式打印（在打印 Lua table 时会很有用）
- `:h lua-ui`
  - `vim.ui`: 可被插件覆写的 UI 相关函数
- `:h lsp-util`
  - `vim.lsp`: 控制内置 LSP 客户端的模块
- `:h treesitter.txt`
  - `vim.treesitter`: 暴露 tree-sitter 库中一些实用函数的模块
- `:h lua-uri`: 提供一些 uri 的转换操作，比如`buf编号<->uri`,`文件路径<->uri`等
  - `vim.uri_xxxxxxxx`
- `:h lua-filetype`
  - `vim.filetype.match()`
  - `vim.filetype.add()`

配置好开发环境后，可以根据代码提示和文档熟悉一下端口。在开发过程中也可以通过`help`学习不熟悉的接口

# 插件实现

## lua 的面向对象

lua 的面向对象是通过 lua 中的 table，functino 以及 table 的`metatable`模拟出来的

table 中可以设置 k-v 作为成员变量，设置 function 作为方法。
然后使用一个 table 作为创建其他 table 的模板，也就是类。

```lua
-- 定义Stack '类'
local Stack = {}

-- 为了用作metatable
Stack.__index = Stack
-- 设置Stack类的成员
Stack.elements = {}

-- 设置new方法，根据Stack这张表创建新的表
function Stack:new(elements, attrs)
  attrs = attrs or {}
  attrs.elements = elements or {}
  return setmetatable(attrs, self)
end
-- 设置各种成员方法。
function Stack:push(element)
  table.insert(self.elements, self:length() + 1, element)
end
function Stack:length()
  return #self.elements
end
function Stack:pop()
  if self:is_empty() then
    return nil
  end
  local element = self.elements[self:length()]
  table.remove(self.elements, self:length())
  return element
end
function Stack:is_empty()
  return self:length() == 0
end
function Stack:peek()
  return self.elements[self:length()]
end

return Stack
```

有一处需要注意，下面的代码通过 metatable 的方式，保证 new 出来的新 table，调用方法时，可以从充当类的表 Stack 中获得到方法。

```lua
Stack.__index = Stack
function Stack:new(elements, attrs)
  attrs = attrs or {}
  attrs.elements = elements or {}
  return setmetatable(attrs, self)
end

-- 等价于

function Stack:new(elements, attrs)
  attrs = attrs or {}
  attrs.elements = elements or {}
  return setmetatable(attrs,{__index = Stack})
end
```

## 项目结构

```bash

├───doc
├───ftdetect # 文件类型设置
│       markdown.vim
├───ftplugin # commad设置
│       markdown.vim
└───lua # 插件实现
    │   md_section_number.lua #主体逻辑
    │
    └───md_section_number
        │   parser.lua # 标题解析
        │   replacer.lua # 标题添加编号处理
        │
        └───common
                stack.lua # stack 数据结构实现
                utils.lua # 工具方法
```

## 核心逻辑

### parser

首先需要找到 markdown 标题，lua 中没有原生支持正则表达式，因此这里使用 lua 的模式匹配。

```lua
M.heading_pattern = "^#+ "
local function judgeHeadingLine(line)
  local s, e = string.find(line, M.heading_pattern)
  local length = s and e - s or 0
  return nil ~= s, length
end
```

同时需要跳过注释以及代码块中的符合标题模式的行。

````lua
-- 定义需要忽略的 包围pair
M.ignore_pairs = {
  { "```", "```" },
  { "\\~\\~\\~", "\\~\\~\\~" },
  { "<!--", "-->" },
}
````

```lua
for line_number, line in ipairs(all_lines) do
  for pair_index, pair in ipairs(M.ignore_pairs) do
    local start_pair_location = vim.fn.match(line, pair[1])
    local end_pair_location = vim.fn.match(line, pair[2], start_pair_location + 1)
    -- 使用栈检查是否在pair包围之外
    if stack:is_empty() then
      -- pair出栈或入栈
    else
      -- pair出栈或入栈
    end
    end
  end
```

### replacer

为标题添加标号，

```lua
--[[
heading_line = {
  {
    1,            -- line number
    "# heading"   -- heading content
    1,            -- heading level
  }
}
]]
for i = 1, #heading_lines do
  local level = heading_lines[i][3]
  -- 第一个heading跳过直接跳过下面的处理
  if i == 1 then
    level_depth[level] = 1 -- level_depth 记录个等级heading的编号
    goto continue
  end

  -- nil值初始化为0
  if not level_depth[level] then
    level_depth[level] = 0
  end
  -- 当heading级别变小时，level 递增
  --[[
    如: # 1
        ## 1.1
        ## 1.2
        # 2
    1.2 -> 2 时，级别变小，在原来的基础(1)上递增得到2
  ]]
  if heading_lines[i][3] < heading_lines[i - 1][3] then
    level_depth[level] = level_depth[level] + 1
  end
  -- 当heading级别不变时，level递增
  if heading_lines[i][3] == heading_lines[i - 1][3] then
    level_depth[level] = level_depth[level] + 1
  end
  -- 当heading级别变大，中间的level depth设为0
  --[[
    如: # 1
        ## 1.2
        ##### 1.2.0.0.5
  ]]
  if heading_lines[i][3] > heading_lines[i - 1][3] then
    for inner_level = heading_lines[i - 1][3] + 1, heading_lines[i][3] - 1 do
      level_depth[inner_level] = 0
    end
    level_depth[level] = 1
  end

  ::continue::
  local heading_number = ""
  for j = 1, level do
    heading_number = heading_number .. (level_depth[j] or 0) .. "."
  end
  table.insert(heading_lines[i], heading_number)
end
```

### 插件配置

提供 setup 方法进行插件的自定义配置。

```lua
-- md_section_number.lua
function M.setup(conf)
  local opts = merge_options(conf)
  parser.setup(opts)
  replacer.setup(opts)
end
```

默认配置为：

```lua
require("md_section_number").setup({
  max_level = 4, -- 只为heading level小于等于4的标题添加编号。
  ignore_pairs = {
    { "```", "```" },
    { "\\~\\~\\~", "\\~\\~\\~" },
    { "<!--", "-->" },
  },
})
```

设置文件 filetype：

```vim
" ftdetect/markdown.vim
au BufRead,BufNewFile *.{md,mdown,mkd,mkdn,markdown,mdwn,mdx} set filetype=markdown
```

在 markdown 文件下设置 command 方便调用：

```vim
" ftplugin/markdown.vim
if exists("b:md_section_number")
  finish
endif

command! -buffer -range=% MDUpdateNumber lua require('md_section_number').update_heading_number()
command! -buffer -range=% MDClearNumber lua require('md_section_number').clear_heading_number()

let b:md_section_number = 1
```

## 测试

- 单独函数测试:使用[nvim-luapad](https://github.com/rafcamlet/nvim-luapad)

- 整体测试

  ```vim
  " 在插件开发目录下打开一个markdown文件后，
  " 执行
  let &runtimepath.="," . getcwd()
  lua print(require("md_section_number").update_heading_number())
  ```

# 参考资料

- [详谈 Vim 的配置层次结构与插件加载方式](https://blog.csdn.net/qq_27825451/article/details/100518128)
- [vim8 原生内置(naive)插件安装](https://blog.csdn.net/qq_27825451/article/details/100557133)
- [在 neovim 中使用 Lua](https://github.com/glepnir/nvim-lua-guide-zh)
- 《笨方法学 vimscript》
- [How to 'require' an entire directory in Lua?](https://www.reddit.com/r/neovim/comments/reovwj/how_to_require_an_entire_directory_in_lua/)
- [How to write neovim plugins in Lua](https://www.2n.pl/blog/how-to-write-neovim-plugins-in-lua)
