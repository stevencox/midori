import ast
import os
from collections import deque
from midori.compiler import Compiler
from midori.utils import Resource
from typing import List, Dict
from midori.tests.utils import TestBase

'''
        Expr(
          value=Call(
            func=Attribute(
              value=Name(id='net', ctx=Load()),
              attr='addLink',
              ctx=Load()),
            args=[
              Name(id='src', ctx=Load()),
              Name(id='dst', ctx=Load())],
            keywords=[])),
'''

class Benchmark:
    def __init__(self):
        self.func_defs = []
        self.calls = []
        self.attributes = []
    def __repr__(self):
        return f"\nfuncs:{self.func_defs}\ncalls:{self.calls}\nattrs:{self.attributes}"
    
class ProgramVerifier(ast.NodeVisitor):

    def __init__(self) -> None:
        self.benchmark = Benchmark()
        self.assign = deque()
        
    def get_attribute_name(self, attr: ast.Attribute) -> str:
        print(ast.dump(attr, indent=2))
        if isinstance(attr, ast.Attribute):
            return f"{self.get_attribute_name(attr.value)}.{attr.attr}"
        elif isinstance(attr, ast.Name):
            return f"{attr.id}"
        else:
            print(f"---->ERROR: {call.func.__class__.__name__}")
            
    def get_call_name(self, call: ast.Call) -> str:
        return self.get_attribute_name(call.func)

    def visit_Assign(self, node) -> None:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple) and \
           isinstance(node.value, ast.Tuple):
            names = [ name.id for name in node.targets[0].elts ]
            values = []
            for name in node.value.elts:
                if isinstance(name, ast.Name):
                    values.append(name.id)
                elif isinstance(name, ast.Constant):
                    values.append(name.value)
                else:
                    values.append('?')
            stack = {}
            for index, value in enumerate(names):
                stack[value] = values[index]
            self.assign.append(stack)
            print(f"---------------> {stack}")

    def visit_Attribute(self, node) -> None:
        if not isinstance(node.value, ast.Attribute):
            self.benchmark.attributes.append(self.get_attribute_name(node))
        self.generic_visit(node)
        
    def visit_Call(self, node) -> None:
        call_name = self.get_call_name(node)
        if call_name in [ "net.addLink", "net.addDocker", "net.addSwitch" ]:
            stack = self.assign.pop() if self.assign else {}
            args = ",".join ([ f"{k}={v}" for k, v in stack.items() ])            
            self.benchmark.calls.append(f"{call_name}({args})")
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node) -> None:
        for expr in node.body:
            if isinstance(expr, ast.Assign):
                self.visit(expr.value)
        self.benchmark.func_defs.append(node.name)
        self.generic_visit(node)

class TestCompiler(TestBase):

    def get_expected(self) -> List[str]:
        return [            
            """d1 = context.add_container(
        name="d1",ip="10.0.0.251", image="ubuntu:trusty", mac="00:00:00:00:00:01",
        env={ },
        ports=[],
        port_bindings = {  },
        cmd=[])""",
            """d2 = context.add_container(
        name="d2",ip="10.0.0.252", image="ubuntu:trusty", mac="00:00:00:00:00:02",
        env={ },
        ports=[],
        port_bindings = {  },
        cmd=[])""",
            """s1 = context.add_switch(name="s1")""",
            """context.add_link(src=s1, dst=s2, cls=TCLink, delay="100ms", bw=int(1))""",
            """context.add_link(src=s2, dst=d2)""",
            """context.net.ping ([d1.node,d2.node])"""
        ]

    def test_compiler (self) -> None:
        source = self.form_example_path("net.midori")
        output = self.form_example_path("net.py")
        compiler = Compiler ()
        source_text = Resource.read_file(source)
        output_text = compiler.process (source=source_text)
        expected = self.get_expected()
        for expectation in expected:
            assert expectation in output_text
            
