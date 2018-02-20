# 第 10 章 用户资料

## 10.1 资料信息

app/models.py:用户信息字段

```python
class User(UserMixin, db.Model):
    # ...
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
```

注意,datetime.utcnow 后面没有 (),因为 db.Column() 的 default 参数可以接受函数作为默认值,所以每次需要生成默认值时,db.Column() 都会 调用指定的函数。`member_since` 字段只需要默认值即可。

last_seen 字段创建时的初始值也是当前时间,但用户每次访问网站后,这个值都会被刷 新。我们可以在 User 模型中添加一个方法完成这个操作

```python
class User(UserMixin, db.Model):
    # ...
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
```

每次收到用户的请求时都要调用 ping() 方法。由于 auth 蓝本中的 before_app_request 处 理程序会在每次请求前运行,所以能很轻松地实现这个需求,如示例 10-3 所示。

```python
@auth.before_app_request
def before_request():
    if current_user.is_authenticated(): current_user.ping()
        if not current_user.confirmed \
        and request.endpoint[:5] != 'auth.': 
            return redirect(url_for('auth.unconfirmed'))
```

## 10.2 用户资料页面

```html
{% if current_user.is_authenticated() %} <li>
  <a href="{{ url_for('main.user', username=current_user.username) }}"> Profile
  </a> </li>
{% endif %}
```

把资料页面的链接包含在条件语句中是非常必要的,因为未认证的用户也能看到导航条,但我们不应该让他们看到资料页面的链接。

## 10.3 资料编辑器

用户资料的编辑分两种情况。用户自己和管理员所有。这两种编辑需求有本质上的区 别,所以我们要创建两个不同的表单。

### 10.3.1 用户级别的资料编辑器

```python
class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
```

为了让用户能轻易找到编辑页面,我们可以在资料页面中添加一个链接,如示例 10-9 所示。 

```html
{% if user == current_user %}
<a class="btn btn-default" href="{{ url_for('.edit_profile') }}">
Edit Profile </a>
{% endif %}
```

### 10.3.2 管理员级别的资料编辑器

管理员使用的资料编辑表单比普通用户的表单更加复杂。除了前面的 3 个资料信息字段之 外,管理员在表单中还要能编辑用户的电子邮件、用户名、确认状态和角色。这个表单如 示例 10-10 所示。

```python
class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()]) 
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)]) location = StringField('Location', validators=[Length(0, 64)]) about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    def __init__(self, user, *args, **kwargs): 
        super(EditProfileAdminForm, self).__init__(*args, **kwargs) 
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
```

在 SelectField 构造函数中添加 coerce=int 参数,从而把字段的值转换为整数, 而不使用默认的字符串。

email 和 username 字段的构造方式和认证表单中的一样,但处理验证时需要更加小心。验 证这两个字段时,首先要检查字段的值是否发生了变化,如果有变化,就要保证新值不 和其他用户的相应字段值重复;如果字段值没有变化,则应该跳过验证。为了实现这个逻辑,表单构造函数接收用户对象作为参数,并将其保存在成员变量中,随后自定义的验证 方法要使用这个用户对象。

可使用 Flask-SQLAlchemy 提供的 get_or_404() 函数,如果提供的 id 不正确,则会返回 404 错误。

## 10.4 用户头像

Gravatar 是一个行业领先的头像服务,能把头像和电子邮件地址关联起来。用户先要到 http://gravatar.com 中注册账户,然后上传图片。生成头像的 URL 时,要计算电子邮件地址的 MD5 散列值:

```python
(venv) $ python
>>> import hashlib
>>> hashlib.md5('john@example.com'.encode('utf-8')).hexdigest()
'd4c74594d841139328695756648b6bd6'
```

生 成 的 头 像 URL 是 在 http://www.gravatar.com/avatar/ 或 https://secure.gravatar.com/avatar/ 之后加上这个 MD5 散列值。例如,你在浏览器的地址栏中输入 http://www.gravatar.com/ avatar/d4c74594d841139328695756648b6bd6,就会看到电子邮件地址 john@example.com 对 应的头像图片。如果这个电子邮件地址没有对应的头像,则会显示一个默认图片。头像 URL 的查询字符串中可以包含多个参数以配置头像图片的特征。可设参数如表 10-1 所示。

| 参数名  | 说明                                       |
| ---- | ---------------------------------------- |
| s    | 图片大小，单位为像素                               |
| r    | 图片级别。可选值有 "g"、"pg"、"r" 和 "x"             |
| d    | 没有注册 Gravatar 服务的用户使用的默认图片生成方式。可选值有:"404",返回 404 错误;默 |
| fd   | 强制使用默认头像                                 |

我们可将构建 Gravatar URL 的方法添加到 User 模型中,实现方式如示例 10-13 所示。 

```python
import hashlib
from flask import request

class User(UserMixin, db.Model):
    # ...
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
```

这一实现会选择标准的或加密的Gravatar URL基以匹配用户的安全需求。头像的URL由 URL 基、用户电子邮件地址的 MD5 散列值和参数组成,而且各参数都设定了默认值。有 了上述实现,我们就可以在 Python shell 中轻易生成头像的 URL 了:

```python
(venv) $ python manage.py shell
>>> u = User(email='john@example.com')
>>> u.gravatar()
'http://www.gravatar.com/avatar/d4c74594d84113932869575bd6?s=100&d=identicon&r=g'
>>> u.gravatar(size=256)
'http://www.gravatar.com/avatar/d4c74594d84113932869575bd6?s=256&d=identicon&r=g'
```

gravatar() 方法也可在 Jinja2 模板中调用。示例 10-14 在资料页面中添加了一个大小为 256 像素的头像。

```html
<img class="img-rounded profile-thumbnail" src="{{ user.gravatar(size=256) }}"> 
```

生成头像时要生成 MD5 值,这是一项 CPU 密集型操作。如果要在某个页面中生成大量头 像,计算量会非常大。由于用户电子邮件地址的 MD5 散列值是不变的,因此可以将其缓 存在 User 模型中。若要把 MD5 散列值保存在数据库中,需要对 User 模型做些改动,如示 例 10-15 所示。

```python
class User(UserMixin, db.Model):
    # ...
    avatar_hash = db.Column(db.String(32))
    def __init__(self, **kwargs):
        # ...
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
    def change_email(self, token):
        # ...
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
```

模型初始化过程中会计算电子邮件的散列值,然后存入数据库,若用户更新了电子邮件 地址,则会重新计算散列值。gravatar() 方法会使用模型中保存的散列值;如果模型中没 有,就和之前一样计算电子邮件地址的散列值。