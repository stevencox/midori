import json
import logging
import uvicorn
from collections import namedtuple
from dataclasses import dataclass, field
from fastapi import FastAPI
from midori.config import get_config
from midori.messaging import get_producer
from midori.utils import LoggingUtil
from pydantic import BaseModel, BaseSettings
from pympler import summary, muppy
from redis import Redis
from uuid import uuid4
from typing import Any, Optional
from fastapi.logger import logger
from fastapi.testclient import TestClient
import midori.messaging

logger = logging.getLogger (__name__)

description = """
The Midori API compiles network representations into simulations.

For background on Midori, see the GitHub [repository](https://github.com/stevencox/midori)

The API lets you submit networks for simulation. The alpha will support simulation with Containernet (a Mininet fork) and ONOS.

"""

app = FastAPI(
    title="Midori API",
    description=description,
    version="0.0.1",
    terms_of_service="https://github.com/stevencox/midori",
    contact={
        "name": "Steve Cox",
        "url": "https://www.linkedin.com/in/stevencscox/",
        "email": "stevencscox@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=[
        {
            "name": "networks",
            "description": "Midori network simulation operations.",
        }
    ]
)
""" Metadata describing the API. """

config = get_config ()
""" The environment configuration object. """

class NetworkSchema(BaseModel):
    """ Schema for a network. """

    """ A client provided identifier. """
    id: int

    """ Source code in Midori for the network. """
    source: str = ''

    """ An optional description of the network. """
    description: Optional[str] = None

class Settings(BaseSettings):
    """ FastAPI application settings. """
    redis_host: str = config.get("redis", "host")
    redis_port: int = config.getint("redis", "port")
    log_level: str = config.get("log", "level")
    midori_api_app: str = config.get("api", "app")
    midori_api_host: str = config.get("api", "host")
    midori_api_port: int = config.getint("api", "port")
    reload: bool = config.getboolean("api", "reload")
    
settings = Settings()
""" Settings values controlling the API's deployment behavior. """

class Context:
    """ The API's runtime data model. """
    def __init__(self):
        """ Construct a context supplying dat services used by the API. """
        self.producer = midori.messaging.get_producer ()
        """ Create a message producer for sending messages to workers. """
        self.cache = Redis(
            host=settings.redis_host,
            port=settings.redis_port)
        """ Connect to the Redis cache. """

class Services:
    def __init__(self) -> None:
        self.context = None
services = Services ()

""" Services used by the API. """
@app.on_event("startup")
async def startup_event():
    services.context = Context()
    
@app.post("/network/queue", tags=["networks"])
async def create_network(network: NetworkSchema):
    """ Create a network simulation job. """
    """ Unescape JSON string. """
    logger.info(network)
    network.source = json.loads(network.source)
    key = str(uuid4().hex)
    logger.debug(f"enqueue(key)=> {key}")
    services.context.producer.write (
        topic="simulation",
        value={
            "id" : key,
            "type" : "simulation",
            "source" : network.source,
            "description" : network.description
        })
    return key

@app.get("/network/result", tags=["networks"])
async def get_network_result(network_id):
    """ Get network simulation result. """
    value = services.context.cache.get(f"{network_id}.result")
    return json.loads(value) if value else None

@app.get("/network/list", tags=["networks"])
async def get_networks():
    """ Get all networks. """
    return {} # Replace with Redis and TTL'd object.

if __name__ == "__main__":
    """ Run the API given the provided settings. """
    uvicorn.run(settings.midori_api_app,
                host=settings.midori_api_host,
                port=settings.midori_api_port,
                log_level=settings.log_level,
                log_config=None,
                reload=settings.reload)
