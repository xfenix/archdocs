from huey import RedisHuey
from redis import Redis
from rq import Queue


redis_connection = Redis(host="localhost", port=6379, db=3)

rq_queue = Queue("emails", connection=redis_connection)

huey_app = RedisHuey("fastapi_app", host="localhost", port=6379, db=4)


def enqueue_welcome_email(user_id: int) -> str:
    """Put a welcome email into the RQ queue."""
    return rq_queue.enqueue(send_welcome_email, user_id).id


def send_welcome_email(user_id: int) -> None:
    """Send a welcome email, executed by the rq worker."""


@huey_app.task()
def cleanup_expired_tokens() -> None:
    """Drop expired tokens, executed by the huey worker."""
