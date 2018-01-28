# 第 5 章 数据库

Web 程序最常用基 于关系模型的数据库,这种数据库也称为 SQL 数据库,因为它们使用结构化查询语言。不 过最近几年文档数据库和键值对数据库成了流行的替代选择,这两种数据库合称 NoSQL 数据库。

## 5.1 SQL数据库

关系型数据库把数据存储在表中,表模拟程序中不同的实体。

表的列数是固定的,行数是可变的。

表中有个特殊的列,称为主键,其值为表中各行的唯一标识符。表中还可以有称为外键的 列,引用同一个表或不同表中某行的主键。行之间的这种联系称为关系,这是关系型数据 库模型的基础。

关系型数据库存储数据很高效,而且避免了重复。

## 5.2 NoSQL数据库

所有不遵循上节所述的关系模型的数据库统称为 NoSQL 数据库。NoSQL 数据库一般使用 集合代替表,使用文档代替记录。NoSQL 数据库采用的设计方式使联结变得困难,所以大 多数数据库根本不支持这种操作。

使用 NoSQL 数据库当然也有好处。数据重复可以提升查询速度。列出用户及其角色的操 作很简单,因为无需联结。

## 5.3 使用SQL还是NoSQL

SQL 数据库擅于用高效且紧凑的形式存储结构化数据。这种数据库需要花费大量精力保证数据的一致性。NoSQL 数据库放宽了对这种一致性的要求,从而获得性能上的优势。

## 5.4 Python数据库框架

Flask 并不限制你使 用何种类型的数据库包,因此可以根据自己的喜好选择使用 MySQL、Postgres、SQLite、 Redis、MongoDB 或者 CouchDB。

如果这些都无法满足需求,还有一些数据库抽象层代码包供选择,例如 SQLAlchemy 和 MongoEngine。你可以使用这些抽象包直接处理高等级的 Python 对象,而不用处理如表、 文档或查询语言此类的数据库实体。

*   易用性：如果直接比较数据库引擎和数据库抽象层,显然后者取胜。抽象层,也称为对象关系 映射(Object-Relational Mapper,ORM)或对象文档映射(Object-Document Mapper, ODM),在用户不知觉的情况下把高层的面向对象操作转换成低层的数据库指令。
*   性能：ORM 和 ODM 把对象业务转换成数据库业务会有一定的损耗。大多数情况下,这种性 能的降低微不足道,但也不一定都是如此。一般情况下,ORM 和 ODM 对生产率的提 升远远超过了这一丁点儿的性能降低,所以性能降低这个理由不足以说服用户完全放弃 ORM 和 ODM。真正的关键点在于如何选择一个能直接操作低层数据库的抽象层,以 防特定的操作需要直接使用数据库原生指令优化。
*   可移植性:选择数据库时,必须考虑其是否能在你的开发平台和生产平台中使用。可移植性还针对 ORM 和 ODM。尽管有些框架只为一种数据库引擎提供抽象层,但其 他框架可能做了更高层的抽象,它们支持不同的数据库引擎,而且都使用相同的面向对 象接口。SQLAlchemy ORM就是一个很好的例子,它支持很多关系型数据库引擎,包 括流行的 MySQL、Postgres 和 SQLite。
*   FLask集成度:选择框架时,你不一定非得选择已经集成了 Flask 的框架,但选择这些框架可以节省 你编写集成代码的时间。使用集成了 Flask 的框架可以简化配置和操作,所以专门为 Flask 开发的扩展是你的首选。

## 5.5 使用Flask-SQLAlchemy管理数据库

Flask-SQLAlchemy 是一个 Flask 扩展,简化了在 Flask 程序中使用 SQLAlchemy 的操作。 SQLAlchemy 是一个很强大的关系型数据库框架,支持多种数据库后台。SQLAlchemy 提 供了高层 ORM,也提供了使用数据库原生 SQL 的低层功能。

```python
pip install flask-sqlalchemy
```

FLask-SQLAlchemy数据库URL

