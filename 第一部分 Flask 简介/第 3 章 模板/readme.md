# 第 3 章 模板

把业务逻辑和表现逻辑混在一起会导致代码难以理解和维护。

把表现逻辑移到模板中能够提升程序的可维护性。

模板是一个包含响应文本的文件，其中包含用占位变量表示的动态部分，其具体值只在请求的上下文中才能知道。使用真实值替换变量，再返回最终得到的响应字符串，这一过程称为渲染。为了渲染模板，Flask 使用了一个名为 Jinja2 的强大模板引擎。

## 3.1 Jinja2 模板引擎

形式最简单的 Jinja2 模板就是一个包含响应文本的文件。

视图函数 user() 返回的响应中包含一个使用变量表示的动态部分。

```python
<h1>Hello, {{ name }}!</h1>
```

### 3.1.1 渲染模板

默认情况下，Flask 在程序文件夹中的 templates 子文件夹中寻找模板。

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
```

Flask 提供的 `render_template` 函数把 Jinja2 模板引擎集成到了程序中。`render_template` 函数的第一个参数是模板的文件名。

### 3.1.2 变量

Jinja2 能识别所有类型的变量，甚至是一些复杂的类型，例如列表、字典和对象。在模板中使用变量的一些示例如下：

```html
<p>A value from a dictionary: {{ mydict['key'] }}.</p>
<p>A value from a list: {{ mylist[3] }}.</p>
<p>A value from a list, with a variable index: {{ mylist[myintvar] }}.</p>
<p>A value from an object's method: {{ myobj.somemethod() }}.</p>
```

可以使用过滤器修改变量，过滤器名添加在变量名之后，中间使用竖线分隔。

| 过滤器名       | 说明                    |
| ---------- | --------------------- |
| safe       | 渲染值时不转义               |
| capitalize | 把值的首字母转换成大写，其他字母转换成小写 |
| lower      | 把值转换成小写形式             |
| upper      | 把值转换成大写形式             |
| title      | 把值中每个单词的首字母都转换成大写     |
| trim       | 把值的首尾空格去掉             |
| striptags  | 渲染之前把值中所有的 HTML 标签都删掉 |

safe 过滤器值得特别说明一下。默认情况下，出于安全考虑，Jinja2 会转义所有变量。例如，如果一个变量的值为 `'<h1>Hello</h1>'`，Jinja2 会将其渲染成 `'<h1>Hello</ h1>'`，浏览器能显示这个 h1 元素，但不会进行解释。很多情况下需要显示变量中存储的 HTML 代码，这时就可使用 safe 过滤器。

>   千万别在不可信的值上使用 safe 过滤器，例如用户在表单中输入的文本。

完整的过滤器列表可在 Jinja2 文档(http://jinja.pocoo.org/docs/templates/#builtin-filters)中查看。

### 3.1.3 控制结构

Jinja2 提供了多种控制结构，可用来改变模板的渲染流程。

```python
{% if user %}
	Hello, {{ user }}!
{% else %}
	Hello, Stranger!
{% endif %}
```

另一种常见需求是在模板中渲染一组元素。下例展示了如何使用 for 循环实现这一需求：

```python
<ul>
	{% for comment in comments %}
		<li>{{ comment }}</li>
    {% endfor %}
</ul>
```

Jinja2 还支持宏。宏类似于 Python 代码中的函数。例如：

```python
{% macro render_comment(comment) %}
	<li>{{ comment }}</li>
{% endmacro %}
<ul>
	{% for comment in comments %}
		{{ render_comment(comment) }}
    {% endfor %}
</ul>
```

为了重复使用宏，我们可以将其保存在单独的文件中，然后在需要使用的模板中导入：

```python
{% import 'macros.html' as macros %}
<ul>
	{% for comment in comments %}
		{{ macros.render_comment(comment) }}
    {% endfor %}
</ul>
```

需要在多处重复使用的模板代码片段可以写入单独的文件，再包含在所有模板中，以避免重复：

```python
{% include 'common.html' %}
```

另一种重复使用代码的强大方式是模板继承，它类似于 Python 代码中的类继承。首先，创建一个名为 `base.html` 的基模板：

```html
<html>
     <head>
		{% block head %}
			<title>{% block title %}{% endblock %} - My Application</title> 
        {% endblock %}
     </head>
     <body>
		{% block body %}
		{% endblock %}
  	 </body>
