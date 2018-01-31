# 第 8 章 用户认证

## 8.1 Flask 的认证扩展

本章使用的包列表如下：

* Flask-Login:管理已登录用户的用户会话。
* Werkzeug:计算密码散列值并进行核对。
* itsdangerous:生成并核对加密安全令牌。

## 8.2 密码安全性

### 使用Werkzeug实现密码散列

Werkzeug 中的 security 模块能够很方便地实现密码散列值的计算。这一功能的实现只需要两个函数,分别用在注册用户和验证用户阶段。

*   `generate_password_hash(password, method=pbkdf2:sha1, salt_length=8)`:这个函数将原始密码作为输入,以字符串形式输出密码的散列值,输出的值可保存在用户数据库中。method 和 salt_length 的默认值就能满足大多数需求。
*   `check_password_hash(hash, password)`:这个函数的参数是从数据库中取回的密码散列值和用户输入的密码。返回值为 True 表明密码正确。

app/models.py:在 User 模型中加入密码散列

```python
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    # ...
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
```

计算密码散列值的函数通过名为 password 的只写属性实现。

密码散列功能已经完成,可以在 shell 中进行测试:

```python
(venv) $ python manage.py shell
>>> u = User()
>>> u.password = 'cat'
>>> u.password_hash
'pbkdf2:sha1:1000$duxMk0OF$4735b293e397d6eeaf650aaf490fd9091f928bed'
>>> u.verify_password('cat')
True
>>> u.verify_password('dog')
False
>>> u2 = User()
>>> u2.password = 'cat'
>>> u2.password_hash
'pbkdf2:sha1:1000$UjvnGeTP$875e28eb0874f44101d6b332442218f66975ee89'
```

## 8.3 创建认证蓝本

与用户认证系统相关的路由可在 auth 蓝本中定义。对于不同的程序功能, 我们要使用不同的蓝本,这是保持代码整齐有序的好方法。

auth 蓝本保存在同名 Python 包中。蓝本的包构造文件创建蓝本对象,再从 views.py 模块 中引入路由,代码如示例 8-3 所示。

注意,为 render_template() 指定的模板文件保存在 auth 文件夹中。这个文件夹必须在 app/templates 中创建,因为 Flask 认为模板的路径是相对于程序模板文件夹而言的。为避 免与 main 蓝本和后续添加的蓝本发生模板命名冲突,可以把蓝本使用的模板保存在单独的 文件夹中。

>   我们也可将蓝本配置成使用其独立的文件夹保存模板。如果配置了多个模板 文件夹,render_template() 函数会首先搜索程序配置的模板文件夹,然后再 搜索蓝本配置的模板文件夹。

auth 蓝本要在 create_app() 工厂函数中附加到程序上,如示例 8-5 所示。

`app/__init__.py`:附加蓝本

```python
def create_app(config_name):
    # ...
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app
```

注册蓝本时使用的 url_prefix 是可选参数。如果使用了这个参数,注册后蓝本中定义的 所有路由都会加上指定的前缀,即这个例子中的 /auth。

## 8.4 使用Flask-Login认证用户

用户登录程序后,他们的认证状态要被记录下来,这样浏览不同的页面时才能记住这个状 态。Flask-Login 是个非常有用的小型扩展,专门用来管理用户认证系统中的认证状态,且 不依赖特定的认证机制。

使用之前,我们要在虚拟环境中安装这个扩展:

```shell
(venv) $ pip install flask-login
```

### 8.4.1 准备用于登录的用户模型

Flask-Login要求实现的用户方法

| 方法                 | 说明                                       |
| ------------------ | ---------------------------------------- |
| is_authenticated() | 如果用户已经登录,必须返回True,否则返回False              |
| is_active()        | 如果允许用户登录,必须返回 True,否则返回 False。如果要禁用账户,可以返回 False |
| is_anonymous()     | 对普通用户必须返回 False                          |
| get_id()           | 必须返回用户的唯一标识符,使用 Unicode 编码字符串            |

这 4 个方法可以在模型类中作为方法直接实现,不过还有一种更简单的替代方案。Flask- Login 提供了一个 UserMixin 类,其中包含这些方法的默认实现,且能满足大多数需求。修 改后的 User 模型如示例 8-6 所示。

示例 8-6 app/models.py:修改 User 模型,支持用户登录

```python
from flask.ext.login import UserMixin
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
```

Flask-Login 在程序的工厂函数中初始化,如示例 8-7 所示。

`app/__init__.py`:初始化 Flask-Login

```python
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
def create_app(config_name): # ...
    login_manager.init_app(app)
    # ...
```

最后,Flask-Login 要求程序实现一个回调函数,使用指定的标识符加载用户。这个函数的 定义如示例 8-8 所示。

示例 8-8 app/models.py:加载用户的回调函数

```python
from . import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

加载用户的回调函数接收以 Unicode 字符串形式表示的用户标识符。如果能找到用户,这 个函数必须返回用户对象;否则应该返回 None。

### 8.4.2 保护路由

为了保护路由只让认证用户访问,Flask-Login 提供了一个 login_required 修饰器。用法演示如下:

```python
from flask.ext.login import login_required
@app.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'
```

如果未认证的用户访问这个路由,Flask-Login 会拦截请求,把用户发往登录页面。

### 8.4.3 添加登录表单

```html
<ul class="nav navbar-nav navbar-right">
  {% if current_user.is_authenticated() %}
  <li><a href="{{ url_for('auth.logout') }}">Sign Out</a></li> {% else %}
  <li><a href="{{ url_for('auth.login') }}">Sign In</a></li> {% endif %}
