# 第 1 章 安装

在大多数标准中，Flask(`http://flask.pocoo.org/`) 都算是小型框架，小到可以称为“微框架”。

Flask 自开发伊始就被设计为可扩展的框架，它具有一个包含基本服务的强健核心，其他功能则可通过扩展实现。

Flask 有两个主要依赖：路由、调试和 Web 服务器网关接口(Web Server Gateway Interface，WSGI) 子系统由 Werkzeug(http://werkzeug.pocoo.org/) 提供；模板系统由 Jinja2(http://jinja.pocoo.org/)提供。

Flask 并不原生支持数据库访问、Web 表单验证和用户认证等高级功能。

## 1.1 使用虚拟环境

使用虚拟环境还有个好处，那就是不需要管理员权限。

虚拟环境使用第三方实用工具 virtualenv 创建。输入以下命令可以检查系统是否安装了 virtualenv：

```shell
virtualenv --version
```

>   Python 3.3 通过 venv 模块原生支持虚拟环境,命令为pyvenv。pyvenv可以替 代virtualenv。不过要注意,在Python 3.3中使用pyvenv命令创建的虚拟环 境不包含 pip,你需要进行手动安装。Python 3.4 改进了这一缺陷,pyvenv 完 全可以代替 virtualenv。

按照惯例，一般虚拟环境会被命名为 venv：

```shell
git clone https://github.com/miguelgrinberg/flasky.git
cd flasky
git checkout 1a
virtualenv venv
```

在使用这个虚拟环境之前，你需要先将其“激活”。如果你使用 bash 命令行(Linux 和 Mac OS X 用户)，可以通过下面的命令激活这个虚拟环境：

```shell
source venv/bin/activate
```

如果使用微软 Windows 系统，激活命令是：

```shell
venv\Scripts\activate
```

虚拟环境被激活后，其中 Python 解释器的路径就被添加进 PATH 中，但这种改变不是永久性的，它只会影响当前的命令行会话。激活虚拟环境的命令会修改命令行提示符，加入环境名：

```shell
(venv) $
```

## 1.2 使用 pip 安装 Python 包

激活虚拟环境后，`pip` 所在的路径会被添加进 PATH。