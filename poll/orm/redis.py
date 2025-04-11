import redis.asyncio as redis

EXPIRATION_TIME = 60 * 60 * 48  # 48 hours


def redis_connection():
    return redis.Redis(host="rpi4db")


async def save_button_associated_key(redis_co: redis.Redis, button_key: str, element_key: str) -> None:
    await redis_co.set(button_key, element_key)
    await redis_co.expire(button_key, EXPIRATION_TIME)


async def get_button_associated_key(redis_co: redis.Redis, button_key: str) -> str:
    element_key = await redis_co.get(button_key)
    return element_key
