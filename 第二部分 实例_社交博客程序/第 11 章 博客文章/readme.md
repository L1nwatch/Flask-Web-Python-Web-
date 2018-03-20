# 第 11 章 博客文章

## 11.1 提交和显示博客文章

博客文章包含正文、时间戳以及和 User 模型之间的一对多关系。

博客文章表单采取惯常处理方式，如果提交的数据能通过验证就创建一个新 Post 实例。在发布新文章之前，要检查当前用户是否有写文章的权限。

注意，新文章对象的 author 属性值为表达式 `current_user._get_current_object()`。变量 `current_user` 由 Flask-Login 提供，和所有上下文变量一样，也是通过线程内的代理对象实现。这个对象的表现类似用户对象，但实际上却是一个轻度包装，包含真正的用户对象。数据库需要真正的用户对象，因此要调用 `_get_current_object()` 方法。

```html
<div class="post-date">{{ moment(post.timestamp).fromNow() }}</div>
```

## 11.2 在资料页中显示博客文章

注意，`_posts.html` 模板名的下划线前缀不是必须使用的，这只是一种习惯用法，以区分独立模板和局部模板。

## 11.3 分页显示长博客文章列表

随着网站的发展，博客文章的数量会不断增多，如果要在首页和资料页显示全部文章，浏览速度会变慢且不符合实际需求。在 Web 浏览器中，内容多的网页需要花费更多的时间生成、下载和渲染，所以网页内容变多会降低用户体验的质量。这一问题的解决方法是分页显示数据，进行片段式渲染。

### 11.3.1 创建虚拟博客文章数据

有多个 Python 包可用于生成虚拟信息，其中功能相对完善的是 ForgeryPy，可以使用 pip 进行安装：

```shell
(venv) $ pip install forgerypy
```

严格来说，ForgeryPy 并不是这个程序的依赖，因为它只在开发过程中使用。为了区分生产环境的依赖和开发环境的依赖，我们可以把文件 requirements.txt 换成 requirements 文件夹，它们分别保存不同环境中的依赖。在这个新建的文件夹中，我们可以创建一个 `dev.txt` 文件，列出开发过程中所需的依赖，再创建一个 prod.txt 文件，列出生产环境所需的依赖。
由于两个环境所需的依赖大部分是相同的，因此可以创建一个 common.txt 文件，在 `dev.txt` 和 `prod.txt` 中使用 `-r` 参数导入。dev.txt 文件的内容如示例 11-7 所示。

`requirements/dev.txt`：开发所需的依赖文件

```shell
-r common.txt
ForgeryPy==0.1
```

示例 11-8 展示了添加到 User 模型和 Post 模型中的类方法，用来生成虚拟数据。

```python
class User(UserMixin, db.Model):
    # ...
 	@staticmethod
 	def generate_fake(count=100):
 		from sqlalchemy.exc import IntegrityError
 		from random import seed
 		import forgery_py
        
        seed()
 		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
					username=forgery_py.internet.user_name(True),
 					password=forgery_py.lorem_ipsum.word(),
					confirmed=True,
 					name=forgery_py.name.full_name(),
					location=forgery_py.address.city(),
					about_me=forgery_py.lorem_ipsum.sentence(),
 					member_since=forgery_py.date.date(True))
 			db.session.add(u)
 			try:
 				db.session.commit()
			except IntegrityError:
 				db.session.rollback()
```

```python
class Post(db.Model):
 	# ...
 	@staticmethod
    def generate_fake(count=100):
 		from random import seed, randint
 		import forgery_py
 		seed()
 		user_count = User.query.count()
 		for i in range(count):
 			u = User.query.offset(randint(0, user_count - 1)).first()
 			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
	 				timestamp=forgery_py.date.date(True),author=u)
 			db.session.add(p)
 			db.session.commit()
```

这些虚拟对象的属性由 ForgeryPy 的随机信息生成器生成，其中的名字、电子邮件地址、句子等属性看起来就像真的一样。
用户的电子邮件地址和用户名必须是唯一的，但 ForgeryPy 随机生成这些信息，因此有重复的风险。如果发生了这种不太可能出现的情况，提交数据库会话时会抛出 IntegrityError 异常。这个异常的处理方式是，在继续操作之前回滚会话。在循环中生成重复内容时不会把用户写入数据库，因此生成的虚拟用户总数可能会比预期少。

随机生成文章时要为每篇文章随机指定一个用户。为此，我们使用 offset() 查询过滤器。这个过滤器会跳过参数中指定的记录数量。通过设定一个随机的偏移值，再调用 first() 方法，就能每次都获得一个不同的随机用户。

### 11.3.2 在页面中渲染数据

示例 11-9 展示了为支持分页对首页路由所做的改动。

```python
page = request.args.get('page', 1, type=int)
```

渲染的页数从请求的查询字符串（request.args）中获取，如果没有明确指定，则默认渲染第一页。参数 `type=int` 保证参数无法转换成整数时，返回默认值。

