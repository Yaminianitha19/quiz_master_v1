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
    return redirect(url_for('dashboard'))

@app.route('/home')
def home():
    return redirect(url_for('dashboard'))


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
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user= User.query.get(session['user_id'])
    if user.role != 'admin':
        subjects = Subject.query.all()
        return render_template('user_dashboard.html', current_user=user, subjects=subjects)
    else:
        subjects = Subject.query.all()
        return render_template('admin_dashboard.html', current_user=user, subjects=subjects)
   
    

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))




@app.route("/add_subject", methods=['GET', 'POST'])
def add_subject():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user= User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        description = request.form['description']
        subject = Subject(name=subject_name, description=description)
        db.session.add(subject)
        try:
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            db.session.rollback()
            flash('Subject name already exists. Please choose a different name.', 'error')
            return render_template('add_subject.html', current_user=user)
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Failed to add subject. Please try again.', 'error')
            return render_template('add_subject.html', current_user=user)
    return render_template('add_subject.html', current_user=user)

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user= User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        subject.name = request.form['subject_name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_subject.html', current_user=user, subject=subject)

@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user= User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user= User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        chapter_name = request.form['chapter_name']
        description = request.form['description']
        subject_id = request.form['subject_id']
        chapter = Chapter(name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_chapter.html', current_user=user, subjects=Subject.query.all())

if __name__ == '__main__':  
    with app.app_context():
        db.create_all()
        create_admin()

    
    app.run(debug=True)