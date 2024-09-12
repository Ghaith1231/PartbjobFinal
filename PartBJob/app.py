import os

import mysql.connector
from flask import Flask, render_template, redirect, session, send_from_directory
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from jobs import NewJobForm, SearchForm
from login import LoginForm
from profiles import StudentProfileForm, EmployerProfileForm
from signup import SignupForm

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'photos')
app.secret_key = 'fx(r8woJ=euk3^&h'

# Crate Bcrypt
bcrypt = Bcrypt(app)

# Connect to the database
cnx = mysql.connector.connect(user='ollydown_partb',
                              password='3O_t9AlvK0&i',
                              host='stout.hostns.io',
                              database='ollydown_partb')


@app.route('/')
def home():
    # show basic home page
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('type') is not None:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        # Get the user's input from the form
        email = form.email.data
        password = form.password.data

        # CConnect to database
        cursor = cnx.cursor(dictionary=True)

        # Get matching users from the database
        query = 'SELECT * FROM users WHERE email = %s'
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if user is not None:
            pw_hash = user['password']

            # Log user in if password matches hash
            if bcrypt.check_password_hash(pw_hash, password):
                session['id'] = user['id']
                session['type'] = user['type']
                return redirect('/dashboard')
            else:
                return redirect('/signup')
        else:
            return redirect('/signup')
    else:
        form = LoginForm()
        return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():


    cursor = cnx.cursor(dictionary=True)
    print(session['type'])

    if session['type'] == "s":
        form = StudentProfileForm()

        if form.validate_on_submit():

            query = 'UPDATE students SET first_name=%s, last_name=%s, phone=%s, education=%s, experience=%s, skills=%s WHERE user_id=%s'
            cursor.execute(query, (
                form.first_name.data,
                form.last_name.data,
                form.phone.data,
                form.education.data,
                form.experience.data,
                form.skills.data,
                session['id'],
            ))
            cnx.commit()

            # Photo Upload
            if form.delete_photo.data is True:
                #find current photo
                query = 'SELECT photo FROM students WHERE user_id=%s'
                cursor.execute(query,(session['id'],))

                photo = cursor.fetchone()
                photo = photo['photo']

                if photo is not None:
                    # dlete it from the folder
                    file = os.path.join(app.instance_path, 'photos', photo)
                    os.remove(file)

                # update our photo name
                query = 'UPDATE students SET photo=NULL WHERE user_id=%s'
                cursor.execute(query, (
                    session['id'],
                ))
                cnx.commit()
            elif form.photo.data is not None:
                # find current photo
                query = 'SELECT photo FROM students WHERE user_id=%s'
                cursor.execute(query, (session['id'],))

                photo = cursor.fetchone()

                # dlete it from the folder
                file = os.path.join(app.instance_path, 'photos', photo['photo'])
                os.remove(file)

                # save new photo
                photo = form.photo.data
                name = secure_filename(photo.filename)
                photo.save(os.path.join(app.instance_path, 'photos', name))

                # update our photo name
                query = 'UPDATE students SET photo=%s WHERE user_id=%s'
                cursor.execute(query, (
                    name,
                    session['id'],
                ))
                cnx.commit()

            return redirect('/profile')

        # Get matching users from the database
        query = 'SELECT * FROM students WHERE user_id = %s'
        cursor.execute(query, (session['id'],))

        student = cursor.fetchone()

        # populate existing data or make new
        if student is not None:
            form.first_name.data = student['first_name']
            form.last_name.data = student['last_name']
            form.phone.data = student['phone']
            form.education.data = student['education']
            form.experience.data = student['experience']
            form.skills.data = student['skills']
        else:
            # create user profile (blank)
            print("student is none")
            query = 'INSERT INTO students (user_id) VALUES (%s)'
            cursor.execute(query, (session['id'],))
            cnx.commit()

        return render_template('student-profile.html', form=form)
    # ----- EMPLOYERS -----
    elif session['type'] == "e":
        form = EmployerProfileForm()

        if form.validate_on_submit():
            print("valudate")
            query = 'UPDATE employers SET name=%s, email=%s, website=%s WHERE user_id=%s'
            cursor.execute(query, (
                form.name.data,
                form.email.data,
                form.website.data,
                session['id'],
            ))
            cnx.commit()

            # Photo Upload
            if form.delete_photo.data is True:
                # find current photo
                query = 'SELECT photo FROM employers WHERE user_id=%s'
                cursor.execute(query, (session['id'],))

                photo = cursor.fetchone()

                # dlete it from the folder
                file = os.path.join(app.instance_path, 'photos', photo['photo'])
                os.remove(file)

                # update our photo name
                query = 'UPDATE employers SET photo=NULL WHERE user_id=%s'
                cursor.execute(query, (
                    session['id'],
                ))
                cnx.commit()
            elif form.photo.data is not None:
                # find current photo
                query = 'SELECT photo FROM employers WHERE user_id=%s'
                cursor.execute(query, (session['id'],))

                photo = cursor.fetchone()
                photo = photo['photo']

                if photo is not None:
                    # dlete it from the folder
                    file = os.path.join(app.instance_path, 'photos', photo)
                    os.remove(file)

                    # save new photo
                photo = form.photo.data
                name = secure_filename(photo.filename)
                photo.save(os.path.join(app.instance_path, 'photos', name))

                # update our photo name
                query = 'UPDATE employers SET photo=%s WHERE user_id=%s'
                cursor.execute(query, (
                    name,
                    session['id'],
                ))
                cnx.commit()

            return redirect('/profile')

        # Get matching users from the database
        query = 'SELECT * FROM employers WHERE user_id = %s'
        cursor.execute(query, (session['id'],))

        employer = cursor.fetchone()

        if employer is not None:
            form.name.data = employer['name']
            form.email.data = employer['email']
            form.website.data = employer['website']
            form.photo.data = employer['photo']
        else:
            # create employer profile (blank)
            query = 'INSERT INTO employers (user_id) VALUES (%s)'
            cursor.execute(query, (session['id'],))
            cnx.commit()

        return render_template('employer-profile.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('type') is not None:
        return redirect("/")

    form = SignupForm()
    if form.validate_on_submit():
        # Register user when they submit the form
        email = form.email.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        type = form.type.data

        cursor = cnx.cursor()
        query = 'INSERT INTO users (email, password, type) VALUES (%s, %s, %s)'
        cursor.execute(query, (email, hashed_password, type))
        cnx.commit()
        cursor.close()
        return redirect('/login')
    else:
        return render_template("signup.html", form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = SearchForm()
    cursor = cnx.cursor(dictionary=True)

    if session.get('type') is None or session.get('type') == "s":
        results = None
        search = False

        if form.validate_on_submit():
            query = 'SELECT * FROM jobs WHERE MATCH(title, description) AGAINST(%s IN NATURAL LANGUAGE MODE);'
            cursor.execute(query, (form.search.data,))
            results = cursor.fetchall()
            search = True

        if results is None:
            query = 'SELECT * FROM jobs ORDER BY id DESC LIMIT 10'
            cursor.execute(query)
            results = cursor.fetchall()
            print(results)

        return render_template("student-dashboard.html", form=form, results=results, search=search)
    elif session['type'] == "e":
        results = []

        if form.validate_on_submit():
            query = 'SELECT * FROM students WHERE MATCH(education, experience, skills) AGAINST(%s IN NATURAL LANGUAGE MODE);'
            cursor.execute(query, (form.search.data,))
            results = cursor.fetchall()

        return render_template("employer-dashboard.html", form=form, results=results)


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    # search database for jobs
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT * FROM jobs WHERE employer_id=%s AND closed=FALSE'
    cursor.execute(query, (session['id'],))
    res = cursor.fetchall()

    return render_template('jobs.html', jobs=res)


@app.route('/newjob', methods=['GET', 'POST'])
def newjob():

    form = NewJobForm()
    if form.validate_on_submit():
        cursor = cnx.cursor()
        query = 'INSERT INTO jobs (employer_id, title, description) VALUES (%s, %s, %s)'
        cursor.execute(query, (session['id'], form.title.data, form.description.data))
        cnx.commit()
        cursor.close()
        return redirect('/dashboard')
    else:
        return render_template("newjob.html", form=form)


@app.route('/closejob/<id>', methods=['GET'])
def closejob(id):

    if id is not None:
        cursor = cnx.cursor()
        query = 'UPDATE jobs SET closed=TRUE WHERE employer_id=%s AND id=%s'
        cursor.execute(query, (session['id'], id))
        cnx.commit()
        cursor.close()

        return redirect('/jobs')


@app.route('/apply/<id>', methods=['GET'])
def apply(id):

    if id is not None:
        cursor = cnx.cursor(dictionary=True)

        # find student profile id
        query = 'SELECT id FROM students WHERE user_id=%s'
        cursor.execute(query, (session['id'],))
        sid = cursor.fetchone()

        # user must create profile first!
        if sid is None:
            return redirect("/profile")

        sid = sid['id']

        query = 'INSERT INTO applications (student_id,job_id) VALUES (%s, %s)'
        cursor.execute(query, (sid, id))
        cnx.commit()
        cursor.close()

        return redirect('/dashboard')


@app.route('/applications/<id>', methods=['GET'])
def applications(id):
    if id is not None:
        # get applications
        cursor = cnx.cursor(dictionary=True)
        query = 'SELECT student_id FROM applications WHERE job_id=%s'
        cursor.execute(query, (id,))

        res = cursor.fetchall()

        # get students
        apps = []

        for appl in res:
            query = 'SELECT * FROM students WHERE id=%s'
            cursor.execute(query, (appl['student_id'],))
            apps.append(cursor.fetchone())

        # get job
        query = 'SELECT * FROM jobs WHERE id=%s'
        cursor.execute(query, (id,))
        job = cursor.fetchone()

        return render_template("applications.html", apps=apps, job=job)
    else:
        return redirect("/jobs")


@app.route('/logout')
def logout():
    # user is logged out when session is removed
    session.clear()
    return redirect('/')


@app.route('/uploads/<filename>')
def serve_photo(filename):
    # serves images from flask resoources to user simply
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
