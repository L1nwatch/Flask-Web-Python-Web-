# 第 7 章 大型程序的结构

## 7.1 项目结构

Flask 程序的基本结构如示例 7-1 所示。

```python
├── LICENSE
├── README.md
├── app
│   ├── __init__.py
│   ├── email.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── models.py
│   ├── static
│   │   └── favicon.ico
│   └── templates
│       ├── 404.html
│       ├── 500.html
│       ├── base.html
│       ├── index.html
│       └── mail
├── config.py
├── data.sqlite
├── flasky.py
├── migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 38c4e85512a9_initial_migration.py
├── requirements.txt
├── tests
│   ├── __init__.py
│   └── test_basics.py
└── venv
```

这种结构有 4 个顶级文件夹:

-   Flask 程序一般都保存在名为 app 的包中;
-   和之前一样,migrations文件夹包含数据库迁移脚本;
-   单元测试编写在tests包中;
-   和之前一样,venv文件夹包含Python虚拟环境。

同时还创建了一些新文件:

-   requirements.txt 列出了所有依赖包,便于在其他电脑中重新生成相同的虚拟环境;
-   config.py 存储配置;
-   manage.py 用于启动程序以及其他的程序任务。

## 7.2 配置选项

程序经常需要设定多个配置。这方面最好的例子就是开发、测试和生产环境要使用不同的 数据库,这样才不会彼此影响。

