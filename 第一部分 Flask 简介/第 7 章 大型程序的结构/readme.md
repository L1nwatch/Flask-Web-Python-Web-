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

