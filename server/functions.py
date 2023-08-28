from typing import Any, cast

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import Response
from json import dumps as mkjson
from server.dtos import *
from server.dynamic_pricing import get_dynamic_pricing
from shared.io import sqlite, redis
import jobs
from server.utils import validate, remove_symbols
from server.auth import make_token, authenticate


def health(data: Any):
    return {"data": "OK"}


def register(data: Any):
    data, err = validate(Register, data)
    if not data:
        return {"error": err}

    db = sqlite()

    if db.execute("select id from users where email = :email", data).fetchone():
        return {"error": "User with email already exists"}

    data["password"] = generate_password_hash(data["password"])
    user = db.execute(
        "insert into users(name, email, password) values(:name, :email, :password) returning id, name, email",
        data,
    ).fetchone()

    db.commit()
    db.close()

    return {"data": user._asdict()}


def login(data: Any):
    data, err = validate(Login, data)
    if not data:
        return {"error": err}

    db = sqlite(readonly=True)
    user = db.execute("select * from users where email = :email", data).fetchone()

    if not user:
        return {"error": "User not found"}

    if user.is_banned:
        return {"error": "User banned"}

    print(generate_password_hash(data["password"]), user.password)
    if not check_password_hash(user.password, data["password"]):
        return {"error": "Invalid password"}

    token = make_token(user.id)

    return {"data": {"token": token}}


def me(data: Any):
    if not (user := authenticate(data)):
        return {"error": "Unauthorized"}

    return {"data": user._asdict()}


# Marker: Venues