</html>
```

block 标签定义的元素可在衍生模板中修改。在本例中，我们定义了名为 head、title 和 body 的块。注意，title 包含在 head 中。下面这个示例是基模板的衍生模板：

```python
{% extends "base.html" %}
{% block title %}Index{% endblock %}
{% block head %}
	{{ super() }}
	<style>
	</style>
{% endblock %}
{% block body %}
<h1>Hello, World!</h1>
{% endblock %}
```

extends 指令声明这个模板衍生自 `base.html`。在 extends 指令之后，基模板中的 3 个块被重新定义，模板引擎会将其插入适当的位置。注意新定义的 head 块，在基模板中其内容不是空的，所以使用 `super()` 获取原来的内容。

## 3.2 使用 Flask-Bootstrap 集成 Twitter Bootstrap

Bootstrap(http://getbootstrap.com/) 是 Twitter 开发的一个开源框架，它提供的用户界面组件可用于创建整洁且具有吸引力的网页,而且这些网页还能兼容所有现代 Web 浏览器。

Bootstrap 是客户端框架，因此不会直接涉及服务器。服务器需要做的只是提供引用了 Bootstrap 层叠样式表(CSS) 和 JavaScript 文件的 HTML 响应，并在 HTML、CSS 和 JavaScript 代码中实例化所需组件。这些操作最理想的执行场所就是模板。

要想在程序中集成 Bootstrap，显然要对模板做所有必要的改动。不过，更简单的方法是使用一个名为 Flask-Bootstrap 的 Flask 扩展，简化集成的过程。

Flask 扩展一般都在创建程序实例时初始化。示例 3-4 是 Flask-Bootstrap 的初始化方法。

```python
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap(app)
```

初始化 Flask-Bootstrap 之后，就可以在程序中使用一个包含所有 Bootstrap 文件的基模板。这个模板利用 Jinja2 的模板继承机制，让程序扩展一个具有基本页面结构的基模板，其中就有用来引入 Bootstrap 的元素。

Flask-Bootstrap 的 base.html 模板还定义了很多其他块,都可在衍生模板中使用。表 3-2 列出了所有可用的块。

| 块名             | 说明                  |
| -------------- | ------------------- |
| doc            | 整个 HTML 文档          |
| `html_attribs` | `<html>` 标签的属性      |
| html           | `<html>` 标签中的内容     |
| head           | `<head>` 标签中的内容     |
| title          | `<title>` 标签中的内容    |
| metas          | 一组 `<meta>` 标签      |
| styles         | 层叠样式表定义             |
| `body_attribs` | `<body>` 标签的属性      |
| body           | `<body>` 标签中的内容     |
| navbar         | 用户定义的导航条            |
| content        | 用户定义的页面内容           |
| scripts        | 文档底部的 JavaScript 声明 |

很多块都是 Flask-Bootstrap 自用的，如果直接重定义可能会导致一些问题。例如，Bootstrap 所需的文件在 styles 和 scripts 块中声明。如果程序需要向已经有内容的块中添加新内容，必须使用 Jinja2 提供的 super() 函数。例如，如果要在衍生模板中添加新的 JavaScript 文件，需要这么定义 scripts 块：

```python
{% block scripts %}
	{{ super() }}
	<script type="text/javascript" src="my-script.js"></script>
{% endblock %}
```

## 3.3 自定义错误页面

Flask 允许程序使用基于模板的自定义错误页面。最常见的错误代码有两个：

404，客户端请求未知页面或路由时显示；

500，有未处理的异常时显示。

为这两个错误代码指定自定义处理程序的方式如示例 3-6 所示。

```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
```

错误处理程序中引用的模板也需要编写。这些模板应该和常规页面使用相同的布局，因此要有一个导航条和显示错误消息的页面头部。

Flask-Bootstrap 提供了一个具有页面基本布局的基模板，同样，程序可以定义一个具有更完整页面布局的基模板，其中包含导航条，而页面内容则可留到衍生模板中定义。

示例 3-7 展示了 `templates/base.html` 的内容，这是一个继承自 `bootstrap/base.html` 的新模板，其中定义了导航条。这个模板本身也可作为其他模板的基模板。

```python
{% extends "bootstrap/base.html" %}

{% block title %}Flasky{% endblock %}

{% block head %}
{{ super() }}
<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
{% endblock %}

{% block navbar %}
<div class="navbar navbar-inverse" role="navigation">
    <div class="container">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">Flasky</a>
        </div>
        <div class="navbar-collapse collapse">
            <ul class="nav navbar-nav">
                <li><a href="/">Home</a></li>
            </ul>
        </div>
    </div>
</div>
{% endblock %}