为了显示某页中的记录，要把 all() 换成 Flask-SQLAlchemy 提供的 `paginate()` 方法。页数是 `paginate()` 方法的第一个参数，也是唯一必需的参数。可选参数 `per_page` 用来指定每页显示的记录数量；如果没有指定，则默认显示 20 个记录。另一个可选参数为 `error_out`，当其设为 True 时（默认值），如果请求的页数超出了范围，则会返回 404 错误；如果设为 False，页数超出范围时会返回一个空列表。为了能够很便利地配置每页显示的记录数量，参数 `per_page` 的值从程序的环境变量 `FLASKY_POSTS_PER_PAGE` 中读取。

### 11.3.3 添加分页导航

paginate() 方法的返回值是一个 Pagination 类对象，这个类在 Flask-SQLAlchemy 中定义。这个对象包含很多属性，用于在模板中生成分页链接，因此将其作为参数传入了模板。分页对象的属性简介如表 11-1 所示。

| 属性         | 说明             |
| ---------- | -------------- |
| items      | 当前页面中的记录       |
| query      | 分页的源查询         |
| page       | 当前页数           |
| `prev_num` | 上一页的页数         |
| `next_num` | 下一页的页数         |
| `has_next` | 如果有下一页，返回 True |
| `has_prev` | 如果有上一页，返回 True |
| pages      | 查询得到的总页数       |
| `per_page` | 每页显示的记录数量      |
| total      | 查询返回的记录总数      |

在分页对象上还可调用一些方法，如表 11-2 所示。

| 方法                                       | 说明                                       |
| ---------------------------------------- | ---------------------------------------- |
| `iter_pages`(`left_edge`=2,`left_current`=2,`right_current`=5,`right_edge`=2) | 一个迭代器，返回一个在分页导航中显示的页数列表。这个列表的最左边显示 `left_edge` 页，当前页的左边显示 `left_current` 页，当前页的右边显示 `right_current` 页，最右边显示 `right_edge` 页。例如，在一个 100 页的列表中，当前页为第 50 页，使用默认配置，这个方法会返回以下页数：1、2、None、48、49、50、51、52、53、54、55、None、99、100。None 表示页数之间的间隔 |
| prev()                                   | 上一页的分页对象                                 |
| next()                                   | 下一页的分页对象                                 |

拥有这么强大的对象和 Bootstrap 中的分页 CSS 类，我们很轻易地就能在模板底部构建一个分页导航。示例 11-10 是以 Jinja2 宏的形式实现的分页导航。

```html
{% macro pagination_widget(pagination, endpoint) %}
<ul class="pagination">
    <li{% if not pagination.has_prev %} class="disabled"{% endif %}>
        <a href="{% if pagination.has_prev %}{{ url_for(endpoint, page=pagination.prev_num, **kwargs) }}{% else %}#{% endif %}">
            &laquo;
        </a>
    </li>
    {% for p in pagination.iter_pages() %}
        {% if p %}
            {% if p == pagination.page %}
            <li class="active">
                <a href="{{ url_for(endpoint, page = p, **kwargs) }}">{{ p }}</a>
            </li>
            {% else %}
            <li>
                <a href="{{ url_for(endpoint, page = p, **kwargs) }}">{{ p }}</a>
            </li>
            {% endif %}
        {% else %}
        <li class="disabled"><a href="#">&hellip;</a></li>
        {% endif %}
    {% endfor %}
    <li{% if not pagination.has_next %} class="disabled"{% endif %}>
        <a href="{% if pagination.has_next %}{{ url_for(endpoint, page=pagination.next_num, **kwargs) }}{% else %}#{% endif %}">
            &raquo;
        </a>
    </li>
</ul>
{% endmacro %}
```

这个宏创建了一个 Bootstrap 分页元素，即一个有特殊样式的无序列表，其中定义了下述页面链接。

Jinja2 宏的参数列表中不用加入 `**kwargs` 即可接收关键字参数。分页宏把接收到的所有关键字参数都传给了生成分页链接的 url_for() 方法。这种方式也可在路由中使用，例如包含一个动态部分的资料页。
pagination_widget 宏可放在 index.html 和 user.html 中的 _posts.html 模板后面。示例 11-11 是它在程序首页中的应用。

`app/templates/index.html`：在博客文章列表下面添加分页导航

```html
{% extends "base.html" %}
{% import "bootstrap/wtf.html" as wtf %}
{% import "_macros.html" as macros %}

{% include '_posts.html' %}
{% if pagination %}
<div class="pagination">
    {{ macros.pagination_widget(pagination, '.index') }}
</div>
{% endif %}
```

## 11.4 使用Markdown和Flask-PageDown支持富文本文章

对于发布短消息和状态更新来说，纯文本足够用了，但如果用户想发布长文章，就会觉得在格式上受到了限制。本节我们要将输入文章的多行文本输入框升级，让其支持 Markdown（http://daringfireball.net/projects/markdown/）语法，还要添加富文本文章的预览功能。

