import sys
from typing import List, Optional
from dataclasses import dataclass, field

from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta

this_module = sys.modules[__name__]

#
#   Define AST
#
class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclass
class Value(_Ast, ast_utils.WithMeta):
    "Uses WithMeta to include line-number metadata in the meta attribute"
    meta: Meta
    value: object

@dataclass
class Name(_Ast):
    name: str

@dataclass
class Program(_Ast, ast_utils.AsList):
    # Corresponds to code_block in the grammar
    statements: List[_Statement]

@dataclass
class Controller(_Statement):
    value: Value

@dataclass
class RemoteController(Controller):
    host: Name
    port: Value
    
@dataclass
class IPAddr(Value):
    pass

@dataclass
class Image(Value):
    pass

@dataclass
class Node(_Statement):
    name: Name
    ip_addr: Value
    image: Value
    mac: Optional[Value] = None
    ports: Optional[Value] = field(default_factory=list)
    port_bindings: Optional[Value] = field(default_factory=list)
    env: Optional[Value] = field(default_factory=dict)
    cmd: Optional[Value] = None

@dataclass
class Switch(_Statement, ast_utils.AsList):
    name: List[Name]
    
@dataclass
class Link(_Statement):
    name: Value
    src: Value
    dst: Value
    port1: Optional[Value] = None
    port2: Optional[Value] = None
    cls: Optional[Value] = None
    delay: Optional[Value] = None
    bw: Optional[Value] = None

@dataclass
class Up(_Ast):
    pass

@dataclass
class Down(_Ast):
    pass

@dataclass
class Ping(_Statement, ast_utils.AsList):
    name: List[Name]
    
class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)

    @v_args(inline=True)
    def start(self, x):
        return x

#
#   Define Parser
#

#     link: "link" NAME "src" NAME "dst" NAME cls? delay? bw?

parser = Lark("""
    start: program

    program: statement+

    ?statement: control | node | switch | link | up | ping | down

    control: controller | remote_controller
    controller: "controller" value
    remote_controller: "remote_controller" value "host" STRING "port" DEC_NUMBER
    node: "node" NAME "ip" ip_addr "image" STRING ["mac" STRING] \
           ["ports" array] ["port_bindings" int_object] ["env" object] \
           ["cmd" array]
    switch: "switch" name+
    cls: "cls" NAME
    delay: "delay" STRING
    bw: "bw" DEC_NUMBER
    link: "link" NAME "src" NAME "dst" NAME \
           ["port1" DEC_NUMBER] ["port2" DEC_NUMBER] \
           ["cls" NAME ] ["delay" STRING] ["bw" DEC_NUMBER] 
    up: "up"
    ping: "ping" value+
    down: "down"

    value: name | STRING | DEC_NUMBER
    name: NAME
    ip_addr: STRING

    array  : "[" [value ("," value)*] "]"
    object : "{" [pair ("," pair)*] "}"
    pair   : string ":" value

    int_object : "{" [int_pair ("," int_pair)*] "}"
    int_pair   : DEC_NUMBER ":" DEC_NUMBER

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import python (NAME, STRING, DEC_NUMBER)
    %import common.WS
    %ignore WS
    """,
    parser="lalr",
)

""" Use Lark tools to build the abstract syntax tree. """
transformer = ast_utils.create_transformer(this_module, ToAst())

class Parser:
    """ The parser performs lexixal analysis, executes gammar productions,
    and generates the abstract syntax tree. """
    def parse(self, text: str) -> Program:
        tree = parser.parse(text)
        print(tree.pretty())
        return transformer.transform(tree)
