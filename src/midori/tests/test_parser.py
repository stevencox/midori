import ast
import os
from collections import defaultdict
from midori.parser import Parser
from midori.utils import Resource
from typing import List, Dict
from midori.tests.utils import TestBase

class TestParser(TestBase):

    def get_expected(self) -> Dict[str, List[str]]:
        return {
            "Controller" : [ "Controller(name='c0')" ],
            "Host" : [
                "Host(name='d1', ip_addr='10.0.0.251', image='ubuntu:trusty', mac='00:00:00:00:00:01', ports=[], port_bindings=[], env=[], cmd=[])",
                "Host(name='d2', ip_addr='10.0.0.252', image='ubuntu:trusty', mac='00:00:00:00:00:02', ports=[], port_bindings=[], env=[], cmd=[])"
            ],
            "Switch" : [ "Switch(name=['s1', 's2'])" ],
            "Link" : [
                "Link(name='l1', src='d1', dst='s1', port1=None, port2=None, cls=None, delay=None, bw=None)",
                "Link(name='l2', src='s1', dst='s2', port1=None, port2=None, cls='TCLink', delay='100ms', bw=1)",
                "Link(name='l3', src='s2', dst='d2', port1=None, port2=None, cls=None, delay=None, bw=None)"
            ],
            "Up" : [ "Up()"],
            "Down" : [ "Down()" ],
            "Ping" : [ "Ping(name=['d1', 'd2'])" ]
        }

    def test_parser(self) -> None:
        source = self.form_example_path("net.midori")
        source_text = Resource.read_file(source)

        parser = Parser()
        program: Program = parser.parse(source_text)

        map = defaultdict(lambda: [])
        for statement in program.statements:
            map[statement.__class__.__name__].append (statement)
            
        production_expected = self.get_expected()
        for production, expected in production_expected.items():
            actual = f"{map[production]}"
            print(f"""\
production:={production}
  expected:={expected}
    actual:={actual}""")
            for item in expected:                
                assert item in actual



            
            
