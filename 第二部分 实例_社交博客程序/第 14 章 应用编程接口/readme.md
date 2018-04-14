# 第 14 章 应用编程接口

最近几年,Web 程序有种趋势,那就是业务逻辑被越来越多地移到了客户端一侧,开创出 了一种称为富互联网应用(Rich Internet Application,RIA)的架构。在RIA中,服务器的 主要功能(有时是唯一功能)是为客户端提供数据存取服务。在这种模式中,服务器变成 了 Web 服务或应用编程接口`(Application Programming Interface,API)`。

RIA可采用多种协议与Web服务通信。远程过程调用`(Remote Procedure Call,RPC)`协议, 例如 `XML-RPC`,及由其衍生的简单对象访问协议`(Simplified Object Access Protocol,SOAP)`, 在几年前比较受欢迎。最近,表现层状态转移`(Representational State Transfer,REST)`架构崭 露头角,成为 Web 程序的新宠,因为这种架构建立在大家熟识的万维网基础之上。

Flask 是开发 REST 架构 Web 服务的理想框架,因为 Flask 天生轻量。

## 14.1 REST简介

6 个符合这一架构定义的特征：

*   客户端-服务器：`客户端和服务器之间必须有明确的界线。`
*   无状态：`客户端发出的请求中必须包含所有必要的信息。服务器不能在两次请求之间保存客户端的任何状态。`
*   缓存：`服务器发出的响应可以标记为可缓存或不可缓存,这样出于优化目的,客户端(或客户 端和服务器之间的中间服务)可以使用缓存。`
*   接口统一：`客户端访问服务器资源时使用的协议必须一致,定义良好,且已经标准化。REST Web 服务最常使用的统一接口是 HTTP 协议。`
*   系统分层：`在客户端和服务器之间可以按需插入代理服务器、缓存或网关,以提高性能、稳定性和 伸缩性。`
*   按需代码：`客户端可以选择从服务器上下载代码,在客户端的环境中执行。`

### 14.1.1 资源就是一切

资源是 REST 架构方式的核心概念。在 REST 架构中,资源是程序中你要着重关注的事物。例如,在博客程序中,用户、博客文章和评论都是资源。

每个资源都要使用唯一的URL表示。

某一类资源的集合也要有一个 URL。博客文章集合的 URL 可以是 `/api/posts/`,评论集合的 URL 可以是 `/api/comments/`。

API 还可以为某一类资源的逻辑子集定义集合 URL。例如,编号为 12345 的博客文章,其 中的所有评论可以使用URL `/api/posts/12345/comments/`表示。表示资源集合的URL习惯 在末端加上一个斜线,代表一种“文件夹”结构。

>   注意,Flask 会特殊对待末端带有斜线的路由。如果客户端请求的 URL 的末 端没有斜线,而唯一匹配的路由末端有斜线,Flask 会自动响应一个重定向, 转向末端带斜线的 URL。反之则不会重定向。

### 14.1.2 请求方法

户端程序在建立起的资源 URL 上发送请求,使用请求方法表示期望的操作。

表 14-1 列出了 REST 架构 API 中常用的 请求方法及其含义。

REST架构API中使用的HTTP请求方法

| 请求方法   | 目标        | 说明                                       | HTTP 状态码 |
| ------ | --------- | ---------------------------------------- | -------- |
| GET    | 单个资源的 URL | 获取目标资源                                   | 200      |
| GET    | 资源集合的 URL | 获取资源的集合（如果服务器实现了分页，就是一页中的资源）             | 200      |
| POST   | 资源集合的 URL | 创建新资源，并将其加入目标集合。服务器为新资源指派 URL，并在响应的 Location 首部中返回 | 201      |
| PUT    | 单个资源的 URL | 修改一个现有资源。如果客户端能为资源指派 URL，还可用来创建新资源       | 200      |
| DELETE | 单个资源的 URL | 删除一个资源                                   | 200      |
| DELETE | 资源集合的 URL | 删除目标集合中的所有资源                             | 200      |

>   REST 架构不要求必须为一个资源实现所有的请求方法。如果资源不支持 客户端使用的请求方法,响应的状态码为 405,返回“不允许使用的方法”。 Flask 会自动处理这种错误。

### 14.1.3 请求和响应主体

