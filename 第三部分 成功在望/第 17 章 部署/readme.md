# 第 17 章 部署

## 17.1 部署流程

不管使用哪种托管方案,程序安装到生产服务器上之后,都要执行一系列的任务。最好的例子就是创建或更新数据库表。

如果每次安装或升级程序都手动执行任务,那么容易出错也浪费时间,所以我们可以在 `manage.py` 中添加一个命令,自动执行所需操作。

`manage.py`:部署命令

```python
@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    
    # 把数据库迁移到最新修订版本
    upgrade()
    
    # 创建用户角色
    Role.insert_roles()

    # 让所有用户都关注此用户
    User.add_self_follows()
```

## 17.2 把生产环境中的错误写入日志

如果调试模式中运行的程序发生错误,那么会出现 Werkzeug 中的交互式调试器。网页中显示错误的栈跟踪,而且可以查看源码,甚至还能使用 Flask 的网页版交互调试器在每个栈帧的上下文中执行表达式。

调试器是开发过程中进行问题调试的优秀工具,但其显然不能在生产环境中使用。生产环境中发生的错误会被静默掉,取而代之的是向用户显示一个 500 错误页面。不过幸好错误的栈跟踪不会完全丢失,因为 Flask 会将其写入日志文件。

在程序启动过程中,Flask 会创建一个 Python 提供的 `logging.Logger` 类实例,并将其附属到程序实例上,得到 app.logger。在调试模式中,日志记录器会把记录写入终端;但在生产模式中,默认情况下没有配置日志的处理程序,所以如果不添加处理程序,就不会保存日志。示例 17-2 中的改动配置了一个日志处理程序,把生产模式中出现的错误通过电子邮件发送给 `FLASKY_ADMIN` 中设置的管理员。

`config.py`:程序出错时发送电子邮件

```python
class ProductionConfig(Config):
	# ...
	@classmethod
	def init_app(cls, app):
		Config.init_app(app)
		
		# 把错误通过电子邮件发送给管理员
		import logging
		from logging.handlers import SMTPHandler

		credentials = None
		secure = None
		if getattr(cls, 'MAIL_USERNAME', None) is not None:
			credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
		if getattr(cls, 'MAIL_USE_TLS', None):
			secure = ()
         mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT), fromaddr=cls.FLASKY_MAIL_SENDER,toaddrs=[cls.FLASKY_ADMIN], subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error', credentials=credentials,secure=secure)
	     mail_handler.setLevel(logging.ERROR)
         app.logger.addHandler(mail_handler)
```

回顾一下,所有配置实例都有一个 `init_app()` 静态方法,在 `create_app()` 方法中调用。在 ProductionConfig 类的 `init_app()` 方法的实现中,配置程序的日志记录器把错误写入电子 邮件日志记录器。电子邮件日志记录器的日志等级被设为 `logging.ERROR`,所以只有发生严重错误时才会发送 电子邮件。通过添加适当的日志处理程序,可以把较轻缓等级的日志消息写入文件、系统 日志或其他的支持方法。这些日志消息的处理方法很大程度上依赖于程序使用的托管平台。

## 17.3 云部署

程序托管的最新潮流是托管到云端。云技术以前称为平台即服务(Platform as a Service,PaaS),它让程序开发者从安装和维护运行程序的软硬件平台的日常工作中解放出来。在PaaS 模型中,服务提供商完全接管了运行程序的平台。程序开发者使用服务商提供的工具和库把程序集成到平台上,然后将其上传到提供商维护的服务器中,部署的过程往往只需几秒钟。大多数 PaaS 提供商都可以通过按需添加或删除服务器以实现程序的动态扩展,从而满足不同请求量的需求。

云部署有较高的灵活性,而且使用起来相对容易。当然,这些优势都是花钱买来的。Heroku 是最流行的 PaaS 提供商之一,对 Python 支持良好。下一节,我们将详细说明如何把程序部署到 Heroku 中。

## 17.4 Heroku平台

Heroku 是最早出现的 PaaS 提供商之一,从 2007 年就开始运营。Heroku 平台的灵活性极高且支持多种编程语言。若想把程序部署到 Heroku 上,开发者要使用 Git 把程序推送到Heroku的Git服务器上。在服务器上,git push命令会自动触发安装、配置和部署程序。

