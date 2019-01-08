import functools
from flask import (Blueprint, flash, g, redirect, render_template, url_for, request, session)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 注册视图 
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # 获取用户提交的表单信息
        username = request.form.get('username')
        password = request.form.get('password')
        # 连接数据库
        db = get_db()
        # 定义错误信息
        error = None
        # 逻辑判断    
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # 查询用户名是否已经存在    
        elif db.execute(
            'SELECT id FROM user WHERE username = ?',(username)
        ).fetchone() is not None:
            error = 'User {} is already registered'.format(username)
        # 用户提交表单信息经过验证后执行, 向数据库中插入数据, 对密码进行加密
        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            return redirect(url_for('autu.login'))
        # 将错误信息flash到下一个呈现的模板内, 模板中使用 get_flashed_messages 方法
        flash(error)

    return render_template('auth/register.html')

# 登录视图
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # 取出用户提交的form表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        # 连接数据库
        db = get_db()
        # 定义错误信息
        error = None
        # 在数据库中查询用户(execute方法 防止SQL注入)
        user = db.execute(
            'SELECT * FROM user WHERE username = ?' ,(username)
        ).fetchone()
        # 逻辑判断
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password): 
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        # 将错误信息flash 到下一次呈现的模板中 (get_flashed_message 方法)    
        flash(error)
    
    return render_template('auth/login.html')

# 在本次请求注册一个g.user对象 方便以后调用, 'g': 上下文中存储数据的一个对象
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id, )
        ).fetchone()

# 注销视图
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

 # 对是否登陆进行认证的装饰器
def login_required(view):
    # 保留装饰器装饰的函数的原始名字
    @functools.wraps(view)  
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view
