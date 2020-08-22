import secrets
import os
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, StateForm
from app.models import User, State
from flask_login import login_user, current_user, logout_user, login_required
from apscheduler.schedulers.background import BackgroundScheduler
from app.toggleKettle import kettle

sched = BackgroundScheduler(daemon=True)
# TODO: add the path to the site.db for apscheduler
sched.add_jobstore('sqlalchemy', url='sqlite://///Users/user/Programs/site.db')
sched.start()

def kettleDemo():
    print("The Kettle Would be running!")
    sched.print_jobs()

def runKettle():
    kettle()
    print("Job Done")

@app.route("/")
@app.route("/home")
def home():
    events = State.query.all()
    print(events)
    return render_template('home.html', events=events)

@app.route("/about")
def about():
    return render_template("about.html", title='About  ')


@app.route("/register", methods=["POST","GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check username and password", 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125,125)

    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=["POST","GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/state", methods=["POST","GET"])
@login_required
def state():
    """
    add a new event
    """
    form = StateForm()
    events = State.query.all()
    days = ''
    event = None
    if form.validate_on_submit():
        if form.mon.data == True:
            days += 'mon,'
        if form.tue.data == True:
            days += 'tue,'
        if form.wed.data == True:
            days += 'wed,'
        if form.thu.data == True:
            days += 'thu,'
        if form.fri.data == True:
            days += 'fri,'
        if form.sat.data == True:
            days += 'sat,'
        if form.sun.data == True:
            days += 'sun,'
        if days != "":
            days = days[0:len(days)-1] # strip "," comma off of end of last day entry (so it is in usable data format)
            event_duplicate = State.query.filter_by(event_days=days, event_hour=form.hour.data, event_min=form.minute.data).first()
            if not event_duplicate:
                event = State(event_days=days, event_hour=form.hour.data, event_min=form.minute.data)
                db.session.add(event)
                db.session.commit()

                sched.add_job(runKettle, 'cron', id=str(event.id) ,day_of_week=str(days), hour=str(form.hour.data), minute=str(form.minute.data))

                sched.print_jobs()
                print(sched.get_jobs())
                flash('Event added!', 'success')
                return redirect(url_for('state'))
            else:
                flash("Event Already Exists, Please revise!", 'danger')
        else:
            flash("Error with request please check that it is valid", 'danger')
    return render_template('state.html', title='State', form=form, event=event, events=events)


@app.route("/state/<int:event_id>", methods=["POST","GET"])
@login_required
def event(event_id):
    """
    view an event on separate page based on it's id
    """
    event = State.query.get_or_404(event_id)
    return render_template('event.html', event=event)

@app.route("/state/delete/<int:event_id>", methods=["POST"])
@login_required
def delete_event(event_id):
    """
    deletes an event based on the id
    - deletes event in apscheduler table and State table
    """
    if bool(State.query.filter_by(id=event_id).first()):
        #delete job in State 
        State.query.filter_by(id=event_id).delete()
        db.session.commit()
        #delete apscheduler job
        sched.remove_job(event_id)
        flash('Job deleted!', 'info')
    else:
        flash('Error deleting Event. Event is not in database', 'danger')
    return redirect(url_for('state'))

@app.route("/state/delete/all", methods=["POST","GET"])
@login_required
def delete_all():
    """
    deletes all jobs from State Table and apscheduler table
    """
    #Delete apscheduler jobs
    jobs = sched.get_jobs()
    for job in jobs:
        job.remove()
    sched.print_jobs()
    #delete State table entries
    State.query.delete()
    db.session.commit()
    flash('All Jobs Deleted', 'info')
    return redirect(url_for('state'))

@app.route("/state/activate", methods=["POST","GET"])
@login_required
def activate_now():
    """
    page that allows the user to activate the kettle with the press of a button
    """
    return render_template('activate.html', title="activate now!")

@app.route("/state/activate/now", methods=["POST"])
@login_required
def activated():
    """
    activate the kettle at the press of a button
    """
    #TODO run this on a separate thread or using apscheduler
    runKettle()
    return render_template('activate.html', title="activate now!")