在请求和响应的主体中,资源在客户端和服务器之间来回传送,但 REST 没有指定编码 资源的方式。请求和响应中的 Content-Type 首部用于指明主体中资源的编码方式。使用 HTTP 协议中的内容协商机制,可以找到一种客户端和服务器都支持的编码方式。

REST Web服务常用的两种编码方式是JavaScript对象表示法(JavaScript Object Notation, JSON)和可扩展标记语言(Extensible Markup Language,XML)。对基于Web的RIA来 说,JSON 更具吸引力,因为 JSON 和 JavaScript 联系紧密

在设计良好的REST API中,客户端只需知道几个顶级资源的URL,其他资源的URL则从响 应中包含的链接上发掘。这就好比浏览网络时,你在自己知道的网页中点击链接发掘新网页。

### 14.1.4 版本

在传统的以服务器为中心的 Web 程序中,服务器完全掌控程序。更新程序时,只需在服务 器上部署新版本就可更新所有的用户,因为运行在用户 Web 浏览器中的那部分程序也是从 服务器上下载的。

但升级 RIA 和 Web 服务要复杂得多,因为客户端程序和服务器上的程序是独立开发的, 有时甚至由不同的人进行开发。你可以考虑一下这种情况,即一个程序的REST Web服 务被很多客户端使用,其中包括 Web 浏览器和智能手机原生应用。服务器可以随时更新 Web 浏览器中的客户端,但无法强制更新智能手机中的应用,更新前先要获得机主的许 可。即便机主想进行更新,也不能保证新版应用上传到所有应用商店的时机都完全吻合新 服务器端版本的部署。

基于以上原因,Web 服务的容错能力要比一般的 Web 程序强,而且还要保证旧版客户端 能继续使用。这一问题的常见解决办法是使用版本区分 Web 服务所处理的 URL。例如, 首次发布的博客 Web 服务可以通过 `/api/v1.0/posts/` 提供博客文章的集合。

在 URL 中加入 Web 服务的版本有助于条理化管理新旧功能,让服务器能为新客户端提供 新功能,同时继续支持旧版客户端。博客服务可能会修改博客文章使用的 JSON 格式,同 时通过 `/api/v1.1/posts/` 提供修改后的博客文章,而客户端仍能通过 `/api/v1.0/posts/` 获取旧的 JSON 格式。在一段时间内,服务器要同时处理 v1.1 和 v1.0 这两个版本的 URL。提供多版本支持会增加服务器的维护负担,但在某些情况下,这是不破坏现有部署且能让 程序不断发展的唯一方式。

## 14.2 使用Flask提供REST Web服务

### 14.2.1 创建API蓝本

REST API相关的路由是一个自成一体的程序子集,所以为了更好地组织代码,我们最好把这些路由放到独立的蓝本中。这个程序 API 蓝本的基本结构如示例 14-1 所示。

```shell
|-flasky |-app/
         |-api_1_0
           |-__init__.py
           |-users.py
           |-posts.py
           |-comments.py
           |-authentication.py
           |-errors.py
           |-decorators.py
```

注意,API 包的名字中有一个版本号。如果需要创建一个向前兼容的 API 版本,可以添加 一个版本号不同的包,让程序同时支持两个版本的 API。

在这个 API 蓝本中,各资源分别在不同的模块中实现。蓝本中还包含处理认证、错误以及 提供自定义修饰器的模块。蓝本的构造文件如示例 14-2 所示。

`app/api_1_0/__init__.py`:API 蓝本的构造文件

```python
from flask import Blueprint
api = Blueprint('api', __name__)
from . import authentication, posts, users, comments, errors
```

注册 API 蓝本的代码如示例 14-3 所示，`app/_init_.py`:注册 API 蓝本

```python
def create_app(config_name): # ...
    from .api_1_0 import api as api_1_0_blueprint app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0') # ...
```

### 14.2.2 错误处理

REST Web服务将请求的状态告知客户端时,会在响应中发送适当的HTTP状态码,并将额外信息放入响应主体。客户端能从 Web 服务得到的常见状态码如表 14-2 所示。

