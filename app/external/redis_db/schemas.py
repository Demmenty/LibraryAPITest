from datetime import timedelta
from typing import Optional

from pydantic import BaseModel as BaseSchema


class RedisData(BaseSchema):
    key: bytes | str
    value: bytes | str
    ttl: Optional[int | timedelta] = None  # seconds of life