| 数据库引擎           | URL                                      |
| --------------- | ---------------------------------------- |
| MySQL           | mysql://username:password@hostname/database |
| Postgres        | postgresql://username:password@hostname/database |
| SQLite(Unix)    | sqlite:////absolute/path/to/database     |
| SQLite(Windows) | sqlite:///c:/absolute/path/to/database   |

数据库服务器上可以托管多个数据库,因此 database 表示要使用的 数据库名。如果数据库需要进行认证,username 和 password 表示数据库用户密令。

>   SQLite 数据库不需要使用服务器,因此不用指定 hostname、username 和 password。URL 中的 database 是硬盘上文件的文件名。

程序使用的数据库 URL 必须保存到 Flask 配置对象的 SQLALCHEMY_DATABASE_URI 键中。配 置对象中还有一个很有用的选项,即 SQLALCHEMY_COMMIT_ON_TEARDOWN 键,将其设为 True 时,每次请求结束后都会自动提交数据库中的变动。其他配置选项的作用请参阅 Flask- SQLAlchemy 的文档。

```python
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

## 5.6 定义模型

模型这个术语表示程序使用的持久化实体。在 ORM 中,模型一般是一个 Python 类,类中的属性对应数据库表中的列。Flask-SQLAlchemy 创建的数据库实例为模型提供了一个基类以及一系列辅助类和辅助函 数,可用于定义模型的结构。

```python
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
```

最常用的SQLAlchemy列类型

| 类型名          | Python 类型          | 说明                              |
| ------------ | ------------------ | ------------------------------- |
| Integer      | int                | 普通整数,一般是 32 位                   |
| SmallInteger | int                | 取值范围小的整数,一般是 16 位               |
| BigInteger   | int 或 long         | 不限制精度的整数                        |
| Float        | float              | 浮点数                             |
| Numeric      | decimal.Decimal    | 定点数                             |
| String       | str                | 变长字符串                           |
| Text         | str                | 变长字符串,对较长或不限长度的字符串做了优化          |
| Unicode      | unicode            | 变长 Unicode 字符串                  |
| UnicodeText  | unicode            | 变长 Unicode 字符串,对较长或不限长度的字符串做了优化 |
| Boolean      | bool               | 布尔值                             |
| Date         | datetime.date      | 日期                              |
| Time         | datetime.time      | 时间                              |
| DateTime     | datetime.datetime  | 日期和时间                           |
| Interval     | datetime.timedelta | 时间间隔                            |
| Enum         | str                | 一组字符串                           |
| PickleType   | 任何 Python 对象       | 自动使用 Pickle 序列化                 |
| LargeBinary  | str                | 二进制文件                           |

db.Column 中其余的参数指定属性的配置选项。

最常使用的SQLAlchemy列选项

| 选项名         | 说明                                      |
| ----------- | --------------------------------------- |
| primary_key | 如果设为 True,这列就是表的主键                      |
| unique      | 如果设为 True,这列不允许出现重复的值                   |
| index       | 如果设为 True,为这列创建索引,提升查询效率                |
| nullable    | 如果设为 True,这列允许使用空值;如果设为 False,这列不允许使用空值 |
| default     | 为这列定义默认值                                |

>   Flask-SQLAlchemy 要求每个模型都要定义主键,这一列经常命名为 id。

虽然没有强制要求,但这两个模型都定义了 __repr()__ 方法

## 5.7 关系

一对多关系在模型类中的表示方法如示例 5-3 所示。

```python
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
```

关系使用 users 表中的外键连接了两行。添加到 User 模型中的 role_id 列 被定义为外键,就是这个外键建立起了关系。传给 db.ForeignKey() 的参数 'roles.id' 表 明,这列的值是 roles 表中行的 id 值。

添加到 Role 模型中的 users 属性代表这个关系的面向对象视角。对于一个 Role 类的实例, 其 users 属性将返回与角色相关联的用户组成的列表。db.relationship() 的第一个参数表 明这个关系的另一端是哪个模型。如果模型类尚未定义,可使用字符串形式指定。

db.relationship() 中的 backref 参数向 User 模型中添加一个 role 属性,从而定义反向关 系。这一属性可替代 role_id 访问 Role 模型,此时获取的是模型对象,而不是外键的值。

大多数情况下,db.relationship() 都能自行找到关系中的外键,但有时却无法决定把 哪一列作为外键。例如,如果 User 模型中有两个或以上的列定义为 Role 模型的外键, SQLAlchemy 就不知道该使用哪列。如果无法决定外键,你就要为 db.relationship() 提供 额外参数,从而确定所用外键。表 5-4 列出了定义关系时常用的配置选项。

| 选项名           | 说明                                       |
| ------------- | ---------------------------------------- |
| backref       | 在关系的另一个模型中添加反向引用                         |
| primaryjoin   | 明确指定两个模型之间使用的联结条件。只在模棱两可的关系中需要指定         |
| lazy          | 指定如何加载相关记录。可选值有 select(首次访问时按需加载)、immediate(源对象加载后就加载)、joined(加载记录,但使用联结)、subquery(立即加载,但使用子查询), noload(永不加载)和 dynamic(不加载记录,但提供加载记录的查询) |
| uselist       | 如果设为 False，不使用列表，而使用标量值                  |
| order_by      | 指定关系中记录的排列方式                             |
| secondary     | 指定多对多关系中关系表的名字                           |
| secondaryjoin | SQLAlchemy 无法自行决定时，指定多对多关系中的二级联结条件       |

除了一对多之外,还有几种其他的关系类型。一对一关系可以用前面介绍的一对多关系 表示,但调用 db.relationship() 时要把 uselist 设为 False,把“多”变成“一”。多对 一关系也可使用一对多表示,对调两个表即可,或者把外键和 db.relationship() 都放在“多”这一侧。最复杂的关系类型是多对多,需要用到第三张表,这个表称为关系表。

## 5.8 数据库操作

### 5.8.1 创建表

首先,我们要让 Flask-SQLAlchemy 根据模型类创建数据库。方法是使用 db.create_all() 函数:

```python
(venv) $ python hello.py shell
>>> from hello import db
>>> db.create_all()
```

如果数据库表已经存在于数据库中,那么 db.create_all() 不会重新创建或者更新这个表。如果修改模型后要把改动应用到现有的数据库中,这一特 性会带来不便。更新现有数据库表的粗暴方式是先删除旧表再重新创建:

```python
>>> db.drop_all()
>>> db.create_all()
```

### 5.8.2 插入行

下面这段代码创建了一些角色和用户:

```python
>>> from hello import Role, User
>>> admin_role = Role(name='Admin')
>>> mod_role = Role(name='Moderator')
>>> user_role = Role(name='User')
>>> user_john = User(username='john', role=admin_role)
>>> user_susan = User(username='susan', role=user_role)
>>> user_david = User(username='david', role=user_role)
```

注意,role 属性也 可使用,虽然它不是真正的数据库列,但却是一对多关系的高级表示。这些新建对象的 id 属性并没有明确设定,因为主键是由 Flask-SQLAlchemy 管理的。现在这些对象只存在于 Python 中,还未写入数据库。因此 id 尚未赋值:

```python
>>> print(admin_role.id)
None
>>> print(mod_role.id)
None
>>> print(user_role.id)
None
```

通过数据库会话管理对数据库所做的改动,在 Flask-SQLAlchemy 中,会话由 db.session 表示。准备把对象写入数据库之前,先要将其添加到会话中:

```python
>>> db.session.add(admin_role)
>>> db.session.add(mod_role)
>>> db.session.add(user_role)
>>> db.session.add(user_john)
>>> db.session.add(user_susan)
>>> db.session.add(user_david)
```

或者简写成:

```python
>>> db.session.add_all([admin_role, mod_role, user_role,
                        ...     user_john, user_susan, user_david])
