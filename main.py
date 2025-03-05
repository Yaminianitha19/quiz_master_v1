from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

from models import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# the above line is to suppress a warning, not mandatory
db.init_app(app)

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(email='admin@quiz.com', password='password', full_name='Admin', role='admin')
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def index():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template('index.html', current_user=user)

@app.route('/home')
def home():
    return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = request.form['dob']
        dob = datetime.strptime(dob, '%Y-%m-%d').date()

        user = User(full_name=full_name, email=email, password=password, qualification=qualification, dob=dob)
        db.session.add(user)
        db.session.commit()

        flash('Signup successful! Please login to continue.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template('admin_dashboard.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()

    
    app.run(debug=True)