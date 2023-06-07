from app import app, db, User, Trips, Results
from flask import request, render_template, flash, redirect, url_for
from forms import RegistrationForm, LoginForm, DestinationForm
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.sql.expression import desc
from shots import Shots
import traceback
from config import GOOGLE_API_KEY


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password, please try again")
            return redirect(url_for('login'))
        login_user(user, form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # check if current_user logged in, if so redirect to a page that makes sense
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<email>', methods=['GET', 'POST'])
@login_required
def user(email):
    shots = Shots()
    user = current_user
    today = datetime.today().date()
    user = User.query.filter_by(email=user.email).first()
    trips = Trips.query.filter_by(user_id=user.id)
    upcoming_trips = []
    for trip in trips:
        date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
        if date_from >= today:
            upcoming_trips.append(trip)
    if trips is None:
        trips = []
    form = DestinationForm()
    if form.validate_on_submit():
        redirect(url_for('index'))
        planner_list = form.planner.data
        planner_str = ', '.join(planner_list)
        new_trip = Trips(fly_from=form.fly_from.data, fly_to=form.fly_to.data,
            date_from=form.date_from.data.strftime('%d/%m/%Y'), date_to=form.date_to.data.strftime('%d/%m/%Y'),
            stops=form.stops.data, budget=form.budget.data, planner=planner_str, user_id=user.id,
            timestamp=datetime.utcnow().strftime('%d/%m/%Y'))
        db.session.add(new_trip)
        db.session.commit()

        try:
            shots.api_call(trip=new_trip, Results=Results, db=db)
        except IndexError as e:
            traceback.print_exc()
            pass
        except KeyError as e:
            traceback.print_exc()
            pass
        except AttributeError as e:
            traceback.print_exc()
            pass
        except KeyboardInterrupt as e:
            traceback.print_exc()
            pass
    else:
        flash(form.errors)
    return render_template('user.html', user=user, trips=trips, form=form, today=today, upcoming_trips=upcoming_trips, API_KEY=GOOGLE_API_KEY)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user = current_user
    today = datetime.today().date()
    trips = Trips.query.filter_by(user_id=user.id)
    upcoming_trips = []
    for trip in trips:
        date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
        if date_from >= today:
            upcoming_trips.append(trip)
    sorted_upcoming_list = sorted(upcoming_trips, key=lambda x: datetime.strptime(x.date_from, "%d/%m/%Y"))
    trip_ids_list = [trip.id for trip in sorted_upcoming_list]
    if trips is None:
        trips = []
    results = Results.query.filter(Results.trip_id.in_(trip_ids_list)).order_by(Results.price.asc()).all()
    processed_results = {

    }
    filtered_results = Results.query.filter(Results.trip_id.in_(trip_ids_list)).order_by(Results.price.desc()).all()
    num_results = len(filtered_results)

    for t in trip_ids_list:
        list_container = []
        for r in results:
            if r.trip_id == t:
                list_container.append(r)
        processed_results[t] = list_container
    if not trips:
        trips = []

    return render_template('landing_page.html', trips=trips, results=results, upcoming_trips=upcoming_trips,
                           trip_ids_list=trip_ids_list, filtered_results=filtered_results,
                           processed_results=processed_results, num_results=num_results)






    return render_template('landing_page.html', trips=trips, results=results, upcoming_trips=upcoming_trips,
                           trip_ids_list=trip_ids_list, filtered_results=filtered_results,
                           processed_results=processed_results, num_results=num_results)
    # form = LoginForm()
    # try:
    #     user = current_user
    #     today = datetime.today().date()
    #     trips = Trips.query.filter_by(user_id=user.id)
    #     upcoming_trips = []
    #     for trip in trips:
    #         date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
    #         if date_from >= today:
    #             upcoming_trips.append(trip)
    #     sorted_upcoming_list = sorted(upcoming_trips, key=lambda x: datetime.strptime(x.date_from, "%d/%m/%Y"))
    #     trip_ids_list = [trip.id for trip in sorted_upcoming_list]
    #     if trips is None:
    #         trips = []
    #     results = Results.query.filter(Results.trip_id.in_(trip_ids_list)).order_by(Results.price.asc()).all()
    #     processed_results = {
    #
    #     }
    #     filtered_results = Results.query.filter(Results.trip_id.in_(trip_ids_list)).order_by(Results.price.desc()).all()
    #     num_results = len(filtered_results)
    #
    #     for t in trip_ids_list:
    #         list_container = []
    #         for r in results:
    #             if r.trip_id == t:
    #                 list_container.append(r)
    #         processed_results[t] = list_container
    #     if not trips:
    #         trips = []
    #
    #     return render_template('landing_page.html', trips=trips, results=results,
    #                            upcoming_trips=upcoming_trips, trip_ids_list=trip_ids_list,
    #                            filtered_results=filtered_results, processed_results=processed_results, num_results=num_results)
    # except:
    #     return redirect(url_for("login"))
    #     # return render_template('login.html', form=form)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = current_user
    form = DestinationForm()
    trip_to_update = Trips.query.filter(Trips.id == id).first()
    if form.validate_on_submit():
        trip_to_update.fly_from = form.fly_from.data
        trip_to_update.fly_to = form.fly_to.data
        trip_to_update.date_from = form.date_from.data.strftime('%d/%m/%Y')
        trip_to_update.date_to = form.date_to.data.strftime('%d/%m/%Y')
        trip_to_update.stops = form.stops.data
        trip_to_update.budget = form.budget.data
        planner_list = form.planner.data
        trip_to_update.planner = ', '.join(planner_list)
        try:
            db.session.commit()
            flash("Trip updated Successfully!")
            return redirect(url_for('index'))
        except:
            flash('Error! Looks like there was a problem, try again!')
            return render_template('update.html', form=form, trip_to_update=trip_to_update, id=id)
    else:
        return render_template('update.html', form=form, trip_to_update=trip_to_update, id=id)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