| HTTP 状态码 | 名称                             | 说明               |
| -------- | ------------------------------ | ---------------- |
| 200      | OK(成功)                         | 请求成功完成           |
| 201      | Created(已创建)                   | 请求成功完成并创建了一个新资源  |
| 400      | Bad request(坏请求)               | 请求不可用或不一致        |
| 401      | Unauthorized(未授权)              | 请求未包含认证信息        |
| 403      | Forbidden(禁止)                  | 请求中发送的认证密令无权访问目标 |
| 404      | Notfound(未找到)                  | URL 对应的资源不存在     |
| 405      | Method not allowed(不允许使用的方法)   | 指定资源不支持请求使用的方法   |
| 500      | Internal server error(内部服务器错误) | 处理请求的过程中发生意外错误   |

处理 404 和 500 状态码时会有点小麻烦,因为这两个错误是由 Flask 自己生成的,而且一 般会返回 HTML 响应,这很可能会让 API 客户端困惑。

为所有客户端生成适当响应的一种方法是,在错误处理程序中根据客户端请求的格式改写 响应,这种技术称为内容协商。示例 14-4 是改进后的 404 错误处理程序,它向 Web 服务 客户端发送 JSON 格式响应,除此之外都发送 HTML 格式响应。500 错误处理程序的写法 类似。

`app/main/errors.py`：使用 HTTP 内容协商处理错误

```python
@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
    not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404
```