def create_venue(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(Venue, data)
    if not data:
        return {"error": err}

    venue = db.execute(
        "insert into venues(name, description, image, city, address) values(:name, :description, :image, :city, :address) returning *",
        data,
    ).fetchone()

    db.commit()
    db.close()

    redis.delete("venues")

    return {"data": venue._asdict()}


def get_venues(data: Any):
    db = sqlite(readonly=True)

    data, err = validate(GetVenues, data)
    if not data:
        return {"error": err}

    where_clause = "where 1 = 1"
    cache_key = "venues"
    if data.get("id"):
        where_clause += " and id = :id"
        cache_key += str(data["id"])

    if cached := redis.get(cache_key):
        return Response('{"data":' + cached + "}", content_type="application/json")
    venues = db.execute(f"select * from venues {where_clause}", data).fetchall()

    json = mkjson([venue._asdict() for venue in venues])

    if venues:
        redis.set(cache_key, json)

    return '{"data":' + json + "}"


def update_venue(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(VenueWithId, data)
    if not data:
        return {"error": err}

    venue = db.execute(
        "update venues set name = :name, description = :description, image = :image, city = :city, address = :address where id = :id returning *",
        data,
    ).fetchone()
    db.commit()

    if not venue:
        return {"error": "Venue not found"}

    db.close()

    redis.delete(f"venue:{venue.id}")

    return {"data": venue._asdict()}


def delete_venue(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(DeleteVenue, data)
    if not data:
        return {"error": err}

    venue = db.execute("delete from venues where id = :id returning id", data).fetchone()

    if not venue:
        return {"error": "Venue does not exist"}

    db.commit()
    db.close()

    redis.delete(f"venue:{venue.id}")

    return {"data": "success"}


# Marker: Shows


def create_show(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(Show, data)
    if not data:
        return {"error": err}

    show = db.execute(
        "insert into shows(name, description, image, tags) values(:name, :description, :image, :tags) returning *",
        data,
    ).fetchone()

    db.commit()
    db.close()

    redis.delete("shows")

    return {"data": show._asdict()}


def get_shows(data: Any):
    db = sqlite(readonly=True)

    data, err = validate(GetShows, data)
    if not data:
        return {"error": err}

    where_clause = "where 1 = 1"
    cache_key = "shows"
    if data.get("id"):
        where_clause += " and id = :id"
        cache_key += str(data["id"])

    if cached := redis.get(cache_key):
        return Response('{"data":' + cached + "}", content_type="application/json")
    shows = db.execute(f"select * from shows {where_clause}", data).fetchall()

    json = mkjson([show._asdict() for show in shows])

    if shows:
        redis.set(cache_key, json)

    return '{"data":' + json + "}"


def update_show(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(ShowWithId, data)
    if not data:
        return {"error": err}

    show = db.execute(
        "update shows set name = :name, description = :description, image = :image,tags = :tags where id = :id returning *",
        data,
    ).fetchone()
    db.commit()

    if not show:
        return {"error": "Show not found"}

    db.close()

    redis.delete(f"show:{show.id}")

    return {"data": show._asdict()}


def delete_show(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(DeleteShow, data)
    if not data:
        return {"error": err}

    show = db.execute("delete from shows where id = :id returning id", data).fetchone()

    if not show:
        return {"error": "Show does not exist"}

    db.commit()
    db.close()

    redis.delete(f"show:{show.id}")

    return {"data": "success"}


def create_allocation(data: Any):
    db = sqlite()
    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(Allocation, data)
    if not data:
        return {"error": err}

    allocation = db.execute(
        """insert into allocations(venue_id, show_id, time, capacity, base_price, max_multiplier)
        values(:venue_id, :show_id, :time, :capacity, :base_price, :max_multiplier)
        returning *
        """,
        data,
    ).fetchone()

    db.commit()
    db.close()

    return {"data": allocation._asdict()}


def get_allocations(data: Any):
    db = sqlite(readonly=True)

    data, err = validate(GetAllocations, data)
    if not data:
        return {"error": err}

    where_clause = "where 1 = 1"
    cache_key = "allocations"
    if data.get("id"):
        where_clause += " and id = :id"
        cache_key += str(data["id"])
    if data.get("venue_id"):
        where_clause += " and venue_id = :venue_id"
        cache_key += "venue:" + str(data["venue_id"])
    if data.get("show_id"):
        where_clause += " and show_id = :show_id"
        cache_key += "show:" + str(data["show_id"])

    if cached := redis.get(cache_key):
        return Response('{"data":' + cached + "}", content_type="application/json")


    allocations = db.execute(
        f"select * from allocations {where_clause}",
        data,
    ).fetchall()

    data = [allocation._asdict() for allocation in allocations]

    json = mkjson(data)
    redis.set(cache_key, json)

    return '{"data":' + json + "}"


def get_filled_status(data: Any):
    db = sqlite(readonly=True)

    data, err = validate(GetFilledStatus, data)
    if not data:
        return {"error": err}

    status = db.execute(
        """
        select coalesce(sum(b.quantity), 0) as filled
        from allocations a join bookings b on a.id = b.allocation_id
        where a.id = :id
        group by a.id
        """,
        data,
    ).fetchone()

    if not status:
        return {"error": "Allocation not found"}

    return {"data": status._asdict()}


def get_price(data: Any):
    db = sqlite(readonly=True)
    data, err = validate(GetPrice, data)
    if not data:
        return {"error": err}

    allocation = db.execute("select * from allocations where id = :id", data).fetchone()

    if not allocation:
        return {"error": "Allocation not found"}

    return {"data": {"price": get_dynamic_pricing(allocation)}}


def update_allocation(data: Any):
    db = sqlite()
    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(AllocationWithId, data)
    if not data:
        return {"error": err}

    allocation = db.execute(
        """
        update allocations set venue_id = :venue_id, show_id = :show_id, time = :time,
        capacity = :capacity, base_price = :base_price, max_multiplier = :max_multiplier
        where id = :id
        returning *
        """,
        data,
    ).fetchone()
    db.commit()

    if not allocation:
        return {"error": "Allocation not found"}

    db.close()

    return {"data": allocation._asdict()}


def delete_allocation(data: Any):
    db = sqlite()

    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(DeleteAllocation, data)
    if not data:
        return {"error": err}

    allocation = db.execute("delete from allocations where id = :id returning id", data).fetchone()
    db.commit()

    if not allocation:
        return {"error": "Allocation does not exist"}

    db.close()

    return {"data": "success"}


def book(data: Any):
    db = sqlite()
    if not (user := authenticate(data)):
        return {"error": "Unauthorized"}

    data, err = validate(Booking, data)
    if not data:
        return {"error": err}

    with db:
        allocation = db.execute(
            "select * from bookable_allocations where id = :allocation_id", data
        ).fetchone()

        if not allocation:
            return {"error": "Show not found"}

        already_booked = (
            db.execute(
                "select coalesce(sum(quantity), 0) as cnt from bookings where allocation_id = :allocation_id",
                data,
            )
            .fetchone()
            .cnt
        )

        if already_booked + data["quantity"] > allocation.capacity:
            return {"error": "Not enough seats"}

        calculated_price: float = data["quantity"] * get_dynamic_pricing(allocation)

        if data["gross_price"] != calculated_price:
            print(data, calculated_price)
            return {"error": "The price of the show has changed, please book again."}

        data["user_id"] = user.id

        booking = db.execute(
            """insert into bookings(allocation_id, user_id, quantity, gross_price)
            values(:allocation_id, :user_id, :quantity, :gross_price) returning *
            """,
            data,
        ).fetchone()

    db.commit()
    db.close()

    redis.zincrby("popularity", booking.quantity, allocation.id)

    return {"data": booking._asdict()}


def my_bookings(data: Any):
    db = sqlite(readonly=True)

    if not (user := authenticate(data)):
        return {"error": "Unauthorized"}

    data, err = validate(MyBookings, data)
    if not data:
        return {"error": err}

    where_clause = "where user_id = :user_id"
    if data.get("id"):
        where_clause += " and id = :id"

    data["user_id"] = user.id
    bookings = db.execute(f"select * from bookings {where_clause}", data).fetchall()

    return {"data": [each._asdict() for each in bookings]}


def search(data: Any):
    q = data.get("q", "")

    q = remove_symbols(q)

    if not q:
        return cast(Any, {"data": {"venues": [], "shows": []}})

    db = sqlite(readonly=True)

    shows = db.execute("select rowid as id, * from shows_fts where shows_fts match ?", [q]).fetchall()
    venues = db.execute("select rowid as id, * from venues_fts where venues_fts match ?", [q]).fetchall()

    return {
        "data": {
            "venues": [each._asdict() for each in venues],
            "shows": [each._asdict() for each in shows],
        }
    }


def upsert_review(data: Any):
    db = sqlite()
    if not (user := authenticate(data)):
        return {"error": "Unauthorized"}

    data, err = validate(Review, data)
    if not data:
        return {"error": err}

    data["user_id"] = user.id
    review = db.execute(
        """
        update bookings set review = :review, rating = :rating
        where id = :booking_id and user_id = :user_id
        returning id, review, rating
        """,
        data,
    ).fetchone()
    db.commit()

    if not review:
        return {"error": "Booking not found"}

    db.close()

    return review._asdict()


def get_reviews(data: Any):
    db = sqlite(readonly=True)

    data, err = validate(GetReviews, data)
    if not data:
        return {"error": err}

    where_clause = "where 1 = 1"
    cache_key = "reviews"
    if data.get("id"):
        where_clause += "b.id = :id"
        cache_key += str(data["id"])
    if data.get("allocation_id"):
        where_clause += " and a.id = :allocation_id"
        cache_key += "allocation:" + str(data["allocation_id"])
    if data.get("venue_id"):
        where_clause += " and a.venue_id = :venue_id"
        cache_key += "venue:" + str(data["venue_id"])
    if data.get("show_id"):
        where_clause += " and a.show_id = :show_id"
        cache_key += "show:" + str(data["show_id"])

    if cached := redis.get(cache_key):
        return Response('{"data":' + cached + "}", content_type="application/json")

    reviews = db.execute(
        f"""
        select b.id, b.rating, b.review from bookings b left join allocations a on b.allocation_id = a.id
        {where_clause}
        """,
        data,
    ).fetchall()

    json = mkjson([review._asdict() for review in reviews])

    redis.set(cache_key, json)

    return '{"data":' + json + "}"


def delete_review(data: Any):
    db = sqlite()
    if not (user := authenticate(data)):
        return {"error": "Unauthorized"}

    data, err = validate(DeleteReview, data)
    if not data:
        return {"error": err}

    data["user_id"] = user.id
    review = db.execute(
        """
        update bookings set review = null, rating = null
        where id = :id and user_id = :user_id
        returning id, review, rating
        """,
        data,
    ).fetchone()
    db.commit()

    if not review:
        return {"error": "Booking not found"}

    db.close()
    return review._asdict()


def export_venue(data: Any):
    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}
    db = sqlite(readonly=True)

    data, err = validate(ExportVenue, data)
    if not data:
        return {"error": err}

    if not db.execute("select * from venues where id = :id", data).fetchone():
        return {"error": "Venue not found"}

    promise = jobs.export_venue.delay(data["id"])

    return {"data": {"promise_id": promise.id}}


def check_export_venue_status(data: Any):
    if not authenticate(data, require_admin=True):
        return {"error": "Unauthorized"}

    data, err = validate(Promise, data)
    if not data:
        return {"error": err}

    promise = jobs.export_venue.AsyncResult(data["promise_id"])

    return {
        "data": {
            "ready": promise.ready(),
            "success": promise.successful(),
            "result": promise.result if promise.ready() else None,
        }
    }
