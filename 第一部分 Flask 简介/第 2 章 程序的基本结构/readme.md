# 第 2 章 程序的基本结构

## 2.1 初始化

所有 Flask 程序都必须创建一个程序实例。Web 服务器使用一种名为 Web 服务器网关接口 (Web Server Gateway Interface，WSGI) 的协议，把接收自客户端的所有请求都转交给这个对象处理。程序实例是 Flask 类的对象，经常使用下述代码创建：

```python
from flask import Flask
app = Flask(__name__)
```

Flask 类的构造函数只有一个必须指定的参数，即程序主模块或包的名字。在大多数程序中，Python 的 `__name__` 变量就是所需的值。

>   Flask 用这个参数决定程序的根目录，以便稍后能够找到相对于程序根目录的资源文件位置。

## 2.2 路由和视图函数

客户端（例如 Web 浏览器）把请求发送给 Web 服务器，Web 服务器再把请求发送给 Flask 程序实例。程序实例需要知道对每个 URL 请求运行哪些代码，所以保存了一个 URL 到 Python 函数的映射关系。处理 URL 和函数之间关系的程序称为路由。

在 Flask 程序中定义路由的最简便方式，是使用程序实例提供的 `app.route` 修饰器，把修饰的函数注册为路由。

```python
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'
```

>   在 Python 代码中嵌入响应字符串会导致代码难以维护，此处这么做只是为了介绍响应的概念。

下例定义的路由中就有一部分是动态名字：

```python
@app.route('/user/<name>')
def user(name):
	return '<h1>Hello, %s!</h1>' % name
```

路由中的动态部分默认使用字符串，不过也可使用类型定义。例如，路由 `/user/<int:id>` 只会匹配动态片段 id 为整数的 URL。Flask 支持在路由中使用 int、float 和 path 类型。 path 类型也是字符串，但不把斜线视作分隔符，而将其当作动态片段的一部分。

## 2.3 启动服务器

程序实例用 run 方法启动 Flask 集成的开发 Web 服务器：

```python
if __name__ == '__main__':
    app.run(debug=True)
```

服务器启动后，会进入轮询，等待并处理请求。

>   Flask 提供的 Web 服务器不适合在生产环境中使用。

## 2.4 一个完整的程序

## 2.5 请求-响应循环

### 2.5.1 程序和请求上下文

为了避免大量可有可无的参数把视图函数弄得一团糟，Flask 使用上下文临时把某些对象变为全局可访问。有了上下文，就可以写出下面的视图函数：

```python
from flask import request
@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent
```

注意在这个视图函数中我们如何把 request 当作全局变量使用。事实上，request 不可能是全局变量。试想，在多线程服务器中，多个线程同时处理不同客户端发送的不同请求时，每个线程看到的 request 对象必然不同。Flask 使用上下文让特定的变量在一个线程中全局可访问，与此同时却不会干扰其他线程。

在 Flask 中有两种上下文：程序上下文和请求上下文。表 2-1 列出了这两种上下文提供的变量。

| 变量名           | 上下文   | 说明                          |
| ------------- | ----- | --------------------------- |
| `current_app` | 程序上下文 | 当前激活程序的程序实例                 |
| `g`           | 程序上下文 | 处理请求时用作临时存储的对象。每次请求都会重设这个变量 |
| `request`     | 请求上下文 | 请求对象，封装了客户端发出的 HTTP 请求中的内容  |
| `session`     | 请求上下文 | 用户对象，用于存储请求之间需要“记住”的值的词典    |

Flask 在分发请求之前激活(或推送)程序和请求上下文，请求处理完成后再将其删除。程序上下文被推送后，就可以在线程中使用 `current_app` 和 g 变量。类似地，请求上下文被推送后，就可以使用 request 和 session 变量。如果使用这些变量时我们没有激活程序上下文或请求上下文，就会导致错误。

下面这个 Python shell 会话演示了程序上下文的使用方法：

```python
>>> from hello import app
>>> from flask import current_app
>>> current_app.name
Traceback (most recent call last):
    ...
RuntimeError: working outside of application context
>>> app_ctx = app.app_context()
>>> app_ctx.push()
>>> current_app.name
'hello'
>>> app_ctx.pop()
```

在这个例子中，没激活程序上下文之前就调用 `current_app.name` 会导致错误，但推送完上下文之后就可以调用了。注意，在程序实例上调用 `app.app_context()` 可获得一个程序上下文。

### 2.5.2 请求调度

Flask 使用 `app.route` 修饰器或者非修饰器形式的 `app.add_url_rule()` 生成映射。

