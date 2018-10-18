from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12blogz34@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '12secretkey34'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body= db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id') )
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username= username
        self.password= password
        
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_list', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods= ['POST', 'GET'] )
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password != password:
            flash('Incorrect password', 'error')
            return redirect('/login')
        if not user:
            flash('User does not exist', 'error')
            return redirect('/login')
        if user and user.password == password:
            session['username']= username
            flash('Logged in')
            return redirect ('/newpost')
    
    return render_template('login.html')


@app.route('/signup',  methods= ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('User already exists', 'error')
            return redirect('/signup')

        if username == "" or password == "" or verify == "":
            flash('One or more fields have been left blank', 'error')
            return redirect('/signup')
        
        if len(username) > 20 or len(username)<3:      
            flash("Username length must be greater than 3 and less than 20", 'error')
            return redirect('/signup')
        else:
            for char in username:
                if char == " ":
                    flash(" No empty spaces allowed", 'error')
                    return redirect('/signup')
                      
        if len(password) >20 or len(password)<3:
            flash("Password length must be greater than 3 and less than 20", 'error')
            return redirect('/signup')
        else:
            for char in password:
                if char == " ":
                    flash(" No empty spaces allowed", 'error')
                    return redirect('/signup')
                
        if verify != password:
            flash("passwords do not match. Please re-enter", 'error')
            return redirect('/signup')
       
        if not existing_user and verify == password:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']= username
            flash('Welcome to Blogz! Lets Get Blogging!')
            return redirect ('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect ('/blog')
        


@app.route('/newpost', methods=['POST', 'GET'])
def add_blog():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        body = request.form['body']
        title = request.form['title']

        if body == '':
            flash('Please enter message in the body', 'error')
            return render_template('blog_add.html', body=body, title=title)

        if title == '':
            flash('Please enter a title for you blog', 'error')
            return render_template('blog_add.html', body=body, title=title)

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id={}'.format(new_blog.id))
        

    return render_template('blog_add.html')


@app.route('/blog', methods=['GET']) 
def blog_list():

    if request.args:
        if 'id' in request.args:
            blog_id = int(request.args.get('id'))
            blog = Blog.query.get(blog_id)
            return render_template('blog_page.html', blog = blog)

        if 'user' in request.args:
            user_id = int(request.args.get('user'))
            user= User.query.get(user_id)
            return render_template('user_page.html', user = user)
     
    else:
        blogs = Blog.query.all()
        return render_template('blog_list.html', blogs = blogs)


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)


if __name__ == '__main__':
    app.run()