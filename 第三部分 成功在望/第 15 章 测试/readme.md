# 第 15 章 测试

## 15.1 获取代码覆盖报告

Python 提供了一个优秀的代码覆盖工具,称为 coverage,你可以使用 pip 进行安装: 

```shell
(venv) $ pip install coverage
```

它还提供了更方便的脚本访问功能,使用编程方式启动覆盖检查引擎。为了能更好地把覆 盖检测集成到启动脚本 manage.py 中,我们可以增强第 7 章中自定义的 test 命令,添加可 选选项 --coverage。这个选项的实现方式如示例 15-1 所示。

`manage.py`:覆盖检测

```python
#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
    # ...
    @manager.command
    def test(coverage=False):
        """Run the unit tests."""
        if coverage and not os.environ.get('FLASK_COVERAGE'):
            import sys
            os.environ['FLASK_COVERAGE'] = '1'
            os.execvp(sys.executable, [sys.executable] + sys.argv)
            import unittest
            tests = unittest.TestLoader().discover('tests')
            unittest.TextTestRunner(verbosity=2).run(tests)
            if COV:
                COV.stop()
                COV.save()
                print('Coverage Summary:')
                COV.report()
                basedir = os.path.abspath(os.path.dirname(__file__)) covdir = os.path.join(basedir, 'tmp/coverage') COV.html_report(directory=covdir)
                print('HTML version: file://%s/index.html' % covdir) COV.erase()
                # ...
```

在 Flask-Script 中,自定义命令很简单。若想为 test 命令添加一个布尔值选项,只需在 test() 函数中添加一个布尔值参数即可。Flask-Script 根据参数名确定选项名,并据此向函 数中传入 True 或 False。不过,把代码覆盖集成到 manage.py 脚本中有个小问题。test() 函数收到 `--coverage` 选项 的值后再启动覆盖检测已经晚了,那时全局作用域中的所有代码都已经执行了。为了检测 的准确性,设定完环境变量 FLASK_COVERAGE 后,脚本会重启。再次运行时,脚本顶端的代 码发现已经设定了环境变量,于是立即启动覆盖检测。

函数 `coverage.coverage()` 用于启动覆盖检测引擎。`branch=True` 选项开启分支覆盖分析, 除了跟踪哪行代码已经执行外,还要检查每个条件语句的 True 分支和 False 分支是否都执行了。include 选项用来限制程序包中文件的分析范围,只对这些文件中的代码进行覆盖检测。如果不指定 include 选项,虚拟环境中安装的全部扩展和测试代码都会包含进覆盖报告中,给报告添加很多杂项。

执行完所有测试后,text() 函数会在终端输出报告,同时还会生成一个使用 HTML 编写 的精美报告并写入硬盘。HTML 格式的报告非常适合直观形象地展示覆盖信息,因为它按 照源码的使用情况给代码行加上了不同的颜色。

## 15.2 Flask测试客户端

Flask 内建了一个测试客户端用于解决(至少部分解决)这一问题。测试客户端能复现程 序运行在 Web 服务器中的环境,让测试扮演成客户端从而发送请求。Flask 内建了一个测试客户端用于解决(至少部分解决)这一问题。测试客户端能复现程 序运行在 Web 服务器中的环境,让测试扮演成客户端从而发送请求。

### 15.2.1 测试Web程序

`tests/test_client.py`:使用 Flask 测试客户端编写的测试框架

```python
import unittest
from app import create_app, db
from app.models import User, Role
class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)
        def tearDown(self):
            db.session.remove()
            db.drop_all()
            self.app_context.pop()
            def test_home_page(self):
                response = self.client.get(url_for('main.index'))
                self.assertTrue('Stranger' in response.get_data(as_text=True))
```

如果创建测试客户端时启用了 use_cookies 选项,这个测试客户端就能像 浏览器一样接收和发送 cookie,因此能使用依赖 cookie 的功能记住请求之间的上下文。值 得一提的是,这个选项可用来启用用户会话,让用户登录和退出。

