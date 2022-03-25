import importlib
import logging
import midori.runtime
import midori.messaging
import pytest
import redis
import sys
from collections import namedtuple
from starlette.testclient import TestClient
from midori.api import app
from midori.runtime import run_simulation, Host
from midori.messaging import Producer
from midori.utils import LoggingUtil

logger = logging.getLogger (__name__)

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client  # testing happens here

@pytest.fixture(scope="function")
def mock_producer(monkeypatch):

    class MockFuture:
        def get(self, timeout):
            return { "id" : 9 }
        
    class MockProducer:
        def __init__(self, value_serializer, bootstrap_servers, retries):
            pass
        def send(self, topic: str, value : object, key: str = None) -> None:
            logger.info(f"mock-producer-write():=> topic:{topic} value:{value} key:{key}")
            return MockFuture()
        
    monkeypatch.setattr('kafka.KafkaProducer', MockProducer)
    importlib.reload(midori.messaging)

@pytest.fixture(scope="function")
def mock_redis(monkeypatch):
    
    class MockRedis:
        def __init__(self, host, port):
            pass
        def get(self, key):
            return "asdfljlflkhkalhfksdhflkahfslkah"
        
    monkeypatch.setattr('redis.Redis', MockRedis)
    importlib.reload(redis)

@pytest.fixture(scope="function")
def mock_run_simulation(monkeypatch):
    
    def mock_simulation_response():
        return {
            "start_time" : "start",
            "end_time"   : "end",
            "error"      : "exception",
            "log"        : [ "context.messages" ]
        }
    
    monkeypatch.setattr(midori.runtime, "run_simulation", mock_simulation_response)

@pytest.fixture(scope="function")
def mock_mininet(monkeypatch):
    
    class ContainernetFactory:
        def get_containernet(self, *args, **kwargs):
            return MockContainernet()
        def cleanup_containernet (self):
            pass
        
    class MockContainernet:
        def addDocker(self, *args, **kwargs):
            FakeNode = namedtuple('FakeNode', 'name')
            return FakeNode(args[0])
        def addSwitch(self, *args, **kwargs):
            FakeNode = namedtuple('FakeNode', 'name')
            return FakeNode(args[0])
        def addLink(self, *args, **kwargs):
            pass
        def start(self, *args, **kwargs):
            pass
        def ping(self, *args, **kwargs):
            pass
        def stop(self, *args, **kwargs):
            pass
        
    def mock_get_containernet(controller_host, controller_port):
        return MockContainernet()
    monkeypatch.setattr("midori.runtime.ContainernetFactory", ContainernetFactory)
    print(f"monkeypatched runtime containernet.")
    
@pytest.fixture(scope="function")
def mock_graph(monkeypatch):
    class MockGraph:
        def __init__(self, *args):
            pass
        def add_node(self, *args):
            pass
        def add_edge(self, *args):
            pass
        def commit(self):
            pass
        def query(self, *args):
            pass
        def clean(self, *args):
            pass
    monkeypatch.setattr("redis.commands.graph.Graph", MockGraph)
    importlib.reload(midori.graph)
