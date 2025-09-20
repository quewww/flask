from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

#连接数据库
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1:3306/quewww'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'production.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-1234567890'

db = SQLAlchemy(app)

#初始化LoginMananger
login_manager = LoginManager()      # 用户登录管理器
login_manager.login_view = 'login'  # 这个绿色的login是login函数
login_manager.init_app(app)         # 开始应用

# 定义用户模型, UserMixin提供用户模型的一些必要方法(直接写在这就继承过来了)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # 关联到Post数据库, backref可以使Post反向引用User模型, 里面的绿色字段可以随便命名, lazy表示需要时才加载关联数据
    posts = db.relationship('Post', backref='author_ref', lazy=True)

    #python会自动传递对象实例给self, self.能访问对象的属性和方法
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)   #主要作用是加密密码

    def check_password(self,password):
        return check_password_hash(self.password_hash,password) #解密密码, 这个和上面那个函数都是导入库提供的

# 定义文章模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), default='匿名')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #ForeignKey引用user里的id

    def __repr__(self):
        return f'<Post {self.title}>'

# 添加用户加载回调(((维持登录状态)))
@login_manager.user_loader                  # 注册用户加载器, 就是告诉Flask加载用户数据时调用下面这个函数
# 登录时浏览器会发送cookie到服务器, 后续用户访问新界面时Flask会从cookie中解密出用户ID, 然后调用这个函数, 维持登录状态
def load_user(user_id):
    return User.query.get(int(user_id))     # 返回用户对象

# 创建注册和登录路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first(): #filter_by相当于select * from... where ...
            return '用户名已存在'

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

        return '用户名或密码错误'
    return render_template('login.html')

# 退出登录
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():  # put application's code here
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')


# 创建文章
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        posts = Post(
            title = request.form['title'],
            content = request.form['content'],
            author = request.form['author'],
            user_id = current_user.id  #Flask提供的全局变量, 无需传递, 用户登录就能用
        )
        db.session.add(posts)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')

# 详情页
@app.route('/post/<int:post_id>')
def post(post_id):
    posts = Post.query.get_or_404(post_id)
    return render_template('post.html', post=posts)

#编辑页
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    posts = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        posts.title = request.form['title']
        posts.content = request.form['content']
        posts.author = request.form['author']

        db.session.commit()
        return redirect(url_for('post', post_id=posts.id))

    return render_template('edit.html',post=posts)

#删除页
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    posts = Post.query.get_or_404(post_id)
    db.session.delete(posts)
    db.session.commit()

    return redirect(url_for('index'))


#个人详情页
@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)



# 创建数据库表（只需要运行一次, 如果之后创建了更多的数据表要先输入python app.py才能运行flask run）
def init_db():
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")

if __name__ == '__main__':
    init_db()
    app.run()