注意,默认 情况下 `get_data()` 得到的响应主体是一个字节数组,传入参数 as_text=True 后得到的是 一个更易于处理的 Unicode 字符串。

为了避免在测 试中处理 CSRF 令牌这一烦琐操作,最好在测试配置中禁用 CSRF 保护功能,如示例 15-3 所示。

config.py:在测试配置中禁用 CSRF 保护

```python
class TestingConfig(Config): #...
    WTF_CSRF_ENABLED = False
```

### 15.2.2 测试Web服务

Flask测试客户端还可用来测试REST Web服务。示例15-5是一个单元测试示例,包含了两个测试。

`tests/test_api.py`:使用 Flask 测试客户端测试 REST API

```python
class APITestCase(unittest.TestCase):
    # ...
    def get_api_headers(self, username, password):
        return {
            'Authorization':
            'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 401)

        def test_posts(self): # 添加一个用户
            r = Role.query.filter_by(name='User').first() self.assertIsNotNone(r)
            u = User(email='john@example.com', password='cat', confirmed=True,
                     ￼￼￼role=r)
            db.session.add(u)
            db.session.commit()
            # 写一篇文章
            response = self.client.post(
                url_for('api.new_post'),
                headers=self.get_auth_header('john@example.com', 'cat'),
                data=json.dumps({'body': 'body of the *blog* post'}))
            self.assertTrue(response.status_code == 201)
            url = response.headers.get('Location')
            self.assertIsNotNone(url)
            # 获取刚发布的文章 response = self.client.get(
            url,
            headers=self.get_auth_header('john@example.com', 'cat'))
            self.assertTrue(response.status_code == 200)
            json_response = json.loads(response.data.decode('utf-8'))
            self.assertTrue(json_response['url'] == url)
            self.assertTrue(json_response['body'] == 'body of the *blog* post')
            self.assertTrue(json_response['body_html'] ==
                            '<p>body of the <em>blog</em> post</p>')
```

## 15.3 使用Selenium进行端到端测试

Werkzeug Web 服务器本身就有停止选项,但由于服务器运行在单独的线程中,关闭服务器的唯一方法是 发送一个普通的 HTTP 请求。示例 15-6 实现了关闭服务器的路由。

`app/main/views.py`:关闭服务器的路由

```python
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
```

`tests/test_selenium.py`:使用 Selenium 运行测试的框架

```python
from selenium import webdriver
class SeleniumTestCase(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(cls):
	# 启动 Firefox
	try:
		cls.client = webdriver.Firefox()
	except:
		pass

	# 如果无法启动浏览器,则跳过这些测试
	if cls.client:
		# 创建程序
		cls.app = create_app('testing')
		cls.app_context = cls.app.app_context()
		cls.app_context.push()
		
		# 禁止日志,保持输出简洁
		import logging
		logger = logging.getLogger('werkzeug')
		logger.setLevel("ERROR")

		# 创建数据库,并使用一些虚拟数据填充
		db.create_all()
		Role.insert_roles()
		User.generate_fake(10)
		Post.generate_fake(10)

		# 添加管理员
		admin_role = Role.query.filter_by(permissions=0xff).first()

		admin = User(email='john@example.com', username='john', password='cat', role=admin_role, confirmed=True)
		db.session.add(admin)
		db.session.commit()

		# 在一个线程中启动 Flask 服务器
		threading.Thread(target=cls.app.run).start()


    @classmethod
    def tearDownClass(cls):
		if cls.client:
		# 关闭 Flask 服务器和浏览器
		cls.client.get('http://localhost:5000/shutdown')
		cls.client.close()

		# 销毁数据库
		db.drop_all()
		db.session.remove()

		# 删除程序上下文
		cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not available')

    def tearDown(self):
		pass
```

`tests/test_selenium.py`:Selenium 单元测试示例

```python
self.client.find_element_by_link_text('Log In').click()
self.client.find_element_by_name('email').send_keys('john@example.com')
```

## 15.4 值得测试吗