{% block content %}
<div class="container">
    {% block page_content %}{% endblock %}
</div>
{% endblock %}
```

这个模板的 content 块中只有一个 `<div>` 容器，其中包含了一个名为 `page_content` 的新的空块，块中的内容由衍生模板定义。现在，程序使用的模板继承自这个模板，而不直接继承自 Flask-Bootstrap 的基模板。通过继承 `templates/base.html` 模板编写自定义的 404 错误页面很简单。

## 3.4 链接

Flask 提供了 `url_for()` 辅助函数，它可以使用程序 URL 映射中保存的信息生成 URL。

`url_for()` 函数最简单的用法是以视图函数名(或者 `app.add_url_route()` 定义路由时使用的端点名)作为参数，返回对应的 URL。例如，在当前版本的 hello.py 程序中调用 `url_ for('index')` 得到的结果是 /。调用`url_for('index', _external=True)` 返回的则是绝对地址，在这个示例中是 `http://localhost:5000/`。

使用 `url_for()` 生成动态地址时，将动态部分作为关键字参数传入。例如，`url_for ('user', name='john', _external=True)` 的返回结果是 `http://localhost:5000/user/john`。传入 `url_for()` 的关键字参数不仅限于动态路由中的参数。函数能将任何额外参数添加到查询字符串中。例如，`url_for('index', page=2)` 的返回结果是 `/?page=2`。

例子：

```python
{% block head %}
{{ super() }}
<link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
{% endblock %}
```

## 3.5 静态文件

默认设置下，Flask 在程序根目录中名为 static 的子目录中寻找静态文件。如果需要，可在 static 文件夹中使用子文件夹存放文件。

## 3.6 使用 `Flask-Moment` 本地化日期和时间

服务器需要统一时间单位，这和用户所在的地理位置无关，所以一般使用协调世界时 `(Coordinated Universal Time，UTC)`。

要想在服务器上只使用 UTC 时间，一个优雅的解决方案是，把时间单位发送给 Web 浏览器，转换成当地时间，然后渲染。Web 浏览器可以更好地完成这一任务，因为它能获取用户电脑中的时区和区域设置。

有一个使用 JavaScript 开发的优秀客户端开源代码库，名为 `moment.js(http://momentjs.com/)`，它可以在浏览器中渲染日期和时间。Flask-Moment 是一个 Flask 程序扩展（`pip install flask-moment`），能把 moment.js 集成到 Jinja2 模板中。

```python
from flask.ext.moment import Moment
moment = Moment(app)
```

除了 `moment.js`，Flask-Moment 还依赖 `jquery.js`。要在 HTML 文档的某个地方引入这两个库，可以直接引入，这样可以选择使用哪个版本，也可使用扩展提供的辅助函数，从内容分发网络(Content Delivery Network,CDN)中引入通过测试的版本。Bootstrap 已经引入 了 jquery.js，因此只需引入 moment.js 即可。

引入 `moment.js` 库：

```python
{% block scripts %}
	{{ super() }}
	{{ moment.include_moment() }}
{% endblock %}
```

为了处理时间戳，Flask-Moment 向模板开放了 moment 类。

```python
from datetime import datetime
@app.route('/')
def index():
    return render_template('index.html',current_time=datetime.utcnow())
```

模板：

```html
<p>The local date and time is {{ moment(current_time).format('LLL') }}.</p>
<p>That was {{ moment(current_time).fromNow(refresh=True) }}</p>
```

第二行中的 `fromNow()` 渲染相对时间戳，而且会随着时间的推移自动刷新显示的时间。这个时间戳最开始显示为 “a few seconds ago”，但指定 `refresh` 参数后，其内容会随着时间的推移而更新。如果一直待在这个页面，几分钟后，会看到显示的文本变成 `“a minute ago”“2 minutes ago”` 等。

Flask-Moment 实现了 moment.js 中的 `format()、fromNow()、fromTime()、calendar()、valueOf() 和 unix()` 方法。你可查阅文档(`http://momentjs.com/docs/#/displaying/`)学习 moment.js 提供的全部格式化选项。

>   Flask-Monet 假定服务器端程序处理的时间戳是“纯正的” datetime 对象，且使用 UTC 表示。
>
>   纯正的时间戳，英文为 `navie time`，指不包含时区的时间戳；
>
>   细致的时间戳，英文为 `aware time`，指包含时区的时间戳。

Flask-Moment 渲染的时间戳可实现多种语言的本地化。语言可在模板中选择，把语言代码传给 lang() 函数即可：

```python
{{ moment.lang('es') }}
```

