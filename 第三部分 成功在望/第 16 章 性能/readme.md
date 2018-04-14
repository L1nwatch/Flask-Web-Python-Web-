# 第 16 章 性能

## 16.1 记录影响性能的缓慢数据库查询

优化数据库有时很简单,只需添加更多的索引即 可;有时却很复杂,需要在程序和数据库之间加入缓存。大多数数据库查询语言都提供了 explain 语句,用来显示数据库执行查询时采取的步骤。从这些步骤中,我们经常能发现 数据库或索引设计的不足之处。

Flask-SQLAlchemy 提供了一个选项,可以记录请求中执行的与数据库查询相关的统计数字。在示例 16-1 中, 我们可以看到如何使用这个功能把慢于设定阈值的查询写入日志。

`app/main/views.py`:报告缓慢的数据库查询

```python
from flask.ext.sqlalchemy import get_debug_queries
@main.after_app_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
			current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (query.statement, query.parameters, query.duration,
    query.context))
	return response
```

这个功能使用 `after_app_request` 处理程序实现,它和 `before_app_request` 处理程序的工 作方式类似,只不过在视图函数处理完请求之后执行。Flask 把响应对象传给 `after_app_ request` 处理程序,以防需要修改响应。

`get_debug_queries()` 函数返回一个列表,其元素是请求中执行的查询。Flask-SQLAlchemy 记录的查询信息如表 16-1 所示。

| 名称           | 说明               |
| ------------ | ---------------- |
| statement    | SQL 语句           |
| parameters   | SQL 语句使用的参数      |
| `start_time` | 执行查询时的时间         |
| `end_time`   | 返回查询结果时的时间       |
| duration     | 查询持续的时间，单位为秒     |
| context      | 表示查询在源码中所处位置的字符串 |

`after_app_request` 处理程序遍历 `get_debug_queries()` 函数获取的列表，把持续时间比设定阈值长的查询写入日志。写入的日志被设为“警告”等级。如果换成“错误”等级，发现缓慢的查询时还会发送电子邮件。

默认情况下,`get_debug_queries()` 函数只在调试模式中可用。但是数据库性能问题很少发 生在开发阶段,因为开发过程中使用的数据库较小。因此,在生产环境中使用该选项才能 发挥作用。若想在生产环境中分析数据库性能,我们必须修改配置,如示例 16-2 所示。

`config.py`:启用缓慢查询记录功能的配置

```python
class Config:
    # ...
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 0.5
    # ...
```

`SQLALCHEMY_RECORD_QUERIES` 告诉 Flask-SQLAlchemy 启用记录查询统计数字的功能。缓慢查询的阈值设为 0.5 秒。这两个配置变量都在 Config 基类中设置,因此在所有环境中都可使用。

## 16.2 分析源码

性能问题的另一个可能诱因是高 CPU 消耗,由执行大量运算的函数导致。源码分析器能找出程序中执行最慢的部分。分析器监视运行中的程序,记录调用的函数以及运行各函数 所消耗的时间,然后生成一份详细的报告,指出运行最慢的函数。

>   分析一般在开发环境中进行。源码分析器会让程序运行得更慢,因为分析器 要监视并记录程序中发生的一切。因此我们不建议在生产环境中进行分析, 除非使用专为生产环境设计的轻量级分析器。

Flask 使用的开发 Web 服务器由 Werkzeug 提供,可根据需要为每条请求启用 Python 分析 器。示例 16-3 向程序中添加了一个新命令,用来启动分析器。

`manage.py`:在请求分析器的监视下运行程序

```python
@manager.command
def profile(length=25, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],profile_dir=profile_dir)
	app.run()
```

使用 `python manage.py profile` 启动程序后,终端会显示每条请求的分析数据,其中包 含运行最慢的 25 个函数。`--length` 选项可以修改报告中显示的函数数量。如果指定了 `--profile-dir` 选项,每条请求的分析数据就会保存到指定目录下的一个文件中。分析器 数据文件可用来生成更详细的报告,例如调用图。Python 分析器的详细信息请参阅官方文档(https://docs.python.org/2/library/profile.html)。

