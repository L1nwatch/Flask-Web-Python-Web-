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

