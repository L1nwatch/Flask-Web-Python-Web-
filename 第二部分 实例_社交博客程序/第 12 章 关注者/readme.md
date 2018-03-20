# 第 12 章 关注者

## 12.1　再论数据库关系

数据库使用关系建立记录之间的联系。其中，一对多关系是最常用的关系类型，它把一个记录和一组相关的记录联系在一起。实现这种关系时，要在“多”这一侧加入一个外键，指向“一”这一侧联接的记录。

### 12.1.1　多对多关系

下面以一个典型的多对多关系为例，即一个记录学生和他们所选课程的数据库。很显然，你不能在学生表中加入一个指向课程的外键，因为一个学生可以选择多个课程，一个外键不够用。同样，你也不能在课程表中加入一个指向学生的外键，因为一个课程有多个学生选择。两侧都需要一组外键。
这种问题的解决方法是添加第三张表，这个表称为关联表。现在，多对多关系可以分解成原表和关联表之间的两个一对多关系。

这个例子中的关联表是 registrations，表中的每一行都表示一个学生注册的一个课程。

查询多对多关系要分成两步。若想知道某位学生选择了哪些课程，你要先从学生和注册之间的一对多关系开始，获取这位学生在 registrations 表中的所有记录，然后再按照多到一的方向遍历课程和注册之间的一对多关系，找到这位学生在 registrations 表中各记录所对应的课程。同样，若想找到选择了某门课程的所有学生，你要先从课程表中开始，获取其在 registrations 表中的记录，再获取这些记录联接的学生。

通过遍历两个关系来获取查询结果的做法听起来有难度，不过像前例这种简单关系，SQLAlchemy 就可以完成大部分操作。图 12-1 中的多对多关系使用的代码表示如下：

```python
registrations = db.Table('registrations',
 db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
 db.Column('class_id', db.Integer, db.ForeignKey('classes.id'))
)

class Student(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	classes = db.relationship('Class',secondary=registrations, backref=db.backref('students', lazy='dynamic'), lazy='dynamic')

class Class(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String)
```

多对多关系仍使用定义一对多关系的 `db.relationship()` 方法进行定义，但在多对多关系中，必须把 secondary 参数设为关联表。多对多关系可以在任何一个类中定义，backref 参数会处理好关系的另一侧。关联表就是一个简单的表，不是模型，SQLAlchemy 会自动接管这个表。

classes 关系使用列表语义，这样处理多对多关系特别简单。假设学生是 s，课程是 c，学生注册课程的代码为：

```python
>>> s.classes.append(c)
>>> db.session.add(s)
```

列出学生 s 注册的课程以及注册了课程 c 的学生也很简单：

```python
>>> s.classes.all()
>>> c.students.all()
```

Class 模型中的 students 关系由参数 `db.backref()` 定义。注意，这个关系中还指定了 `lazy= 'dynamic'` 参数，所以关系两侧返回的查询都可接受额外的过滤器。

如果后来学生 s 决定不选课程 c 了，那么可使用下面的代码更新数据库：

```python
>>> s.classes.remove(c)
```
### 12.1.2　自引用关系

如果关系中的两侧都在同一个表中，这种关系称为自引用关系。在关注中，关系的左侧是用户实体，可以称为“关注者”；关系的右侧也是用户实体，但这些是“被关注者”。

### 12.1.3　高级多对多关系

