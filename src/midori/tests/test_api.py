import json
import logging
import pytest
from uuid import UUID
from midori.config import get_config
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from midori.api import app
from starlette.testclient import TestClient
from midori.utils import LoggingUtil

logger = logging.getLogger (__name__)

config = get_config()

@pytest.mark.asyncio
async def test_queue(test_app, mock_producer, mock_redis):
    source = """
    host x y z
    host a b c
    host m n o
    """
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            response = await ac.post(
                url="/network/queue",
                json={
                    "id" : "0",
                    "source" : json.dumps(source),
                    "description" : "description"
                })
            assert response.status_code == 200
            assert validate_uuid4(json.loads(response.text))

def validate_uuid4(uuid_string):

    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string 
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code, 
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a 
    # valid uuid4. This is bad for validation purposes.

    return val.hex == uuid_string
