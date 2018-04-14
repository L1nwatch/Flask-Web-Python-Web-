# 第 18 章 其他资源

## 18.1 使用集成开发环境

在集成开发环境(Integrated Development Environment,IDE)中开发Flask程序非常方便, 因为代码补全和交互式调试器等功能可以显著提升编程的速度。以下是几个适合进行 Flask 开发的 IDE。

-   PyCharm(http://www.jetbrains.com/pycharm/):JetBrains 开发的商用 IDE,有社区版(免费)和专业版(付费),两个版本都兼容 Flask 程序,可在 Linux、Mac OS X 和 Windows 中使用。
-   PyDev(http://pydev.org/):这是基于Eclipse的开源IDE,可在Linux、Mac OS X和Windows 中使用。
-   Python Tools for Visual Studio(http://pytools.codeplex.com/):这是免费IDE,作为微软Visual Studio 的一个扩展,只能在微软 Windows 中使用。

>   配置 Flask 程序在调试器中启动时,记得为 runserver 命令加入 `--passthrough-errors --no-reload` 选项。第一个选项禁用 Flask 对错误的缓存,这样处理请 求过程中抛出的异常才会传到调试器中。第二个选项禁用重载模块,而这个模 块会搅乱某些调试器。

## 18.2 查找 Flask 扩展

本书中的示例程序用到了很多扩展和包,不过还有很多有用的扩展没有介绍。下面列出了其他一些值得研究的包。

-   Flask-Babel(https://pythonhosted.org/Flask-Babel/):提供国际化和本地化支持。

-   FLask-RESTful(http://flask-restful.readthedocs.org/en/latest/):开发REST API的工具。

-   Celery(http://docs.celeryproject.org/en/latest/):处理后台作业的任务队列。

-   Frozen-Flask(https://pythonhosted.org/Frozen-Flask/):把 Flask 程序转换成静态网站。

-   Flask-DebugToolbar(https://github.com/mgood/flask-debugtoolbar):在浏览器中使用的

    调试工具。

-   Flask-Assets(https://github.com/miracle2k/flask-assets):用于合并、压缩、编译 CSS 和

    JavaScript 静态资源文件。

-   Flask-OAuth(http://pythonhosted.org/Flask-OAuth/):使用OAuth服务进行认证。

-   Flask-OpenID(http://pythonhosted.org/Flask-OpenID/):使用 OpenID 服务进行认证。

-   Flask-WhooshAlchemy(https://pythonhosted.org/Flask-WhooshAlchemy/): 使 用 Whoosh

    (http://pythonhosted.org/Whoosh/)实现 Flask-SQLAlchemy 模型的全文搜索。

-   Flask-KVsession(http://flask-kvsession.readthedocs.org/en/latest/):使用服务器端存储实

    现的另一种用户会话。