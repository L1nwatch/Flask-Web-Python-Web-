# 第 9 章 用户角色

有多种方法可用于在程序中实现角色。具体采用何种实现方法取决于所需角色的数量和细 分程度。例如,简单的程序可能只需要两个角色,一个表示普通用户,一个表示管理员。 对于这种情况,在 User 模型中添加一个 is_administrator 布尔值字段就足够了。复杂的 程序可能需要在普通用户和管理员之间再细分出多个不同等级的角色。有些程序甚至不能 使用分立的角色,这时赋予用户某些权限的组合或许更合适。本章介绍的用户角色实现方式结合了分立的角色和权限,赋予用户分立的角色,但角色使 用权限定义。

## 9.1 角色在数据库中的表示

创建了一个简单的 roles 表,用来演示一对多关系。示例 9-1 是改进后的 Role 模型。

```python
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
```

只有一个角色的 default 字段要设为 True,其他都设为 False。用户注册时,其角色会被 设为默认角色。

这个模型的第二处改动是添加了 permissions 字段,其值是一个整数,表示位标志。各操 作都对应一个位位置,能执行某项操作的角色,其位会被设为 1。

参考：

| 操作          | 位值               | 说明            |
| ----------- | ---------------- | ------------- |
| 关注用户        | 0b00000001（0x01） | 关注其他用户        |
| 在他人的文章中发表评论 | 0b00000010（0x02） | 在他人撰写的文章中发布评论 |
| 写文章         | 0b00000100（0x04） | 写原创文章         |
| 管理他人发表的评论   | 0b00001000（0x08） | 查处他人发表的不当评论   |
| 管理员权限       | 0b10000000（0x80） | 管理网站          |

表 9-2 列出了要支持的用户角色以及定义角色使用的权限位。 

| 用户角色 | 权限               | 说明                            |
| ---- | ---------------- | ----------------------------- |
| 匿名   | 0b00000000（0x00） | 未登录的用户。在程序中只有阅读权限             |
| 用户   | 0b00000111（0x07） | 具有发布文章、发表评论和关注其他用户的权限。新用户默认角色 |
| 协管员  | 0b00001111（0x0f） | 增加审查不当评论的权限                   |
| 管理员  | 0b11111111（0xff） | 具有所有权限，包括修改其他用户所属角色的权限        |

使用权限组织角色,这一做法让你以后添加新角色时只需使用不同的权限组合即可。 将角色手动添加到数据库中既耗时又容易出错。作为替代,我们要在 Role 类中添加一个类方法,完成这个操作,如示例 9-3 所示。

insert_roles() 函数并不直接创建新角色对象,而是通过角色名查找现有的角色,然后再 进行更新。只有当数据库中没有某个角色名时才会创建新角色对象。如此一来,如果以后 更新了角色列表,就可以执行更新操作了。要想添加新角色,或者修改角色的权限,修改 roles 数组,再运行函数即可。注意,“匿名”角色不需要在数据库中表示出来,这个角色 的作用就是为了表示不在数据库中的用户。

## 赋予角色

管理员由保存在设置变量 FLASKY_ADMIN 中的电子邮件地址识别,只要这个电子 邮件地址出现在注册请求中,就会被赋予正确的角色。

如何在 User 模型的构造函数中完成这一操作：

```python
class User(UserMixin, db.Model):
    # ...
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first() if self.role is None:
                    self.role = Role.query.filter_by(default=True).first()
```

## 9.3 角色验证

为了简化角色和权限的实现过程,我们可在 User 模型中添加一个辅助方法,检查是否有指定的权限

```python
from flask.ext.login import UserMixin, AnonymousUserMixin
class User(UserMixin, db.Model):
    # ...
    def can(self, permissions):
        return self.role is not None and \
    (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
```

```python
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
    login_manager.anonymous_user = AnonymousUser
```

检查管理员权限的 功能经常用到,因此使用单独的方法 is_administrator() 实现。

出于一致性考虑,我们还定义了 AnonymousUser 类,并实现了 can() 方法和 is_administrator() 方法。这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类,并将其设为用户未登录时 current_user 的值。这样程序不用先检查用户是否登录,就能自由调用 current_user.can() 和 current_user.is_administrator()。

如果你想让视图函数只对具有特定权限的用户开放,可以使用自定义的修饰器。示例 9-6 实现了两个修饰器,一个用来检查常规权限,一个专门用来检查管理员权限。

```python
from functools import wraps
from flask import abort
from flask.ext.login import current_user
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
```

这两个修饰器都使用了 Python 标准库中的 functools 包,如果用户不具有指定权限,则返 回 403 错误码,即 HTTP“禁止”错误。

在模板中可能也需要检查权限,所以 Permission 类为所有位定义了常量以便于获取。为了 避免每次调用 render_template() 时都多添加一个模板参数,可以使用上下文处理器。上 下文处理器能让变量在所有模板中全局可访问。

修改方法如示例 9-7 所示。`app/main/__init__.py`:把 Permission 类加入模板上下文

```python
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
```