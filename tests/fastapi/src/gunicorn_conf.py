"""Gunicorn configuration used to serve the fastapi example in production."""

bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn_worker.UvicornWorker"
keyfile = "/etc/tls/tls.key"
certfile = "/etc/tls/tls.crt"