实现这个功能要用到一些新包。
* PageDown：使用 JavaScript 实现的客户端 Markdown 到 HTML 的转换程序。
* Flask-PageDown：为 Flask 包装的 PageDown，把 PageDown 集成到 Flask-WTF 表单中。
* Markdown：使用 Python 实现的服务器端 Markdown 到 HTML 的转换程序。
* Bleach：使用 Python 实现的 HTML 清理器。

```shell
(venv) $ pip install flask-pagedown markdown bleach
```

### 11.4.1 使用Flask-PageDown

Flask-PageDown 扩展定义了一个 PageDownField 类，这个类和 WTForms 中的 TextAreaField 接口一致。使用 PageDownField 字段之前，先要初始化扩展，如示例 11-12 所示。

`app/__init__.py`：初始化 `Flask-PageDown`

```python
from flask.ext.pagedown import PageDown
# ...
pagedown = PageDown()
# ...
def create_app(config_name):
	# ...
	pagedown.init_app(app)
	# ...
```

若想把首页中的多行文本控件转换成 Markdown 富文本编辑器，PostForm 表单中的 body 字段要进行修改，如示例 11-13 所示。

```python
from flask.ext.pagedown.fields import PageDownField
class PostForm(Form):
	body = PageDownField("What's on your mind?", validators=[Required()])
 	submit = SubmitField('Submit')
```

Markdown 预览使用 PageDown 库生成，因此要在模板中修改。Flask-PageDown 简化了这个过程，提供了一个模板宏，从 CDN 中加载所需文件，如示例 11-14 所示

```html
{% block scripts %}
{{ super() }}
{{ pagedown.include_pagedown() }}
{% endblock %}
```

做了上述修改后，在多行文本字段中输入 Markdown 格式的文本会被立即渲染成 HTML 并显示在输入框下方。

### 11.4.2　在服务器上处理富文本

安全起见，只提交 Markdown 源文本，在服务器上使用 Markdown（使用 Python 编写的 Markdown 到 HTML 转换程序）将其转换成 HTML。得到 HTML 后，再使用 Bleach 进行清理，确保其中只包含几个允许使用的 HTML 标签。

把 Markdown 格式的博客文章转换成 HTML 的过程可以在 `_posts.html` 模板中完成，但这么做效率不高，因为每次渲染页面时都要转换一次。为了避免重复工作，我们可在创建博客文章时做一次性转换。转换后的博客文章 HTML 代码缓存在 Post 模型的一个新字段中，在模板中可以直接调用。

`app/models.py`：在 Post 模型中处理 Markdown 文本

```python
from markdown import markdown
import bleach
class Post(db.Model):
   # ...
   body_html = db.Column(db.Text)
   # ...
   @staticmethod
   def on_changed_body(target, value, oldvalue, initiator):
   		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),tags=allowed_tags, strip=True))
	db.event.listen(Post.body, 'set', Post.on_changed_body)
```

`on_changed_body` 函数注册在 body 字段上，是 SQLAlchemy“set”事件的监听程序，这意味着只要这个类实例的 body 字段设了新值，函数就会自动被调用。`on_changed_body` 函数把 body 字段中的文本渲染成 HTML 格式，结果保存在 `body_html` 中，自动且高效地完成 Markdown 文本到 HTML 的转换。

转换的最后一步由 `linkify()` 函数完成，这个函数由 Bleach 提供，把纯文本中的 URL 转换成适当的 `<a>` 链接。最后一步是很有必要的，因为 Markdown 规范没有为自动生成链接提供官方支持。PageDown 以扩展的形式实现了这个功能，因此在服务器上要调用 linkify() 函数。

渲染 HTML 格式内容时使用 `| safe` 后缀，其目的是告诉 Jinja2 不要转义 HTML 元素。出于安全考虑，默认情况下 Jinja2 会转义所有模板变量。Markdown 转换成的 HTML 在服务器上生成，因此可以放心渲染。

## 11.5　博客文章的固定链接

某些类型的程序使用可读性高的字符串而不是数字 ID 构建固定链接。除了数字 ID 之外，程序还为博客文章起了个独特的字符串别名。

```python
post = Post.query.get_or_404(id)
```

## 11.6　博客文章编辑器

与博客文章相关的最后一个功能是文字编辑器，它允许用户编辑自己的文章。博客文章编辑器显示在单独的页面中。在这个页面的上部会显示文章的当前版本，以供参考，下面跟着一个 Markdown 编辑器，用于修改 Markdown 源。这个编辑器基于 Flask-PageDown 实现，所以页面下部还会显示一个编辑后的文章预览。

`app/main/views.py`：编辑博客文章的路由

```python
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
   	form = PostForm()
   	if form.validate_on_submit():
   		post.body = form.body.data
   		db.session.add(post)
   		flash('The post has been updated.')
   		return redirect(url_for('post', id=post.id))
   	form.body.data = post.body
   	return render_template('edit_post.html', form=form)
```

这个视图函数的作用是只允许博客文章的作者编辑文章，但管理员例外，管理员能编辑所有用户的文章。如果用户试图编辑其他用户的文章，视图函数会返回 403 错误。这里使用的 PostForm 表单类和首页中使用的是同一个。