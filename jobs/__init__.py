from typing import Any, List
from shared.io import celery, sqlite, email, redis
import shared.config as config
from celery.schedules import solar, crontab
from jobs.utils import online_average, base64img
from itertools import groupby
import matplotlib.pyplot as plt

celery.conf.beat_schedule = {
    "daily_reminder": {
        "task": "jobs.daily_reminder",
        "schedule": solar("sunset", 13.0827, 80.2707),  # evening in Chennai
    },
    "monthly_report": {"task": "jobs.monthly_report", "schedule": crontab(day_of_month=1)},
    "test": {"task": "jobs.heartbeat", "schedule": crontab()},  # every minute
}

celery.conf.timezone = "UTC"


@celery.task(ignore_result=True)
def heartbeat():
    return {"beat_status": "alive"}


@celery.task(ignore_result=True)
def async_email_sender(sender: str, receiver: str, subject: str, html: str):
    email(sender, receiver, subject, html)


@celery.task(ignore_result=True)
def daily_reminder():
    db = sqlite(readonly=True)
    for user in db.execute("select * from users").fetchall():
        if redis.exists(f"visited:{user.id}"):
            redis.delete(f"visited:{user.id}")
            continue
        subject = "Psst! You haven't visited TicketShow today!"
        sender = config.email_from
        receiver = user.email
        html = f"""
        <html>
            <body>
                <p>Hi {user.name},</p>
                <p> You haven't visited TicketShow today. Why not check out our latest shows?</p>
                <p><a href="{config.frontend_uri}">TicketShow</a></p>
            </body>
        </html>
        """
        # print(sender, receiver, subject, html)
        async_email_sender.delay(sender, receiver, subject, html)


@celery.task(ignore_result=True)
def monthly_report():
    db = sqlite(readonly=True)
    bookings = db.execute(
        """
        select
            b.id,
            u.name as user_name,
            u.email as email,
            v.id as venue_id,
            v.name as venue_name,
            s.id as show_id,
            s.name as show_name,
            a.time as show_time,
            b.quantity,
            b.rating
        from
            users u
            join bookings b on b.user_id = u.id
            join allocations a on b.allocation_id = a.id
            join shows s on a.show_id = s.id
            join venues v on a.venue_id = v.id
        where
            b.time >= date('now', '-1 month')
        order by u.email
        """
    ).fetchall()

    for email, data in groupby(bookings, lambda x: x.email):
        bookings: List[Any] = []
        for datum in data:
            booking = datum._asdict()
            booking["show_time"] = datum.show_time.replace(" ", "T")
            booking["link"] = config.frontend_uri + "/#/my-bookings/" + str(datum.id)
            booking["venue_link"] = config.frontend_uri + "/#/venues/" + str(datum.venue_id)
            booking["show_link"] = config.frontend_uri + "/#/shows/" + str(datum.show_id)
            bookings.append(booking)
        html = f"""
        <html>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Venue</th>
                        <th>Show</th>
                        <th>Quantity</th>
                        <th>Rating</th>
                    </tr>
                    {
                        chr(10).join([
                            f'''
                            <tr>
                                <td> <input readonly type=datetime-local value={booking['show_time']}> </td>
                                <td> <a href={booking['venue_link']}>{booking['venue_name']}</td>
                                <td> <a href={booking['show_link']}>{booking['show_name']}</td>
                                <td> {booking['quantity']} </td>
                                <td> {booking['rating']} </td>
                            </tr>
                            '''
                            for booking in bookings
                        ])
                    }
                </table>
        </html>
        """

        sender = config.email_from
        receiver = email
        subject = "Your monthly entertainment report!"
        async_email_sender.delay(sender, receiver, subject, html)


@celery.task(ignore_result=False)
def export_venue(venue_id: int):
    db = sqlite(readonly=True)
    stats = db.execute(
        """
        select
            coalesce(count(distinct a.id), 0) as total_allocations,
            coalesce(avg(b.quantity), 0) as average_booking_size,
            coalesce(count(b.id), 0) as total_bookings,
            coalesce(sum(b.quantity), 0) as total_tickets_sold,
            coalesce(avg(b.rating), 0) as average_rating,
            coalesce(avg(b.rating * b.quantity), 0) as weighted_average_rating
        from
            allocations a right join bookings b on a.id = b.allocation_id
        where
            a.venue_id = ?
        group by a.venue_id
        """,
        [venue_id],
    ).fetchone()

    average_filled_per_allocation = db.execute(
        """
        select
            a.id as allocation_id,
            s.name as show_name,
            round(coalesce(sum(b.quantity)*100.0/a.capacity, 0), 2) as percentage_filled
        from
            allocations a
            left join shows s on a.show_id = s.id
            left join bookings b on b.allocation_id = a.id
        where
            a.venue_id = ?
        group by a.id
        """,
        [venue_id],
    ).fetchall()

    week_over_week = db.execute(
        """
        select strftime('%W', b.time) as week, sum(b.gross_price) as earnings
        from bookings b join allocations a on b.allocation_id = a.id
        where a.venue_id = ?
        group by week
        order by week
        """,
        [venue_id],
    ).fetchall()

    average_filled_per_allocation = [
        datapoint._asdict() for datapoint in average_filled_per_allocation
    ]

    average_filled = online_average(
        datapoint["percentage_filled"] for datapoint in average_filled_per_allocation
    )

    x = [week.week for week in week_over_week]
    y = [week.earnings for week in week_over_week]

    fig = plt.figure(figsize=(10, 10))

    ax = fig.add_subplot(111)

    ax.plot(x, y)

    WoW = base64img(fig)

    data = {
        "total_allocations": stats.total_allocations,
        "average_booking_size": stats.average_booking_size,
        "total_bookings": stats.total_bookings,
        "total_tickets_sold": stats.total_tickets_sold,
        "average_rating": stats.average_rating,
        "weighted_average_rating": stats.weighted_average_rating,
        "average_percentage_filled_overall": average_filled,
        "average_percentage_filled_per_allocation": average_filled_per_allocation,
        "WoW": WoW,
    }

    return data
