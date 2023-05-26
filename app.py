from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Instantiate Flask App.
app = Flask(__name__)
app.secret_key = "my_secret_key"

# Bind app to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Instantiate the Database

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    trips = db.relationship("Trips", backref="email", lazy="dynamic")

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # ------- Creating Accounts and Authentication -------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Trips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fly_from = db.Column(db.String(140))
    fly_to = db.Column(db.String(140))
    date_from = db.Column(db.String(140))
    date_to = db.Column(db.String(140))
    stops = db.Column(db.Integer)
    budget = db.Column(db.Integer)
    planner = db.Column(db.String(140))
    timestamp = db.Column(db.String, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    results = db.relationship('Results', backref='trips', lazy='dynamic')

    def __repr__(self):
        return f"Trip from {self.fly_from} to {self.fly_to}"


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    price = db.Column(db.Integer, index=True)
    quality = db.Column(db.Integer, index=True)
    link = db.Column(db.Text, index=True)
    city_1 = db.Column(db.String)
    country_1 = db.Column(db.String)
    travel_time_1 = db.Column(db.Integer)
    city_2 = db.Column(db.String)
    country_2 = db.Column(db.String)
    travel_time_2 = db.Column(db.Integer)
    city_3 = db.Column(db.String)
    country_3 = db.Column(db.String)
    travel_time_3 = db.Column(db.Integer)
    city_4 = db.Column(db.String)
    country_4 = db.Column(db.String)
    travel_time_4 = db.Column(db.Integer)
    city_5 = db.Column(db.String)
    country_5 = db.Column(db.String)
    travel_time_5 = db.Column(db.Integer)
    city_6 = db.Column(db.String)
    country_6 = db.Column(db.String)
    travel_time_6 = db.Column(db.Integer)
    city_7 = db.Column(db.String)
    country_7 = db.Column(db.String)
    travel_time_7 = db.Column(db.Integer)
    city_8 = db.Column(db.String)
    country_8 = db.Column(db.String)
    travel_time_8 = db.Column(db.Integer)
    city_9 = db.Column(db.String)
    country_9 = db.Column(db.String)
    travel_time_9 = db.Column(db.Integer)
    city_10 = db.Column(db.String)
    country_10 = db.Column(db.String)
    travel_time_10 = db.Column(db.Integer)
    def __repr__(self):
        return f"Results {self.price} to {self.link}"

# with app.app_context():
#     db.create_all()
#
# if __name__ == '__main__':
#     app.run(debug=True)


