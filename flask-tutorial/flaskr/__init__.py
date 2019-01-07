import os

from flask import Flask

def create_app(test_config=None):
    # 创建和设置app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
        )
    if test_config is None:
        # 加载默认配置,没有配置文件时
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载自定义的配置
        app.config.from_mapping(test_config)
    # 创建一个instance文件夹, 关于此应用的相关文件(如sqllite.db数据库文件等)    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 测试用,简单的路由(经典的Hello, World!)
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # 数据库相关
    from . import db
    db.init_app(app)    
    
    # 注册蓝图, auth认证模块(登录, 注册等)
    from . import auth 
    app.register_blueprint(auth.bp)

    return app