from collections import namedtuple
from dataclasses import dataclass, field
from fastapi import FastAPI
from midori.runtime import run_simulation, midori_job_exception_handler
from midori.config import MidoriConfig
from pydantic import BaseModel, BaseSettings
from pympler import summary, muppy
from redis import Redis
from rq import Queue
from rq.job import Job
from typing import Any, Optional
import json
import uvicorn

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

config = MidoriConfig ()
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
    def __init__(self, networks=None):
        self.jobs = []
        self.redis_q = Queue(
            connection=Redis(
                host=settings.redis_host,
                port=settings.redis_port))
        """ An RQ (Redis Queue) connection to Redis. """
        
context = Context()

@app.post("/network/queue", tags=["networks"])
async def create_network(network: NetworkSchema):
    """ Create a network simulation job. """
    """ Unescape JSON string. """
    network.source = json.loads(network.source)
    """ Enqueue the job for execution. """
    job = context.redis_q.enqueue(
        run_simulation,
        network,
        result_ttl=24 * 60 * 60)
    """ Remember this job """
    context.jobs.append (job)
    return job.id

@app.get("/network/result", tags=["networks"])
async def get_network_result(network_id):
    """ Get network simulation result. """
    job = Job.fetch(network_id, context.redis_q.connection)
    print(f"got job: {job} {job.id}")
    return job.result if job else None

@app.get("/network/failed", tags=["networks"])
async def get_failed():
    """ Get information about failed jobs. """

    """ todo: move memory profiling. """
    all_objects = muppy.get_objects()
    sum1 = summary.summarize(all_objects)
    summary.print_(sum1)

    return {
        j : Job.fetch(j, context.redis_q.connection)
        for j in context.redis_q.failed_job_registry.get_job_ids()
    }
    
@app.get("/network/list", tags=["networks"])
async def get_networks():
    """ Get all networks. """
    result = {}
    
    for j in context.jobs:
        print(f"{j.exc_info}")
        job = Job.fetch (j.id, context.redis_q.connection)
        result[job.id] = job.result        
    return result

if __name__ == "__main__":
    """ Run the API given the provided settings. """
    uvicorn.run(settings.midori_api_app,
                host=settings.midori_api_host,
                port=settings.midori_api_port,
                log_level=settings.log_level,
                reload=settings.reload)
