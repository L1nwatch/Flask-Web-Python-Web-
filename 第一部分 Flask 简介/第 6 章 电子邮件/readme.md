# 第 6 章 电子邮件

虽然 Python 标准库中的 smtplib 包可用在 Flask 程序中发送电子邮件,但包装了 smtplib 的 Flask-Mail 扩展能更好地和 Flask 集成。

## 使用Flask-Mail提供电子邮件支持

```python
(venv) $ pip install flask-mail
```

Flask-Mail连接到简单邮件传输协议(Simple Mail Transfer Protocol,SMTP)服务器,并把邮件交给这个服务器发送。

### Flask-Mail SMTP服务器的配置

| 配置              | 默认值       | 说明                                      |
| --------------- | --------- | --------------------------------------- |
| `MAIL_SERVER`   | localhost | 电子邮件服务器的主机名或 IP 地址                      |
| `MAIL_PORT`     | 25        | 电子邮件服务器的端口                              |
| `MAIL_USE_TLS`  | False     | 启用传输层安全（Transport Layer Security，TLS）协议 |
| `MAIL_USE_SSL`  | False     | 启用安全套接层（Secure Sockets Layer，SSL）协议     |
| `MAIL_USERNAME` | None      | 邮件账户的用户名                                |
| `MAIL_PASSWORD` | None      | 邮件账户的密码                                 |

```python
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

from flask.ext.mail import Mail
mail = Mail(app)
```

如果你在 Linux 或 Mac OS X 中使用 bash,那么可以按照下面的方式设定这两个变量:

```shell
(venv) $ export MAIL_USERNAME=<Gmail username>
(venv) $ export MAIL_PASSWORD=<Gmail password>
```

微软 Windows 用户可按照下面的方式设定环境变量:

```shell
(venv) $ set MAIL_USERNAME=<Gmail username>
(venv) $ set MAIL_PASSWORD=<Gmail password>
```

## 在Python shell中发送电子邮件

```python
(venv) $ python hello.py shell
>>> from flask.ext.mail import Message
>>> from hello import mail
>>> msg = Message('test subject', sender='you@example.com', ... recipients=['you@example.com'])
>>> msg.body = 'text body'
>>> msg.html = '<b>HTML</b> body'
>>> with app.app_context():
... mail.send(msg)
```

## 在程序中集成发送电子邮件功能

可以使用 Jinja2 模板渲染邮件正文

```python
from flask.ext.mail import Message
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to]) msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
```

指定 模板时不能包含扩展名,这样才能使用两个模板分别渲染纯文本正文和富文本正文。调用者 将关键字参数传给 render_template() 函数,以便在模板中使用,进而生成电子邮件正文。

index() 视图函数很容易被扩展,这样每当表单接收新名字时,程序都会给管理员发送一 封电子邮件。

```python
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))
```

我们要创建两个模板文件,分别用于渲染纯文本和 HTML 版本的邮件正 文。

```html
User <b>{{ user.username }}</b> has joined.
```

```shell
User {{ user.username }} has joined.
```

## 异步发送电子邮件

如果你发送了几封测试邮件,可能会注意到 mail.send() 函数在发送电子邮件时停滞了几 秒钟,在这个过程中浏览器就像无响应一样。为了避免处理请求过程中不必要的延迟,我 们可以把发送电子邮件的函数移到后台线程中。

```python
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
```

很多 Flask 扩展都假设已经存在激活的程序上下文和请求 上下文。Flask-Mail 中的 send() 函数使用 current_app,因此必须激活程序上下文。不过, 在不同线程中执行 mail.send() 函数时,程序上下文要使用 app.app_context() 人工创建。

程序要发送大量电子邮件时,使 用专门发送电子邮件的作业要比给每封邮件都新建一个线程更合适。例如,我们可以把执 行 send_async_email() 函数的操作发给 Celery(http://www.celeryproject.org/)任务队列。