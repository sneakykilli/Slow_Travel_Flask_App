from app import app, db
from shots import Shots
from app import Trips, Results
from datetime import datetime, datetime, timedelta
import traceback


with app.app_context():
    shots = Shots()
    today = datetime.today().date()
    trips = Trips.query.all()

    # trip_22 = Trips.query.filter(Trips.id == 22).first()  # Fetch the specific instance using .first()
    # if trip_22:
    #     db.session.delete(trip_22)
    #     db.session.commit()
    #     print("Trip deleted successfully")
    # else:
    #     print("Trip with ID 22 not found")

    results = Results.query.all()
    upcoming_trips = []
    for trip in trips:
        date_from = datetime.strptime(trip.date_from, '%d/%m/%Y').date()
        if date_from >= today:
            upcoming_trips.append(trip)
        else:
            results = Results.query.filter(Results.trip_id == trip.id)
            for result in results:
                db.session.delete(result)
            db.session.commit()
    for upcoming_trip in upcoming_trips:
        try:
            shots.api_call(trip=upcoming_trip, Results=Results, db=db)
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


