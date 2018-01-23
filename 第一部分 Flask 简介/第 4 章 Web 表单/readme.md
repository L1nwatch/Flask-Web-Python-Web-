# 第 4 章 Web 表单

Flask-WTF `(http://pythonhosted.org/Flask-WTF/)` 扩展可以把处理 Web 表单的过程变成一 种愉悦的体验。

Flask-WTF 及其依赖可使用 pip 安装: 

```shell
(venv) $ pip install flask-wtf
```

## 4.1 跨站请求伪造保护

默认情况下，Flask-WTF 能保护所有表单免受跨站请求伪造 `(Cross-Site Request Forgery，CSRF)` 的攻击。恶意网站把请求发送到被攻击者已登录的其他网站时就会引发 CSRF 攻击。 为了实现 CSRF 保护，Flask-WTF 需要程序设置一个密钥。Flask-WTF 使用这个密钥生成加密令牌,再用令牌验证请求中表单数据的真伪。设置密钥的方法：

```shell
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
```

`app.config` 字典可用来存储框架、扩展和程序本身的配置变量。

>   为了增强安全性,密钥不应该直接写入代码,而要保存在环境变量中。这一技术会在第 7 章介绍。

## 4.2 表单类

使用 Flask-WTF 时，每个 Web 表单都由一个继承自 Form 的类表示。这个类定义表单中的一组字段，每个字段都用对象表示。字段对象可附属一个或多个验证函数。验证函数用来验证用户提交的输入值是否符合要求。

```python
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
```

StringField 构造函数中的可选参数 validators 指定一个由验证函数组成的列表，在接受用户提交的数据之前验证数据。验证函数 `Required()` 确保提交的字段不为空。

>   Form 基类由 Flask-WTF 扩展定义,所以从 `flask.ext.wtf` 中导入。字段和验证函数却可以直接从 WTForms 包中导入。

WTForms 支持的 HTML 标准字段如表 4-1 所示：

| 字段类型                | 说明                             |
| ------------------- | ------------------------------ |
| StringField         | 文本字段                           |
| TextAreaField       | 多行文本字段                         |
| PasswordField       | 密码文本字段                         |
| HiddenField         | 隐藏文本字段                         |
| DateField           | 文本字段，值为 `datetime.date` 格式     |
| DateTimeField       | 文本字段，值为 `datetime.datetime` 格式 |
| IntegerField        | 文本字段，值为整数                      |
| DecimalField        | 文本字段，值为 `decimal.Decimal`      |
| FloatField          | 文本字段，值为浮点数                     |
| BooleanField        | 复选框，值为 True 和 False            |
| RadioField          | 一组单选框                          |
| SelectField         | 下拉列表                           |
| SelectMultipleField | 下拉列表，可选择多个值                    |
| FileField           | 文件上传字段                         |
| SubmitField         | 表单提交按钮                         |
| FieldList           | 把表单作为字段嵌入另一个表单                 |
| FormField           | 一组指定类型的字段                      |

WTForms 内建的验证函数如表 4-2 所示：

| 验证函数        | 说明                          |
| ----------- | --------------------------- |
| Email       | 验证电子邮件地址                    |
| EqualTo     | 比较两个字段的值;常用于要求输入两次密码进行确认的情况 |
| IPAddress   | 验证 IPv4 网络地址                |
| Length      | 验证输入字符串的长度                  |
| NumberRange | 验证输入的值在数字范围内                |
| Optional    | 无输入值时跳过其他验证函数               |
| Required    | 确保字段中有数据                    |
| Regexp      | 使用正则表达式验证输入值                |
| URL         | 验证 URL                      |
| AnyOf       | 确保输入值在可选值列表中                |
| NoneOf      | 确保输入值不在可选值列表中               |

## 4.3 在表单渲染成 HTML

通过参数 form 传入模板，两种方式：

```html
<form method="POST">
	{{ form.hidden_tag() }}
	{{ form.name.label }} {{ form.name(id='my-text-field') }} {{ form.submit() }}
</form>
```

在条件允许的情况下最好能使用 Bootstrap 中的表单样式。Flask-Bootstrap 提供了一个非常高端的辅助函数，可以使用 Bootstrap 中预先定义好的表单样式渲染整个 Flask-WTF 表单，而这些操作只需一次调用即可完成。使用 Flask-Bootstrap，上述表单可使用下面的方式渲染：

```python
{% import "bootstrap/wtf.html" as wtf %}
{{ wtf.quick_form(form) }}
```

导入的 `bootstrap/wtf.html` 文件中定义了一个使用 Bootstrap 渲染 Falsk-WTF 表单对象的辅助函数。`wtf.quick_form()` 函数的参数为 Flask-WTF 表单对象，使用 Bootstrap 的默认样式渲染传入的表单。

```shell
{% extends "base.html" %}
{% import "bootstrap/wtf.html" as wtf %}

{% block title %}Flasky{% endblock %}

{% block page_content %}
<div class="page-header">
    <h1>Hello, {% if name %}{{ name }}{% else %}Stranger{% endif %}!</h1>
</div>
{{ wtf.quick_form(form) }}
{% endblock %}
```

## 4.4 在视图函数中处理表单

用户提交表单后,服务器收到一个包含数据的 POST 请求。`validate_on_submit()` 会调用 name 字段上附属的 `Required()` 验证函数。如果名字不为空，就能通过验证，`validate_on_ submit()` 返回 True。

```python
@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('index.html', form=form, name=name)
```

## 4.5 重定向和用户会话

最好别让 Web 程序把 POST 请求作为浏览器发送的最后一个请求。

这种需求的实现方式是，使用重定向作为 POST 请求的响应，而不是使用常规响应。重定向是一种特殊的响应，响应内容是 URL，而不是包含 HTML 代码的字符串。浏览器收到这种响应时，会向重定向的 URL 发起 GET 请求，显示页面的内容。这个页面的加载可能要多花几微秒，因为要先把第二个请求发给服务器。除此之外，用户不会察觉到有什么不同。现在，最后一个请求是 GET 请求，所以刷新命令能像预期的那样正常使用了。这个技巧称为 `Post/ 重定向 /Get 模式`。

程序可以把数据存储在用户会话中，在请求之间“记住”数据。用户会话是一种私有存储，存在于每个连接到服务器的客户端中。我们在第 2 章介绍过用户会话，它是请求上下文中的变量，名为 session，像标准的 Python 字典一样操作。

>   默认情况下，用户会话保存在客户端 cookie 中，使用设置的 SECRET_KEY 进行加密签名。如果篡改了 cookie 中的内容，签名就会失效，会话也会随之失效。

```python
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))
```

