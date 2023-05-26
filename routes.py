from app import app, db, User, Trips, Results
from flask import request, render_template, flash, redirect, url_for
from forms import RegistrationForm, LoginForm, DestinationForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

@app.route('/login', methods=['GET', 'POST'])
def login():
  #check if current_user logged in, if so redirect to a page that makes sense
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email = form.email.data).first()
    if user is None or not user.check_password(form.password.data):
      flash("Invalid email or password")
      return redirect(url_for('login'))
    login_user(user, form.remember_me.data)
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != "":
      next_page = url_for("index")
    return redirect(next_page)
  return render_template('login.html', title = 'Sign In', form = form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  #check if current_user logged in, if so redirect to a page that makes sense
  if current_user.is_authenticated:
    return redirect(url_for("index"))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(
      email=form.email.data
    )
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))
  return render_template('register.html', title = 'Register', form = form)



@app.route('/user/<email>', methods = ['GET', 'POST'])
@login_required
def user(email):
  user = current_user
  today = datetime.today().date()
  user = User.query.filter_by(email = user.email).first()
  trips = Trips.query.filter_by(user_id = user.id)
  upcoming_trips = []
  for trip in trips:
      date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
      if date_from >= today:
          upcoming_trips.append(trip)
  if trips is None:
      trips = []
  form = DestinationForm()
  if form.validate_on_submit():
      planner_list = form.planner.data
      planner_str = ', '.join(planner_list)
      new_trip = Trips(
          fly_from = form.fly_from.data,
          fly_to= form.fly_to.data,
          date_from = form.date_from.data.strftime('%d/%m/%Y'),
          date_to = form.date_to.data.strftime('%d/%m/%Y'),
          stops = form.stops.data,
          budget = form.budget.data,
          planner = planner_str,
          user_id = user.id,
          timestamp = datetime.utcnow().strftime('%d/%m/%Y')
      )
      db.session.add(new_trip)
      db.session.commit()
  else:
      flash(form.errors)
  return render_template('user.html', user = user, trips = trips, form = form, today=today, upcoming_trips=upcoming_trips)


@app.route('/')
def index():
    user = current_user
    trips = Trips.query.filter_by(user_id=user.id)
    trip_ids = [trip.id for trip in trips]
    results = Results.query.filter(Results.trip_id.in_(trip_ids))
    if not trips:
        trips = []
    return render_template('landing_page.html', trips=trips, results=results)

@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)