</ul>
```

判断条件中的变量 current_user 由 Flask-Login 定义,且在视图函数和模板中自动可用。 这个变量的值是当前登录的用户,如果用户尚未登录,则是一个匿名用户代理对象。如果 是匿名用户,is_authenticated() 方法返回 False。所以这个方法可用来判断当前用户是否 已经登录。

### 8.4.4 登入用户

为了登入用户,视图函数首先使用表单中填写的 email 从数据库中加载用户。如果电子邮 件地址对应的用户存在,再调用用户对象的 verify_password() 方法,其参数是表单中填 写的密码。如果密码正确,则调用 Flask-Login 中的 login_user() 函数,在用户会话中把 用户标记为已登录。login_user() 函数的参数是要登录的用户,以及可选的“记住我”布 尔值,“记住我”也在表单中填写。如果值为 False,那么关闭浏览器后用户会话就过期 了,所以下次用户访问时要重新登录。如果值为 True,那么会在用户浏览器中写入一个长 期有效的 cookie,使用这个 cookie 可以复现用户会话。

“Post/ 重定向 /Get 模式”,提交登录密令的 POST 请求最后也做了重定 向,不过目标 URL 有两种可能。用户访问未授权的 URL 时会显示登录表单,Flask-Login 会把原地址保存在查询字符串的 next 参数中,这个参数可从 request.args 字典中读取。 如果查询字符串中没有 next 参数,则重定向到首页。如果用户输入的电子邮件或密码不正 确,程序会设定一个 Flash 消息,再次渲染表单,让用户重试登录。

### 8.4.5 登出用户

app/auth/views.py:退出路由

```python
from flask.ext.login import logout_user, login_required
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.') return redirect(url_for('main.index'))
```

为了登出用户,这个视图函数调用 Flask-Login 中的 logout_user() 函数,删除并重设用户 会话。随后会显示一个 Flash 消息,确认这次操作,再重定向到首页,这样登出就完成了。

## 8.5 注册新用户

### 8.5.1 添加用户注册表单

示例 8-15 app/auth/forms.py:用户注册表单

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
```

安全起见,密码要输入两次。此时要验证两个密码字段中的值是否一致,这种验证可使用 WTForms 提供的另一验证函数实现,即 EqualTo。这个验证函数要附属到两个密码字段中 的一个上,另一个字段则作为参数传入。

这个表单还有两个自定义的验证函数,以方法的形式实现。如果表单类中定义了以 validate_ 开头且后面跟着字段名的方法,这个方法就和常规的验证函数一起调用。

自定 义的验证函数要想表示验证失败,可以抛出 ValidationError 异常,其参数就是错误消息。

### 8.5.2 注册新用户

app/auth/views.py:用户注册路由

```python
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
```

## 8.6 确认账户

为验证电子邮件地址,用户注册后,程序会立即发送一封确认邮件。新账户先被标记成待 确认状态,用户按照邮件中的说明操作后,才能证明自己可以被联系上。账户确认过程 中,往往会要求用户点击一个包含确认令牌的特殊 URL 链接。

### 8.6.1 使用itsdangerous生成确认令牌

确认邮件中最简单的确认链接是 http://www.example.com/auth/confirm/<id> 这种形式的 URL,其中 id 是数据库分配给用户的数字 id。用户点击链接后,处理这个路由的视图函 数就将收到的用户 id 作为参数进行确认,然后将用户状态更新为已确认。

但这种实现方式显然不是很安全,只要用户能判断确认链接的格式,就可以随便指定 URL 中的数字,从而确认任意账户。解决方法是把 URL 中的 id 换成将相同信息安全加密后得 到的令牌。

Flask 使用加密的签名 cookie 保护用户会话, 防止被篡改。这种安全的 cookie 使用 itsdangerous 包签名。同样的方法也可用于确认令 牌上。

下面这个简短的 shell 会话显示了如何使用 itsdangerous 包生成包含用户 id 的安全令牌:

```python
(venv) $ python manage.py shell
>>> from manage import app
>>> from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
>>> s = Serializer(app.config['SECRET_KEY'], expires_in = 3600)
>>> token = s.dumps({ 'confirm': 23 })
>>> token
'eyJhbGciOiJIUzI1NiIsImV4cCI6MTM4MTcxODU1OCwiaWF0IjoxMzgxNzE0OTU4fQ.ey ...'
>>> data = s.loads(token)
>>> data {u'confirm': 23}
```

itsdangerous 提供了多种生成令牌的方法。其中,TimedJSONWebSignatureSerializer 类生成 具有过期时间的JSON Web签名(JSON Web Signatures,JWS)。这个类的构造函数接收 的参数是一个密钥,在 Flask 程序中可使用 SECRET_KEY 设置。

dumps() 方法为指定的数据生成一个加密签名,然后再对数据和签名进行序列化,生成令 牌字符串。expires_in 参数设置令牌的过期时间,单位为秒。

为了解码令牌,序列化对象提供了 loads() 方法,其唯一的参数是令牌字符串。这个方法 会检验签名和过期时间,如果通过,返回原始数据。如果提供给 loads() 方法的令牌不正 确或过期了,则抛出异常。

我们可以将这种生成和检验令牌的功能可添加到 User 模型中。

generate_confirmation_token() 方法生成一个令牌,有效期默认为一小时。confirm() 方 法检验令牌,如果检验通过,则把新添加的 confirmed 属性设为 True。

```python

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username
```

除了检验令牌,confirm() 方法还检查令牌中的 id 是否和存储在 current_user 中的已登录 用户匹配。如此一来,即使恶意用户知道如何生成签名令牌,也无法确认别人的账户。

### 8.6.2 发送确认邮件

