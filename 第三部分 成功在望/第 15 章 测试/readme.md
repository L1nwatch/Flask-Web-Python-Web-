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