这个新版错误处理程序检查 Accept 请求首部(Werkzeug 将其解码为 `request.accept_ mimetypes)`,根据首部的值决定客户端期望接收的响应格式。浏览器一般不限制响应的格 式,所以只为接受 JSON 格式而不接受 HTML 格式的客户端生成 JSON 格式响应。

其他状态码都由 Web 服务生成,因此可在蓝本的 errors.py 模块作为辅助函数实现。

`app/api_1_0/errors.py`:API 蓝本中 403 状态码的错误处理程序

```python
def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response
```

### 14.2.3 使用Flask-HTTP Auth认证用户

和普通的 Web 程序一样,Web 服务也需要保护信息,确保未经授权的用户无法访问。为此,RIA 必须询问用户的登录密令,并将其传给服务器进行验证。

客户端必须在发出的请求中包含所有必要信息,因此所有请求都 必须包含用户密令。

程序当前的登录功能是在 Flask-Login 的帮助下实现的,可以把数据存储在用户会话中。默 认情况下,Flask 把会话保存在客户端 cookie 中,因此服务器没有保存任何用户相关信息, 都转交给客户端保存。这种实现方式看起来遵守了 REST 架构的无状态要求,但在 REST Web 服务中使用 cookie 有点不现实,因为 Web 浏览器之外的客户端很难提供对 cookie 的 支持。鉴于此,使用 cookie 并不是一个很好的设计选择。

>   REST 架构的无状态要求看起来似乎过于严格,但这并不是随意提出的要 求,无状态的服务器伸缩起来更加简单。如果服务器保存了客户端的相关信 息,就必须提供一个所有服务器都能访问的共享缓存,这样才能保证一直使 用同一台服务器处理特定客户端的请求。这样的需求很难实现。

因为 REST 架构基于 HTTP 协议,所以发送密令的最佳方式是使用 HTTP 认证,基本认证 和摘要认证都可以。在 HTTP 认证中,用户密令包含在请求的 Authorization 首部中。

HTTP认证协议很简单,可以直接实现,不过Flask-HTTPAuth扩展提供了一个便利的包 装,可以把协议的细节隐藏在修饰器之中,类似于 Flask-Login 提供的 login_required 修 饰器。

```shell
(venv) $ pip install flask-httpauth
```

在将 HTTP 基本认证的扩展进行初始化之前,我们先要创建一个 HTTPBasicAuth 类对象。 和Flask-Login一样,Flask-HTTPAuth不对验证用户密令所需的步骤做任何假设,因此所 需的信息在回调函数中提供。

`app/api_1_0/authentication.py`:初始化Flask-HTTPAuth：

```python
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True
    user = User.query.filter_by(email = email).first() if not user:
        return False
    g.current_user = user
    return user.verify_password(password)
```

由于这种用户认证方法只在API蓝本中使用,所以Flask-HTTPAuth扩展只在蓝本包中初 始化,而不像其他扩展那样要在程序包中初始化

验证回调函数把通过认证的用户保存在 Flask 的全局对象 g 中,如此一来,视图函数便能 进行访问。注意,匿名登录时,这个函数返回 True 并把 Flask-Login 提供的 AnonymousUser 类实例赋值给 `g.current_user`。

>   由于每次请求时都要传送用户密令,所以 API 路由最好通过安全的 HTTP 提 供,加密所有的请求和响应。

如果认证密令不正确,服务器向客户端返回401错误。默认情况下,Flask-HTTPAuth自 动生成这个状态码,但为了和 API 返回的其他错误保持一致,我们可以自定义这个错误响 应,如示例 14-7 所示。

`app/api_1_0/authentication.py`:Flask-HTTPAuth错误处理程序

```python
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')
```

为保护路由,可使用修饰器 `auth.login_required`:

```python
@api.route('/posts/')
@auth.login_required
def get_posts():
    pass
```

不过,这个蓝本中的所有路由都要使用相同的方式进行保护,所以我们可以在 `before_request` 处理程序中使用一次 login_required 修饰器,应用到整个蓝本,如示例 14-8 所示。

`app/api_1_0/authentication.py`:在 `before_request` 处理程序中进行认证

```python
from .errors import forbidden_error

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \ not g.current_user.confirmed:
        return forbidden('Unconfirmed account')
```

现在,API 蓝本中的所有路由都能进行自动认证。而且作为附加认证,`before_request` 处理程序还会拒绝已通过认证但没有确认账户的用户。

### 14.2.4 基于令牌的认证

每次请求时,客户端都要发送认证密令。为了避免总是发送敏感信息,我们可以提供一种基于令牌的认证方案。

使用基于令牌的认证方案时,客户端要先把登录密令发送给一个特殊的 URL,从而生成 认证令牌。一旦客户端获得令牌,就可用令牌代替登录密令认证请求。出于安全考虑,令 牌有过期时间。令牌过期后,客户端必须重新发送登录密令以生成新令牌。令牌落入他人 之手所带来的安全隐患受限于令牌的短暂使用期限。为了生成和验证认证令牌,我们要在 User 模型中定义两个新方法。这两个新方法用到了 itsdangerous 包,如示例 14-9 所示。

`app/models.py`:支持基于令牌的认证

```python
class User(db.Model):
    # ...
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY']) try:
            data = s.loads(token)
            except:
                return None
            return User.query.get(data['id'])
```

`generate_auth_token()` 方法使用编码后的用户 id 字段值生成一个签名令牌,还指定了以秒 为单位的过期时间。`verify_auth_token()` 方法接受的参数是一个令牌,如果令牌可用就返 回对应的用户。`verify_auth_token()` 是静态方法,因为只有解码令牌后才能知道用户是谁。

为了能够认证包含令牌的请求,我们必须修改Flask-HTTPAuth提供的 `verify_password` 回 调,除了普通的密令之外,还要接受令牌。修改后的回调如示例 14-10 所示。

`app/api_1_0/authentication.py`:支持令牌的改进验证回调

```python
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first() if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)
```

在这个新版本中,第一个认证参数可以是电子邮件地址或认证令牌。如果这个参数为空, 那就和之前一样,假定是匿名用户。如果密码为空,那就假定 `email_or_token` 参数提供的 是令牌,按照令牌的方式进行认证。如果两个参数都不为空,假定使用常规的邮件地址和 密码进行认证。在这种实现方式中,基于令牌的认证是可选的,由客户端决定是否使用。 为了让视图函数能区分这两种认证方法,我们添加了 `g.token_used` 变量。

把认证令牌发送给客户端的路由也要添加到 API 蓝本中,具体实现如示例 14-11 所示。

`app/api_1_0/authentication.py`:生成认证令牌

```python
@api.route('/token')
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
```

由于这个路由也在蓝本中,所以添加到 `before_request` 处理程序上的认证机制也会用在这 个路由上。为了避免客户端使用旧令牌申请新令牌,要在视图函数中检查 `g.token_used` 变 量的值,如果使用令牌进行认证就拒绝请求。这个视图函数返回 JSON 格式的响应,其中 包含了过期时间为 1 小时的令牌。JSON 格式的响应也包含过期时间。

### 14.2.5 资源和JSON的序列化转换

开发 Web 程序时,经常需要在资源的内部表示和 JSON 之间进行转换。JSON 是 HTTP 请求和响应使用的传输格式。示例 14-12 是新添加到 Post 类中的 `to_json()` 方法。

提供给客户端的资源表示没必要和数据库模型的内部表示完全一致。

把 JSON 转换成模型时面临的问题是,客户端提供的数据可能无效、错误或者多余。示例 14-14 是从 JSON 格式数据创建 Post 模型实例的方法。

`app/models.py`:从 JSON 格式数据创建一篇博客文章

```python
from app.exceptions import ValidationError
￼￼class Post(db.Model):
    # ...
    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
            return Post(body=body)
```

如你所见,上述代码在实现过程中只选择使用 JSON 字典中的 body 属性,而把 body_html 属性忽略了,因为只要 body 属性的值发生变化,就会触发一个 SQLAlchemy 事件,自动 在服务器端渲染 Markdown。除非允许客户端倒填日期(这个程序并不提供此功能),否则 无需指定 timestamp 属性。由于客户端无权选择博客文章的作者,所以没有使用 author 字 段。author 字段唯一能使用的值是通过认证的用户。comments 和 comment_count 属性使用 数据库关系自动生成,因此其中没有创建模型所需的有用信息。最后,url 字段也被忽略 了,因为在这个实现中资源的 URL 由服务器指派,而不是客户端。

注意如何检查错误。如果没有 body 字段或者其值为空,from_json() 方法会抛出 ValidationError 异常。在这种情况下,抛出异常才是处理错误的正确方式,因为 from_json() 方法并没有掌握处理问题的足够信息,唯有把错误交给调用者,由上层代码处理这个错误。

现在,程序需要向客户端提供适当的响应以处理这个异常。为了避免在视图函数中编写捕 获异常的代码,我们可创建一个全局异常处理程序。对于 ValidationError 异常,其处理 程序如示例 14-16 所示。

`app/api_1_0/errors.py`:API 中 ValidationError 异常的处理程序

```python
@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
```

使用这个技术时,视图函数中得代码可以写得十分简洁明,而且无需检查错误。例如:

```python
@api.route('/posts/', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
```

### 14.2.6 实现资源端点

用来防止未授权用户创建新博客文章的 `permission_required` 修饰器和程序中使用的类似, 但会针对 API 蓝本进行自定义。具体实现如示例 14-19 所示。

`app/api_1_0/decorators.py:permission_required` 修饰器：

```python
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

博客文章 PUT 请求的处理程序用来更新现有资源,如示例 14-20 所示。

`app/api_1_0/posts.py`:文章资源 PUT 请求的处理程序

```python
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
    not g.current_user.can(Permission.ADMINISTER): return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
```

### 14.2.7 分页大型资源集合

`app/api_1_0/posts.py`:分页文章资源

```python
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('api.get_posts', page=page+1, _external=True)
            return jsonify({
                'posts': [post.to_json() for post in posts],
                'prev': prev,
                'next': next,
                'count': pagination.total
            })
```

### 14.2.8 使用 `HTTPie` 测试 Web 服务

常使用的两个在命令行中测试 Web 服务的客户端是 curl 和 HTTPie。后者的命令行更简洁,可读性也更高。HTTPie 使用 pip 安装:

```shell
(venv) $ pip install httpie
```

GET 请求可按照如下的方式发起:

```shell
(venv) $ http --json --auth <email>:<password> GET \
> http://127.0.0.1:5000/api/v1.0/posts
HTTP/1.0 200 OK
Content-Length: 7018
Content-Type: application/json
Date: Sun, 22 Dec 2013 08:11:24 GMT
Server: Werkzeug/0.9.4 Python/2.7.3
{
"posts": [
... ],
"prev": null
"next": "http://127.0.0.1:5000/api/v1.0/posts/?page=2",
"count": 150
}
```

匿名用户可发送空邮件地址和密码以发起相同的请求:

```shell
(venv) $ http --json --auth : GET http://127.0.0.1:5000/api/v1.0/posts/
```

下面这个命令发送 POST 请求以添加一篇新博客文章:

```shell
 (venv) $ http --auth <email>:<password> --json POST \
```

要想使用认证令牌,可向 `/api/v1.0/token` 发送请求:

```shell
(venv) $ http --auth <email>:<password> --json GET \
```

在接下来的 1 小时中,这个令牌可用于访问 API,请求时要和空密码一起发送:

```shell
(venv) $ http --json --auth eyJpYXQ...: GET http://127.0.0.1:5000/api/v1.0/posts/
```