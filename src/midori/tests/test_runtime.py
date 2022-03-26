import uuid
import json
from midori.runtime import run_simulation
from midori.utils import Resource, Code
from typing import List, Dict
from midori.tests.utils import TestBase

mock_mininet_modules = {
    "mininet.net" : """
class Containernet:
    def __init__(self, *args, **kwargs):
        pass
    def addController(self, *args, **kwargs):
        pass
""",
    "mininet.node" : """
class Node:
    def __init__(self, name):
        self.name = name
class Controller:
    def __init__(self, *args, **kwargs):
        pass
class RemoteController:
    def __init__(self, *args, **kwargs):
        pass
""",
    "mininet.cli" : """
class CLI:
    def __init__(self, *args, **kwargs):
        pass
""",
    "mininet.link" : """
class TCLink:
    def __init__(self, *args, **kwargs):
        pass
""",
    "mininet.log" : """
def setLogLevel(*args):
    pass
def info(*args):
    pass
"""
    }

class TestRuntime(TestBase):

    def test_runtime(self, mock_graph, mock_mininet, mock_onos) -> None:
        for name, source in mock_mininet_modules.items():
            print(f"compiling module: {name}")
            module = Code.importCode(code=source, name=name, add_to_sys_modules=1)
            
        source = self.form_example_path("net.midori")
        source_text = Resource.read_file(source)
        result = run_simulation({
            "id" : uuid.uuid4(),
            "source" : source_text,
            "description" : "text"
        })
        print(json.dumps(result, indent=2))
            