```

为了把对象写入数据库,我们要调用 commit() 方法提交会话:

```python
>>> db.session.commit()
```

数据库会话能保证数据库的一致性。提交操作使用原子方式把会话中的对象全部写入数据 库。如果在写入会话的过程中发生了错误,整个会话都会失效。如果你始终把相关改动放 在会话中提交,就能避免因部分更新导致的数据库不一致性。

>   数据库会话也可回滚。调用 db.session.rollback() 后,添加到数据库会话 中的所有对象都会还原到它们在数据库时的状态。

### 5.8.3 修改行

在数据库会话上调用 add() 方法也能更新模型。

```python
>>> admin_role.name = 'Administrator'
>>> db.session.add(admin_role)
>>> db.session.commit()
```

### 5.8.4 删除行

```python
>>> db.session.delete(mod_role)
>>> db.session.commit()
```

### 5.8.5 查询行

```python
>>> Role.query.all()
[<Role u'Administrator'>, <Role u'User'>]
>>> User.query.all()
[<User u'john'>, <User u'susan'>, <User u'david'>]
```

使用过滤器可以配置 query 对象进行更精确的数据库查询。下面这个例子查找角色为 "User" 的所有用户:

```python
>>> User.query.filter_by(role=user_role).all() [<User u'susan'>, <User u'david'>]
```

若要查看 SQLAlchemy 为查询生成的原生 SQL 查询语句,只需把 query 对象转换成字 符串:

```python
>>> str(User.query.filter_by(role=user_role))
'SELECT users.id AS users_id, users.username AS users_username, users.role_id AS users_role_id FROM users WHERE :param_1 = users.role_id'
```

```python
>>> user_role = Role.query.filter_by(name='User').first()
```

filter_by() 等过滤器在 query 对象上调用,返回一个更精确的 query 对象。多个过滤器可以一起调用,直到获得所需结果。

常用的SQLAlchemy查询过滤器

| 过滤器         | 说明                         |
| ----------- | -------------------------- |
| filter()    | 把过滤器添加到原查询上,返回一个新查询        |
| filter_by() | 把等值过滤器添加到原查询上,返回一个新查询      |
| limit()     | 使用指定的值限制原查询返回的结果数量,返回一个新查询 |
| offset()    | 偏移原查询返回的结果,返回一个新查询         |
| order_by()  | 根据指定条件对原查询结果进行排序,返回一个新查询   |
| group_by()  | 根据指定条件对原查询结果进行分组,返回一个新查询   |

在查询上应用指定的过滤器后,通过调用 all() 执行查询,以列表的形式返回结果。除了 all() 之外,还有其他方法能触发查询执行。表 5-6 列出了执行查询的其他方法。

| 方法             | 说明                                      |
| -------------- | --------------------------------------- |
| all()          | 以列表形式返回查询的所有结果                          |
| first()        | 返回查询的第一个结果,如果没有结果,则返回 None              |
| first_or_404() | 返回查询的第一个结果,如果没有结果,则终止请求,返回404错误响应       |
| get()          | 返回指定主键对应的行,如果没有对应的行,则返回 None            |
| get_or_404()   | 返回指定主键对应的行,如果没找到指定的主键,则终止请求,返回 404 错误响应 |
| count()        | 返回查询结果的数量                               |
| paginate()     | 返回一个 Paginate 对象,它包含指定范围内的结果            |

关系和查询的处理方式类似。下面这个例子分别从关系的两端查询角色和用户之间的一对 多关系:

```python
>>> users = user_role.users
>>> users
[<User u'susan'>, <User u'david'>]
>>> users[0].role
<Role u'User'>
```

这个例子中的 user_role.users 查询有个小问题。执行 user_role.users 表达式时,隐含的 查询会调用 all() 返回一个用户列表。query 对象是隐藏的,因此无法指定更精确的查询 过滤器。就这个特定示例而言,返回一个按照字母顺序排序的用户列表可能更好。在示例 5-4 中,我们修改了关系的设置,加入了 lazy = 'dynamic' 参数,从而禁止自动执行查询。

```python
class Role(db.Model):
    # ...
    users = db.relationship('User', backref='role', lazy='dynamic')
    # ...