```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

基类 Config 中包含通用配置,子类分别定义专用的配置。如果需要,你还可添加其他配置类。

为了让配置方式更灵活且更安全,某些配置可以从环境变量中导入。例如,SECRET_KEY 的值, 这是个敏感信息,可以在环境中设定,但系统也提供了一个默认值,以防环境中没有定义。

在 3 个子类中,SQLALCHEMY_DATABASE_URI 变量都被指定了不同的值。这样程序就可在不同 的配置环境中运行,每个环境都使用不同的数据库。配置类可以定义 init_app() 类方法,其参数是程序实例。在这个方法中,可以执行对当前 环境的配置初始化。

在这个配置脚本末尾,config 字典中注册了不同的配置环境,而且还注册了一个默认配置 (本例的开发环境)。

## 7.3 程序包

程序包用来保存程序的所有代码、模板和静态文件。

### 7.3.1 使用程序工厂函数

在单个文件中开发程序很方便,但却有个很大的缺点,因为程序在全局作用域中创建,所 以无法动态修改配置。运行脚本时,程序实例已经创建,再修改配置为时已晚。

这个问题的解决方法是延迟创建程序实例,把创建过程移到可显式调用的工厂函数中。这 种方法不仅可以给脚本留出配置程序的时间,还能够创建多个程序实例,这些实例有时在 测试中非常有用。程序的工厂函数在 app 包的构造文件中定义,如示例 7-3 所示。

`app/__init__.py:程序包的构造文件`：

```python
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
```

构造文件导入了大多数正在使用的 Flask 扩展。由于尚未初始化所需的程序实例,所以没 有初始化扩展,创建扩展类时没有向构造函数传入参数。create_app() 函数就是程序的工 厂函数,接受一个参数,是程序使用的配置名。配置类在 config.py 文件中定义,其中保存 的配置可以使用 Flask app.config 配置对象提供的 from_object() 方法直接导入程序。至 于配置对象,则可以通过名字从 config 字典中选择。程序创建并配置好后,就能初始化 扩展了。在之前创建的扩展对象上调用 init_app() 可以完成初始化过程。

### 7.3.2 在蓝本中实现程序功能

转换成程序工厂函数的操作让定义路由变复杂了。在单脚本程序中,程序实例存在于全 局作用域中,路由可以直接使用 app.route 修饰器定义。但现在程序在运行时创建,只 有调用 create_app() 之后才能使用 app.route 修饰器,这时定义路由就太晚了。和路由 一样,自定义的错误页面处理程序也面临相同的困难,因为错误页面处理程序使用 app. errorhandler 修饰器定义。

幸好 Flask 使用蓝本提供了更好的解决方法。蓝本和程序类似,也可以定义路由。不同的 是,在蓝本中定义的路由处于休眠状态,直到蓝本注册到程序上后,路由才真正成为程序 的一部分。使用位于全局作用域中的蓝本时,定义路由的方法几乎和单脚本程序一样。

和程序一样,蓝本可以在单个文件中定义,也可使用更结构化的方式在包中的多个模块中 创建。

```python
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
```

通过实例化一个 Blueprint 类对象可以创建蓝本。这个构造函数有两个必须指定的参数: 蓝本的名字和蓝本所在的包或模块。和程序一样,大多数情况下第二个参数使用 Python 的 `__name__` 变量即可。

程序的路由保存在包里的 app/main/views.py 模块中,而错误处理程序保存在 app/main/ errors.py 模块中。导入这两个模块就能把路由和错误处理程序与蓝本关联起来。注意,这 些模块在 `app/main/__init__.py` 脚本的末尾导入,这是为了避免循环导入依赖,因为在 views.py 和 errors.py 中还要导入蓝本 main。

蓝本在工厂函数 create_app() 中注册到程序上,如示例 7-5 所示。

```python
def create_app(config_name): 
    # ...
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
```

`app/main/errors.py`:蓝本中的错误处理程序

```python
from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
```

在蓝本中编写错误处理程序稍有不同,如果使用 errorhandler 修饰器,那么只有蓝本中的错误才能触发处理程序。要想注册程序全局的错误处理程序,必须使用 app_errorhandler。

url_for() 函数的用法不同。你可能还记得,url_for() 函数的第一 个参数是路由的端点名,在程序的路由中,默认为视图函数的名字。例如,在单脚本程序 中,index() 视图函数的 URL 可使用 url_for('index') 获取。

在蓝本中就不一样了,Flask 会为蓝本中的全部端点加上一个命名空间,这样就可以在不同的蓝本中使用相同的端点名定义视图函数,而不会产生冲突。命名空间就是蓝本的名字 (Blueprint 构造函数的第一个参数),所以视图函数 index() 注册的端点名是 main.index,其 URL 使用 url_for('main.index') 获取。

url_for() 函数还支持一种简写的端点形式,在蓝本中可以省略蓝本名,例如 url_for('. index')。在这种写法中,命名空间是当前请求所在的蓝本。这意味着同一蓝本中的重定向 可以使用简写形式,但跨蓝本的重定向必须使用带有命名空间的端点名。为了完全修改程序的页面,表单对象也要移到蓝本中,保存于 app/main/forms.py 模块。

## 7.4 启动脚本

顶级文件夹中的 manage.py 文件用于启动程序。

```python
#!/usr/bin/env python
...
```

出于便利,脚本中加入了 shebang 声明,所以在基于 Unix 的操作系统中可以通过 ./manage. py 执行脚本,而不用使用复杂的 python manage.py。

## 7.5 需求文件

## 7.6 单元测试

`tests/test_basics.py`:单元测试

```python
import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
```

setUp() 方法尝试创建一个测试环境,类似于运行中的程序。首先,使用测试配置创建程 序,然后激活上下文。这一步的作用是确保能在测试中使用 current_app,像普通请求一 样。然后创建一个全新的数据库,以备不时之需。数据库和程序上下文在 tearDown() 方法 中删除。

第一个测试确保程序实例存在。第二个测试确保程序在测试配置中运行。若想把 tests 文 件夹作为包使用,需要添加 `tests/__init__.py` 文件,不过这个文件可以为空,因为 unittest 包会扫描所有模块并查找测试。

为了运行单元测试,你可以在 manage.py 脚本中添加一个自定义命令。

```python
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
```

manager.command 修饰器让自定义命令变得简单。修饰函数名就是命令名,函数的文档字符 串会显示在帮助消息中。

## 7.7 创建数据库

不管从哪里获取数据库 URL,都要在新数据库中创建数据表。如果使用 Flask-Migrate 跟 踪迁移,可使用如下命令创建数据表或者升级到最新修订版本:

```python
(venv) $ python manage.py db upgrade
```