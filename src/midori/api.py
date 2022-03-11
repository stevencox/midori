from collections import namedtuple
from dataclasses import dataclass, field
from fastapi import FastAPI
from midori.runtime import run_simulation, midori_job_exception_handler
from pydantic import BaseModel, BaseSettings
from redis import Redis
from rq import Queue
from rq.job import Job
from typing import Any, Optional
import json
import uvicorn

description = """
The Midori API compiles network representations into simulations. 🚀

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
            "description": "Operations on midori network specifications.",
        }
    ]
)

class NetworkSchema(BaseModel):
    """ Schema for a network. """
    id: int
    source: str = ''
    description: Optional[str] = None

class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    log_level: str = "debug"
    midori_api_app: str = "midori.api:app"
    midori_api_host: str = "0.0.0.0"
    midori_api_port: int = 8000
    reload: bool = True
    
settings = Settings()

class Context:
    """ The API's runtime data model. """
    def __init__(self, networks=None):
        self.jobs = []
        self.redis_q = Queue(
            connection=Redis(
                host=settings.redis_host,
                port=settings.redis_port))
        
context = Context()

@app.post("/network/", tags=["networks"])
def create_network(network: NetworkSchema):
    """ Create a network simulation job. """
    args = {
        "a" : network.id,
        "b" : network.source,
        "c" : network.description
    }
    context.jobs.append (
        context.redis_q.enqueue(
            f=run_simulation,
            args=(args,),
            result_ttl=24 * 60 * 60))
    return network

@app.get("/networks", tags=["networks"])
def get_networks():
    """ Get all networks. """
    result = {}
    
    for j in context.redis_q.failed_job_registry.get_job_ids():
        print (f"failed-job-> {j}")
        
    for j in context.jobs:
        print(f"{j.exc_info}")
        job = Job.fetch (j.id, context.redis_q.connection)
        result[job.id] = job.result        
    return result

if __name__ == "__main__":
    uvicorn.run(settings.midori_api_app,
                host=settings.midori_api_host,
                port=settings.midori_api_port,
                log_level=settings.log_level,
                reload=settings.reload)