```

这样配置关系之后,user_role.users 会返回一个尚未执行的查询,因此可以在其上添加过 滤器:

```python
>>> user_role.users.order_by(User.username).all()
[<User u'david'>, <User u'susan'>]
>>> user_role.users.count()
2
```

## 5.9 在视图函数中操作数据库

```python
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
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))
```

对应的模板新版本如示例 5-6 所示

```html
{% extends "base.html" %}
{% import "bootstrap/wtf.html" as wtf %}

{% block title %}Flasky{% endblock %}

{% block page_content %}
<div class="page-header">
    <h1>Hello, {% if name %}{{ name }}{% else %}Stranger{% endif %}!</h1>
    {% if not known %}
    <p>Pleased to meet you!</p>
    {% else %}
    <p>Happy to see you again!</p>
    {% endif %}
</div>
{{ wtf.quick_form(form) }}
{% endblock %}
```

## 5.10 集成Python shell

我们可以做些配置,让 Flask-Script 的 shell 命令自动导入特定的对象。

若想把对象添加到导入列表中,我们要为 shell 命令注册一个 make_context 回调函数,如示例 5-7 所示。

```python
from flask.ext.script import Shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
```

make_shell_context() 函数注册了程序、数据库实例以及模型,因此这些对象能直接导入 shell:

```python
$ python hello.py shell
>>> app
<Flask 'app'>
>>> db
<SQLAlchemy engine='sqlite:////home/flask/flasky/data.sqlite'> >>> User
<class 'app.User'>
```

## 5.11 使用Flask-Migrate实现数据库迁移

仅当数据库表不存在时,Flask-SQLAlchemy 才会根据模型进行创建。因此,更新表的唯一 方式就是先删除旧表,不过这样做会丢失数据库中的所有数据。

更新表的更好方法是使用数据库迁移框架。源码版本控制工具可以跟踪源码文件的变化, 类似地,数据库迁移框架能跟踪数据库模式的变化,然后增量式的把变化应用到数据库中。

SQLAlchemy 的主力开发人员编写了一个迁移框架,称为 Alembic(https://alembic.readthedocs.org/en/latest/index.html)。除了直接使用 Alembic 之外,Flask 程序还可使用 Flask-Migrate (http://flask-migrate.readthedocs.org/en/latest/)扩展。这个扩展对 Alembic 做了轻量级包装,并集成到 Flask-Script 中,所有操作都通过 Flask-Script 命令完成。

### 5.11.1 创建迁移仓库

```python
(venv) $ pip install flask-migrate
```

配置 Flask-Migrate

```python
from flask.ext.migrate import Migrate, MigrateCommand # ...
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
```

为了导出数据库迁移命令,Flask-Migrate 提供了一个 MigrateCommand 类,可附加到 Flask- Script 的 manager 对象上。

在维护数据库迁移之前,要使用 init 子命令创建迁移仓库:

```python
(venv) $ python hello.py db init
```

这个命令会创建 migrations 文件夹,所有迁移脚本都存放其中。

>   数据库迁移仓库中的文件要和程序的其他文件一起纳入版本控制。

### 5.11.2 创建迁移脚本

在 Alembic 中,数据库迁移用迁移脚本表示。脚本中有两个函数,分别是 upgrade() 和 downgrade()。upgrade() 函数把迁移中的改动应用到数据库中,downgrade() 函数则将改动 删除。Alembic 具有添加和删除改动的能力,因此数据库可重设到修改历史的任意一点。

我们可以使用 revision 命令手动创建 Alembic 迁移,也可使用 migrate 命令自动创建。 手动创建的迁移只是一个骨架,upgrade() 和 downgrade() 函数都是空的,开发者要使用 Alembic 提供的 Operations 对象指令实现具体操作。自动创建的迁移会根据模型定义和数 据库当前状态之间的差异生成 upgrade() 和 downgrade() 函数的内容。

>   自动创建的迁移不一定总是正确的,有可能会漏掉一些细节。自动生成迁移 脚本后一定要进行检查。

migrate 子命令用来自动创建迁移脚本:

```python
(venv) $ python hello.py db migrate -m "initial migration"
```

### 5.11.3 更新数据库

检查并修正好迁移脚本之后,我们可以使用 db upgrade 命令把迁移应用到数据库中:

```python
(venv) $ python hello.py db upgrade
```

对第一个迁移来说,其作用和调用 db.create_all() 方法一样。但在后续的迁移中, upgrade 命令能把改动应用到数据库中,且不影响其中保存的数据。