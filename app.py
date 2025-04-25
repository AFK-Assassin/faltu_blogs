from flask import Flask, request, render_template, redirect, session, url_for , flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
app.config["SECRET_KEY"] = "KIRA_BLOGS"
db = SQLAlchemy(app)

class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_blogs = Blog.query.all()
    return render_template("index.html", all_blogs=all_blogs)

@app.route('/register', methods=['GET', 'POST'])
def regestration():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_password = generate_password_hash(password=password)
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username, password=new_password)
            db.session.add(new_user)
            db.session.commit()
            flash('registration successfull' ,category= 'success')
            return redirect('/login')
        flash('wrong username or password ' ,category= 'danger')  
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = username
            flash('login successfull' , category='success')
            return redirect('/')
        flash('wrong username or password ' , category='danger')
    return render_template('login.html')

@app.route('/create-blog', methods=['GET', 'POST'])
def create_blog():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_blog = Blog(title=title, description=description, author=session['user'])
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/')
    return render_template("create_blog.html")

@app.route('/blog/<int:id>')
def view_blog(id):
    blog = Blog.query.get_or_404(id)
    return render_template('blog.html', blog=blog)

@app.route('/blog/<int:id>/delete', methods=['POST'])
def delete_blog(id):
    blog = Blog.query.get_or_404(id)
    if blog.author != session.get('user'):
        return "Unauthorized", 403
    db.session.delete(blog)
    db.session.commit()
    return redirect('/')

@app.route('/blog/<int:id>/update', methods=['GET', 'POST'])
def update_blog(id):
    blog = Blog.query.get_or_404(id)
    if blog.author != session.get('user'):
        return "Unauthorized", 403
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.description = request.form.get('description')
        db.session.commit()
        return redirect(f'/blog/{id}')
    return render_template('update_blog.html', blog=blog)

@app.route('/logout')
def Logout():
    session.pop('user')
    flash('logout successfull',category='info')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
