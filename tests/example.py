import ast
import enum


def find_faststream_features(raw_source: str, _: ast.AST) -> {bool, bool}:
    consumer_found: bool = False
    producer_found: bool = False
    if "faststream" not in raw_source:
        return []
    if ".subscriber" in raw_source:
        consumer_found = True
    if ".producer" in raw_source:
        producer_found = True
    return {consumer_found, producer_found}


source_code = """
from pydantic import BaseModel, Field, PositiveInt
from faststream import FastStream
from faststream.kafka import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)

class User(BaseModel):
    user: str = Field(..., examples=["John"])
    user_id: PositiveInt = Field(..., examples=["1"])

@broker.subscriber("in")
@broker.publisher("out")
async def handle_msg(data: User) -> str:
    return f"User: {data.user} - {data.user_id} registered"
"""

# print(find_faststream_features(source_code, ast.parse(source_code)))


class DiagramOptions(enum.Enum):
    REST = "rest"
    MQ = "mq"
    DATABASES = "databases"


def generate_mermaid_diagram(service_name: str, options: list[DiagramOptions]):
    diagram = ["graph TD;"]
    diagram.append(f"    {service_name};")

    if DiagramOptions.REST in options:
        diagram.append(f"    User -- REST --> {service_name};")
        diagram.append(f"    {service_name} -- REST --> User;")

    if DiagramOptions.MQ in options:
        diagram.append(f"    User -- MQ --> {service_name};")
        diagram.append(f"    {service_name} -- MQ --> User;")

    if DiagramOptions.DATABASES in options:
        diagram.append(f"    {service_name} -- Redis --> RedisDB;")
        diagram.append(f"    {service_name} -- Postgres --> PostgresDB;")

    return "\n".join(diagram)