Heroku 使用名为 Dyno 的计算单元衡量用量,并以此为依据收取服务费用。最常用的 Dyno类型是 Web Dyno,表示一个 Web 服务器实例。程序可以通过使用更多的 Web Dyno 以增强其请求处理能力。另一种 Dyno 类型是 Worker Dyno,用来执行后台作业或其他辅助任务。

Heroku 提供了大量的插件和扩展,可用于数据库、电子邮件支持和其他很多服务。下面各节将展开说明把 Flasky 部署到 Heroku 上的细节步骤。

### 17.4.1 准备程序

若想使用 Heroku,程序必须托管在 Git 仓库中。如果你的程序托管在像 GitHub 或 BitBucket 这样的远程 Git 服务器上,那么克隆程序后会创建一个本地 Git 仓库,可无缝用 于 Heroku。如果你的程序没有托管在 Git 仓库中,那么必须在开发电脑上创建一个仓库。

#### 注册账号，使用免费服务

#### 安装 Heroku Toolbelt

最方便的Heroku程序管理方法是使用Heroku Toolbelt(https://toolbelt.heroku.com/)命令 行工具。Toolbelt 由两个 Heroku 程序组成。

-   heroku:Heroku 客户端,用来创建和管理程序。
-   foreman:一种工具,测试时可用于在自己的电脑上模拟 Heroku 环境。

在 Heroku 客户端连接服务器之前,你需要提供 Heroku 账户密令。`heroku login` 命令可以完成这一操作。

#### 创建程序

接下来,我们要使用 Heroku 客户端创建一个程序。为此,我们首先要确保程序已纳入 Git 源码控制系统,然后在顶级目录中运行如下命令:

```shell
$ heroku create <appname>
```

Heroku 中的程序名必须是唯一的,所以你要找一个没被其他程序使用的名字。如 create命令的输出所示,部署后程序可通过 `http://<appname>.herokuapp.com` 访问。你可以给程序设置自定义域名。

在程序创建过程中,Heroku 还给你分配了一个 Git 服务器,地址为 `git@heroku.com:<appname>.git`。create命令调用git remote命令把这个地址添加为本地Git仓库的远程服务器,名为 heroku。

#### 配置数据库

Heroku 以扩展形式支持 Postgres 数据库。少于 1 万条记录的小型数据库无需付费即可添加 到程序中:

```shell
$ heroku addons:add heroku-postgresql:dev
Adding heroku-postgresql:dev on <appname>... done, v3 (free)
Attached as HEROKU_POSTGRESQL_BROWN_URL
Database has been created and is available
! This database is empty. If upgrading, you can transfer
! data from another database with pgbackups:restore.
Use`heroku addons:docs heroku-postgresql:dev`to view documentation.
```

环境变量 `HEROKU_POSTGRESQL_BROWN_URL` 中保存了数据库的 URL。注意,运行这个命令后,你得到的颜色可能不是棕色。Heroku 中的每个程序都支持多个数据库,而每个数据库 URL 中的颜色都不一样。数据库的地位可以提升,把 URL 保存到环境变量 `DATABASE_URL` 中。下述命令把前面创建的棕色数据库提升为主数据库:

```shell
$ heroku pg:promote HEROKU_POSTGRESQL_BROWN_URL
Promoting HEROKU_POSTGRESQL_BROWN_URL to DATABASE_URL... done
```

`DATABASE_URL` 环境变量的格式正是 SQLAlchemy 所需的。回想一下 config.py 脚本的内容,如果 设定了 DATABASE_URL,就使用其中保存的值,所以现在程序可以自动连接到 Postgres 数据库。

#### 配置日志

在 Heroku 中,日志必须写入 stdout 或 stderr。Heroku 会捕获输出的日志,可以在 Heroku 客户端中使用heroku logs命令查看。

日志的配置可添加到 ProductionConfig 类的 init_app() 静态方法中,但由于这种日志处 理方式是 Heroku 专用的,因此可专门为这个平台新建一个配置类,把 ProductionConfig 作为不同类型生产平台的基类。HerokuConfig 类如示例 17-3 所示。

`config.py`:Heroku 的配置

```python
class HerokuConfig(ProductionConfig):
	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app(app)

		# 输出到 stderr
		import logging
		from logging import StreamHandler
		file_handler = StreamHandler()
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)
```

通过 Heroku 执行程序时,程序需要知道要使用的就是这个配置。`manage.py` 脚本创建的程 序实例通过环境变量 `FLASK_CONFIG` 决定使用哪个配置,所以我们要在 Heroku 的环境中设 定这个变量。环境变量使用 Heroku 客户端中的 config:set 命令设定:

```shell
$ heroku config:set FLASK_CONFIG=heroku
Setting config vars and restarting <appname>... done, v4 FLASK_CONFIG: heroku
```

#### 配置电子邮件

Heroku 没有提供 SMTP 服务器,所以我们要配置一个外部服务器。很多第三方扩展能把 适用于生产环境的邮件发送服务集成到 Heroku 中,但对于测试和评估而言,使用继承自 Config 基类的 Gmail 配置已经足够了。

由于直接把安全密令写入脚本存在安全隐患,所以我们把访问Gmail SMTP服务器的用户 名和密码保存在环境变量中:

```shell
$ heroku config:set MAIL_USERNAME=<your-gmail-username>
$ heroku config:set MAIL_PASSWORD=<your-gmail-password>
```

#### 运行生产Web服务器

Heroku 没有为托管程序提供 Web 服务器,相反,它希望程序启动自己的服务器并监听环 境变量 PORT 中设定的端口。

Flask 自带的开发 Web 服务器表现很差,因为它不是为生产环境设计的服务器。有两个 可以在生产环境中使用、性能良好且支持 Flask 程序的服务器,分别是 Gunicorn(http:// gunicorn.org/)和 uWSGI(http://uwsgi-docs.readthedocs.org/en/latest/)。

若想在本地测试 Heroku 配置,我们最好在虚拟环境中安装 Web 服务器。例如,可通过如 下命令安装 Gunicorn:

```shell
(venv) $ pip install gunicorn
```

若要使用 Gunicorn 运行程序,可执行下面的命令:

```shell
(venv) $ gunicorn manage:app
```

manage:app 参数冒号左边的部分表示定义程序的包或者模块,冒号右边的部分表示包中程 序实例的名字。注意,Gunicor 默认使用端口 8000,而 Flask 默认使用 5000。

#### 添加依赖需求文件

Heroku 从程序顶级文件夹下的 requirements.txt 文件中加载包依赖。这个文件中的所有依赖 都会在部署过程中导入 Heroku 创建的虚拟环境。Heroku 的需求文件必须包含程序在生产环境中使用的所有通用依赖,以及支持 Postgres 数 据库的 psycopg2 包和 Gunicorn Web 服务器。

`requirements.txt`:Heroku 需求文件

```shell
-r requirements/prod.txt
gunicorn==18.0
psycopg2==2.5.1
```

#### 添加Procfile文件

Heroku 需要知道使用哪个命令启动程序。这个命令在一个名为 Procfile 的特殊文件中指定。 这个文件必须放在程序的顶级文件夹中。

Procfile:Heroku Procfile 文件

```shell
web: gunicorn manage:app
```

Procfile 文件内容的格式很简单:在每一行中指定一个任务名,后跟一个冒号,然后是运行 这个任务的命令。名为 web 的任务比较特殊任务,Heroku 使用这个任务启动 Web 服务器。

Heroku 会为这个任务提供一个 PORT 环境变量,用于设定程序监听请求的端口。如果设定 了 PORT 变量,Gunicorn 默认就会使用其中保存的值,因此无需将其包含在启动命令中。

>   程序可在 Procfile 中使用 web 之外的名字声明其他任务,例如程序所需的其 他服务。部署程序后,Heroku 会运行 Procfile 中列出的所有任务。

### 17.4.2 使用Foreman进行测试

Heroku Toolbelt 中还包含另一个名为 Foreman 的工具,它用于在本地通过 Procfile 运行程序以进行测试。Heroku 客户端设定的像 `FLASK_CONFIG` 这样的环境变量只在 Heroku 服务器 上可用,因此要在本地设定,这样 Foreman 使用的测试环境才和生产环境类似。Foreman 会在程序顶级目录中搜寻一个名为 .env 的文件,加载其中的环境变量。例如 .env 文件中可 包含以下变量:

```shell
FLASK_CONFIG=heroku
MAIL_USERNAME=<your-username>
MAIL_PASSWORD=<your-password>
```

oreman 有多个命令,其中两个主要命令是 `foreman run` 和 `foreman start`。run 命令用于 在程序的环境中运行任意命令,特别适合运行创建程序数据库的 deploy 命令:

```shell
(venv) $ foreman run python manage.py deploy
```

start 命令读取 Procfile 的内容,执行其中的所有任务:

```shell
(venv) $ foreman start
```

Foreman 把所有启动任务的日志输出整合在一起并转储至终端,其中每一行的前面都加入 了时间戳和任务名。

使用 -c 选项还能模拟多个 Dyno。例如,下述命令启动了 3 个 Web 工作线程(Web worker),各职程分别监听不同的端口: 

```shell
(venv) $ foreman start -c web=3
```

### 17.4.3 使用Flask-SSLify启用安全HTTP

用户登录程序时要在 Web 表单中提交用户名和密码,这些数据在传输过程中可被第三方截取,就像前文已多次提及的。为了避免他人使用这种方式偷取用户密令,我们必须使用安全 HTTP,使用公钥加密法加密客户端和服务器之间传输的数据。

Heroku 上的程序在 herokuapp.com 域中可使用 http:// 和 https:// 访问,无需任何配置即可直接使用 Heroku 的 SSL 证书。唯一需要做的是让程序拦截发往 http:// 的请求,重定向到https://,这一操作可使用 Flask-SSLify 扩展完成。

我们要将 Flask-SSLify 扩展添加到 requirements.txt 文件中。示例 17-6 中的代码用于激活这个扩展。

`app/__init__.py`:把所有请求重定向到安全 HTTP

```python
def create_app(config_name):
	# ...
	if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
		from flask.ext.sslify import SSLify
		sslify = SSLify(app)
	# ...
```

对 SSL 的支持只需在生产模式中启用,而且所在平台必须支持。为了便于打开和关闭 SSL, 添加了一个名为 `SSL_DISABLE` 的新配置变量。Config 基类将其设为 True,即默认情况下不 使用 SSL,并且 HerokuConfig 类覆盖了这个值。这个变量的配置方式如示例 17-7 所示。

`config.py`:配置是否使用 SSL

```python
class Config:
	# ...
	SSL_DISABLE = True
class HerokuConfig(ProductionConfig):
	# ...
	SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
```

在 HerokuConfig 类中,`SSL_DISABLE` 的值从同名环境变量中读取。如果这个环境变量的值 不是空字符串,那么将其转换成布尔值后会得到 True,即禁用 SSL。如果没有设定这个环 境变量或者其值为空字符串,转换成布尔值后会得到 False。为了避免使用 Foreman 时启 用 SSL,必须在 .env 文件中加入 `SSL_DISABLE=1`。

做了以上改动后,用户会被强制使用 SSL。但还有一个细节需要处理才能完善这一功能。 使用 Heroku 时,客户端不直接连接托管的程序,而是连接一个反向代理服务器,然后再把请求重定向到程序上。在这种连接方式中,只有代理服务器运行在 SSL 模式中。程序从 代理服务器接收到的请求都没有使用 SSL,因为在 Heroku 网络内部无需使用高安全性的 请求。程序生成绝对 URL 时,要和请求使用的安全连接一致,这时就产生问题了,因为 使用反向代理服务器时,`request.is_secure` 的值一直是 False。

User 模型中的 `gravatar()` 方法在生成 `Gravatar URL` 时检查了 `request.is_secure` ,根据其值的不同分别生 成安全或不安全的 URL。如果通过 SSL 请求页面,生成的却是不安全的头像 URL,某些浏 览器会向用户显示安全警告,所以同一页面中的所有内容都要使用安全性相同的 URL。

代理服务器通过自定义的 HTTP 首部把客户端发起的原始请求信息传给重定向后的 Web 服 务器,所以查看这些首部就有可能知道用户和程序通信时是否使用了 SSL。Werkzeug 提 供了一个 WSGI 中间件,可用来检查代理服务器发出的自定义首部并对请求对象进行相应 更新。例如,修改后的 `request.is_secure` 表示客户端发给反向代理服务器的请求安全性, 而不是代理服务器发给程序的请求安全性。示例 17-8 展示了如何把 ProxyFix 中间件添加 到程序中。

`config.py`:支持代理服务器

```python
class HerokuConfig(ProductionConfig):
    # ...
    @classmethod
    def init_app(cls, app):
        # ...
        # 处理代理服务器首部
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
```

ProxyFix 中间件添加在 Heroku 配置的初始化方法中。添加 ProxyFix 等 WSGI 中间件的方 法是包装 WSGI 程序。收到请求时,中间件有机会审查环境,在处理请求之前做些修改。 不仅 Heroku 需要使用 ProxyFix 中间件,任何使用反向代理的部署环境都需要。

### 17.4.4 执行 git push 命令部署

部署过程的最后一步是把程序上传到 Heroku 服务器。在此之前,你要确保所有改动都已经提交到本地Git仓库,然后执行 `git push heroku master` 把程序上传到远程仓库 heroku

```shell
$ git push heroku master
```

现在,程序已经部署好正在运行了,但还不能正常使用,因为还没执行 deploy 命令。 Heroku 客户端可按照下面的方式执行这个命令:

```shell
$ heroku run python manage.py deploy
```

创建并配置好数据库表之后就可以重启程序了,直接使用下述命令即可:

```shell
$ heroku restart
```

### 17.4.5 查看日志

程序生成的日志输出会被 Heroku 捕获,若想查看日志内容,可使用 logs 命令:

```shell
$ heroku logs
```

在测试过程中,还可以使用下述命令方便地跟踪日志文件的内容:

```shell
$ heroku logs -t
```

### 17.4.6 部署一次升级

升级 Heroku 程序时要重复上述步骤。所有改动都提交到 Git 仓库之后,可执行下述命令进 行升级:

```shell
$ heroku maintenance:on
$ git push heroku master
$ heroku run python manage.py deploy
$ heroku restart
$ heroku maintenance:off
```

Heroku 客户端提供的 maintenance 命令会在升级过程中下线程序,并向用户显示一个静态 页面,告知网站很快就能恢复。

## 17.5 传统的托管

如果你选择使用传统托管,那么要购买或租用服务器(物理服务器或虚拟服务器),然后 自己动手在服务器上设置所有需要的组件。传统托管一般比托管在云中要便宜,但显然要 付出更多的劳动。下面各节将简要说明其中涉及的工作

### 17.5.1 架设服务器

在能够托管程序之前,服务器必须完成多项管理任务。

-   安装数据库服务器,例如MySQL或Postgres。也可使用SQLite数据库,但由于其自身的种种限制,不建议用于生产服务器。

-   安装邮件传输代理(Mail Transport Agent,MTA),例如Sendmail,用于向用户发送邮件。

-   安装适用于生产环境的Web服务器,例如Gunicorn或uWSGI。

-   为了启用安全HTTP,购买、安装并配置SSL证书。


-   (可选,但强烈推荐)安装前端反向代理服务器,例如 nginx 或 Apache。反向代理服务

    器能直接服务于静态文件,而把其他请求转发给程序使用的 Web 服务器。Web 服务器

    监听 localhost 中的一个私有端口。

-   强化服务器。这一过程包含多项任务,目标在于降低服务器被攻击的可能性,例如安装 防火墙以及删除不用的软件和服务等。

### 17.5.2 导入环境变量

和 Heroku 中的程序一样,运行在独立服务器上的程序也要依赖某些设置,例如数据库 URL、电子邮件服务器密令以及配置名。这些设置保存在环境变量中,启动服务器之前必须导入。

由于没有 Heroku 客户端和 Foreman 来导入变量,这个任务需要在启动过程中由程序本身 完成。

示例 17-9 中这段简短的代码能加载并解析 Foreman 使用的 .env 文件。在创建程序 实例代码之前,可以将这段代码添加到启动脚本 manage.py 中。

`manage.py`:从 .env 文件中导入环境变量

```python
if os.path.exists('.env'):
	print('Importing environment from .env...')
	for line in open('.env'):
		var = line.strip().split('=')
		if len(var) == 2:
			os.environ[var[0]] = var[1]
```

`.env` 文件中至少要包含 `FLASK_CONFIG` 变量,用以选择要使用的配置。

### 17.5.3 配置日志

在基于 Unix 的服务器中,日志可发送给守护进程 syslog。我们可专门为 Unix 创建一个新配置,继承自 ProductionConfig,如示例 17-10 所示。 

`config.py`:Unix 配置示例

```python
class UnixConfig(ProductionConfig):
	@classmethod
    def init_app(cls, app):
    	ProductionConfig.init_app(app)
        
        # 写入系统日志
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
```

这样配置之后,程序的日志会写入 `/var/log/messages`。如果需要,我们还可以配置系统日 志服务,从而把日志写入别的文件或者发送到其他设备中。