要想查看 Flask 程序中的 URL 映射是什么样子，我们可以在 Python shell 中检查为 `hello.py` 生成的映射。测试之前，请确保你激活了虚拟环境：

```python
(venv) $ python
>>> from hello import app
>>> app.url_map
     Map([<Rule '/' (HEAD, OPTIONS, GET) -> index>,
<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>, <Rule '/user/<name>' (HEAD, OPTIONS, GET) -> user>])
```

`/static/<filename>` 路由是 Flask 添加的特殊路由，用于访问静态文件。

URL 映射中的 HEAD、Options、GET 是请求方法，由路由进行处理。Flask 为每个路由都指定了请求方法，这样不同的请求方法发送到相同的 URL 上时，会使用不同的视图函数进行处理。HEAD 和 OPTIONS 方法由 Flask 自动处理。

### 2.5.3 请求钩子

有时在处理请求之前或之后执行代码会很有用。例如，在请求开始时，我们可能需要创建数据库连接或者认证发起请求的用户。为了避免在每个视图函数中都使用重复的代码，Flask 提供了注册通用函数的功能，注册的函数可在请求被分发到视图函数之前或之后调用。

请求钩子使用修饰器实现。Flask 支持以下 4 种钩子。

```shell
• before_first_request：注册一个函数，在处理第一个请求之前运行。
• before_request：注册一个函数，在每次请求之前运行。
• after_request：注册一个函数，如果没有未处理的异常抛出，在每次请求之后运行。
• teardown_request：注册一个函数，即使有未处理的异常抛出，也在每次请求之后运行。
```

在请求钩子函数和视图函数之间共享数据一般使用上下文全局变量 g。

### 2.5.4 响应

HTTP 响应中一个很重要的部分是状态码，Flask 默认设为 200，这个代码表明请求已经被成功处理。

例如，下述视图函数返回一个 400 状态码，表示请求无效：

```python
@app.route('/')
def index():
    return '<h1>Bad Request</h1>', 400
```

视图函数返回的响应还可接受第三个参数，这是一个由首部(header)组成的字典，可以添加到 HTTP 响应中。

Flask 视图函数还可以返回 Response 对象。`make_response()` 函数可接受 1 个、2 个或 3 个参数(和视图函数的返回值一样)，并返回一个 Response 对象。

```python
from flask import make_response
@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response
```

有一种名为重定向的特殊响应类型。这种响应没有页面文档，只告诉浏览器一个新地址用以加载新页面。重定向经常在 Web 表单中使用。

重定向经常使用 302 状态码表示，指向的地址由 Location 首部提供。重定向响应可以使用 3 个值形式的返回值生成，也可在 Response 对象中设定。不过，由于使用频繁，Flask 提供了 `redirect()` 辅助函数，用于生成这种响应：

```python
from flask import redirect
@app.route('/')
def index():
	return redirect('http://www.example.com')
```

还有一种特殊的响应由 abort 函数生成，用于处理错误。在下面这个例子中，如果 URL 中动态参数 id 对应的用户不存在，就返回状态码 404：

```python
from flask import abort
@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
		abort(404)
	return '<h1>Hello, %s</h1>' % user.name
```

注意，abort 不会把控制权交还给调用它的函数，而是抛出异常把控制权交给 Web 服务器。

## 2.6 Flask 扩展

### 使用 `Flask-Script` 支持命令行选项

Flask 的开发 Web 服务器支持很多启动设置选项，但只能在脚本中作为参数传给 `app.run()` 函数。这种方式并不十分方便，传递设置选项的理想方式是使用命令行参数。

Flask-Script 是一个 Flask 扩展，为 Flask 程序添加了一个命令行解析器。Flask-Script 自带 了一组常用选项，而且还支持自定义命令。

```python
from flask.ext.script import Manager
manager = Manager(app)
# ...
if __name__ == '__main__':
    manager.run()
```

专为 Flask 开发的扩展都暴漏在 `flask.ext` 命名空间下。Flask-Script 输出了一个名为 Manager 的类，可从 `flask.ext.script` 中引入。

运行 `python hello.py runserver` 将以调试模式启动 Web 服务器，但是我们还有很多选项可用：

```python
(venv) wtchdeMacBook-Pro:book_flasky L1n$ python hello.py runserver --help
usage: hello.py runserver [-?] [-h HOST] [-p PORT] [--threaded]
                          [--processes PROCESSES] [--passthrough-errors] [-d]
                          [-D] [-r] [-R] [--ssl-crt SSL_CRT]
                          [--ssl-key SSL_KEY]
```