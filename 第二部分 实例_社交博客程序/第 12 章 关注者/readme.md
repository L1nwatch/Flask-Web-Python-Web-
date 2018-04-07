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

使用多对多关系时,往往需要存储所联两个实体之间的额外信息。对用户之间的关注来 说,可以存储用户关注另一个用户的日期,这样就能按照时间顺序列出所有关注者。这种 信息只能存储在关联表中,但是在之前实现的学生和课程之间的关系中,关联表完全是由 SQLAlchemy 掌控的内部表。

为了能在关系中处理自定义的数据,我们必须提升关联表的地位,使其变成程序可访问的 模型。

`app/models/user.py`：关注关联表的模型实现

```python
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

SQLAlchemy 不能直接使用这个关联表,因为如果这么做程序就无法访问其中的自定义字 段。相反地,要把这个多对多关系的左右两侧拆分成两个基本的一对多关系,而且要定义 成标准的关系。

`app/models/user.py`:使用两个一对多关系实现的多对多关系

```python
class User(UserMixin, db.Model):
    # ...
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
```

followed 和 followers 关系都定义为单独的一对多关系。注意,为了 消除外键间的歧义,定义关系时必须使用可选参数 `foreign_keys` 指定的外键。而且, `db.backref()` 参数并不是指定这两个关系之间的引用关系,而是回引 Follow 模型。

回引中的 lazy 参数指定为 joined。这个 lazy 模式可以实现立即从联结查询中加载相关对 象。

如果把 lazy 设为默认值 select,那么首次访问 follower 和 followed 属性时才会加载对应的用户, 而且每个属性都需要一个单独的查询,这就意味着获取全部被关注用户时需要增加 100 次 额外的数据库查询。

lazy 参数都在“一”这一侧设定, 返回的结果是“多”这一侧中的记录。上述代码使用的是 dynamic,因此关系属性不会直 接返回记录,而是返回查询对象,所以在执行查询之前还可以添加额外的过滤器。

cascade 参数配置在父对象上执行的操作对相关对象的影响。比如,层叠选项可设定为: 将用户添加到数据库会话后,要自动把所有关系的对象都添加到会话中。层叠选项的默认 值能满足大多数情况的需求,但对这个多对多关系来说却不合用。删除对象时,默认的层 叠行为是把对象联接的所有相关对象的外键设为空值。但在关联表中,删除记录后正确的 行为应该是把指向该记录的实体也删除,因为这样能有效销毁联接。这就是层叠选项值 delete-orphan 的作用。

>   cascade 参数的值是一组由逗号分隔的层叠选项,这看起来可能让人有 点困惑,但 all 表示除了 delete-orphan 之外的所有层叠选项。设为 all, delete-orphan 的意思是启用所有默认层叠选项,而且还要删除孤儿记录。

## 12.2 在资料页中显示关注者

## 12.3 使用数据库联结查询所关注用户的文章

若想显示所关注用户发布的所有文章,第一步显然先要获取这些用户,然后获取各用户的 文章,再按一定顺序排列,写入单独列表。可是这种方式的伸缩性不好,随着数据库不断 变大,生成这个列表的工作量也不断增长,而且分页等操作也无法高效率完成。获取博客 文章的高效方式是只用一次查询。

完成这个操作的数据库操作称为联结。联结操作用到两个或更多的数据表,在其中查找满 足指定条件的记录组合,再把记录组合插入一个临时表中,这个临时表就是联结查询的结 果。

使用 Flask-SQLAlchemy 执行 这个联结操作的查询相当复杂:

```python
return db.session.query(Post).select_from(Follow).\ filter_by(follower_id=self.id).\
join(Post, Follow.followed_id == Post.author_id)
```

你在此之前见到的查询都是从所查询模型的 query 属性开始的。这种查询不能在这里使用, 因为查询要返回 posts 记录,所以首先要做的操作是在 follows 表上执行过滤器。因此, 这里使用了一种更基础的查询方式。为了完全理解上述查询,下面分别说明各部分:

*   `db.session.query(Post)` 指明这个查询要返回 Post 对象;
*   `select_from(Follow)` 的意思是这个查询从 Follow 模型开始;
*   `filter_by(follower_id=self.id)` 使用关注用户过滤 follows 表;
*   `join(Post, Follow.followed_id == Post.author_id)` 联结 `filter_by()` 得到的结果和Post 对象。

调换过滤器和联结的顺序可以简化这个查询:

```python
return Post.query.join(Follow, Follow.followed_id == Post.author_id)\ .filter(Follow.follower_id == self.id)
```

如果首先执行联结操作,那么这个查询就可以从 Post.query 开始,此时唯一需要使用的两 个过滤器是 join() 和 filter()。但这两种查询是一样的吗?先执行联结操作再过滤看起 来工作量会更大一些,但实际上这两种查询是等效的。SQLAlchemy 首先收集所有的过滤 器,然后再以最高效的方式生成查询。这两种查询生成的原生 SQL 指令是一样的。

## 12.4 在首页显示所关注用户的文章

决定显示所有博客文章还是只显示所关注用户文章的选项存储在 cookie 的 show_followed 字段中,如果其值为非空字符串,则表示只显示所关注用户的文章。cookie 以 request. cookies 字典的形式存储在请求对象中。这个 cookie 的值会转换成布尔值,根据得到的值 设定本地变量 query 的值。

```python
@app.route('/', methods = ['GET', 'POST'])
def index():
    # ...
    show_followed = False
    if current_user.is_authenticated():
        show_followed = bool(request.cookies.get('show_followed', ''))
        if show_followed:
            query = current_user.followed_posts
            else:
                query = Post.query
                pagination = query.order_by(Post.timestamp.desc()).paginate(
                    page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                    error_out=False)
                posts = pagination.items
                return render_template('index.html', form=form, posts=posts,
                                       show_followed=show_followed, pagination=pagination)
```

`app/main/views.py`:查询所有文章还是所关注用户的文章

```python
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp
```

cookie 只能在响应对象中设置,因此这两个路由不能依赖 Flask,要使用 `make_response()` 方法创建响应对象。

`set_cookie()` 函数的前两个参数分别是 cookie 名和值。可选的 `max_age` 参数设置 cookie 的 过期时间,单位为秒。如果不指定参数 `max_age`,浏览器关闭后 cookie 就会过期。

虽然查询能按设计正常执行,但用户查看好友文章时还是希望能看到自己的文章。这个问 题最简单的解决办法是,注册时把用户设为自己的关注者。

创建函数更新数据库这一技术经常用来更新已部署的程序,因为运行脚本更新比手动更新 数据库更少出错。

```python
(venv) $ python manage.py shell
>>> User.add_self_follows()
```

用户关注自己这一功能的实现让程序变得更实用,但也有一些副作用。因为用户的自关注 链接,用户资料页显示的关注者和被关注者的数量都增加了 1 个。为了显示准确,这些数 字要减去1,这一点在模板中很容易实现,直接渲染 `{{ user.followers.count() - 1 }}` 和 `{{ user.followed.count() - 1 }}` 即可。然后,还要调整关注用户和被关注用户的列表,不显示自己。这在模板中也容易实现,使用条件语句即可。最后,检查关注者数量的单元 测试也会受到自关注的影响,必须做出调整,计入自关注。