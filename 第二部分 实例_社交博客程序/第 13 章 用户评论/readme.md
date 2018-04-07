# 第 13 章 用户评论

## 13.1 评论在数据库中的表示

Comment 模型的定义如

```python
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
        db.event.listen(Comment.body, 'set', Comment.on_changed_body)
```

Comment 模型的属性几乎和 Post 模型一样,不过多了一个 disabled 字段。这是个布尔值字 段,协管员通过这个字段查禁不当评论。和博客文章一样,评论也定义了一个事件,在修 改 body 字段内容时触发,自动把 Markdown 文本转换成 HTML。转换过程和第 11 章中的 博客文章一样,不过评论相对较短,而且对 Markdown 中允许使用的 HTML 标签要求更严 格,要删除与段落相关的标签,只留下格式化字符的标签。为了完成对数据库的修改,User 和 Post 模型还要建立与 comments 表的一对多关系

```python
class User(db.Model):
    # ...
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    class Post(db.Model):
        # ...
        comments = db.relationship('Comment', backref='post', lazy='dynamic')
```

## 13.2 提交和显示评论

在 url_for() 函数的参数中把 page 设为 -1,这是个特殊的页 数,用来请求评论的最后一页,所以刚提交的评论才会出现在页面中。程序从查询字符串 中获取页数,发现值为 -1 时,会计算评论的总量和总页数,得出真正要显示的页数。

```python
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \ current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
        pagination = post.comments.order_by(Comment.timestamp.asc()).paginate( page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
        comments = pagination.items
        return render_template('post.html', posts=[post], form=form,
                               comments=comments, pagination=pagination)
```

指向评论页的链接结构也值得一说。这个链接的地址是在文章的固定链接后面加上一个 `#comments` 后缀。这个后缀称为 URL 片段,用于指定加载页面后滚动条所在的初始位置。 Web 浏览器会寻找 id 等于 URL 片段的元素并滚动页面,让这个元素显示在窗口顶部。

## 13.3 管理评论

这个模板将渲染评论的工作交给 `_comments.html` 模板完成,但把控制权交给从属模板之 前,会使用 Jinja2 提供的 set 指令定义一个模板变量 moderate,并将其值设为 True。这个 变量用在 `_comments.html` 模板中,决定是否渲染评论管理功能。

`_comments.html` 模板中显示评论正文的部分要做两方面修改。对于普通用户(没设定 moderate 变量),不显示标记为有问题的评论。对于协管员(moderate 设为 True),不管评 论是否被标记为有问题,都要显示,而且在正文下方还要显示一个用来切换状态的按钮。