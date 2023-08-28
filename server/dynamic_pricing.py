from server.dtos import AllocationWithId
from shared.io import redis


def get_dynamic_pricing(allocation: AllocationWithId):
    if cached_price := redis.get(f"cached_popularity:{allocation.id}"):
        return float(cached_price)

    rank = redis.zrank("popularity", allocation.id)
    count = redis.zcard("popularity")

    if rank is None or count < 30:
        return allocation.base_price

    standardised_rank = (rank + 1) / count

    multiplier = standardised_rank * allocation.max_multiplier

    price = allocation.base_price * multiplier

    redis.set(f"cached_popularity:{allocation.id}", price, ex=60 * 30)

    return price
