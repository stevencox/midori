import sys
from typing import List, Optional
from dataclasses import dataclass

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

@dataclass
class Switch(_Statement, ast_utils.AsList):
    name: List[Name]
    
@dataclass
class Link(_Statement):
    name: Value
    src: Value
    dst: Value
    cls: Optional[Name] = None
    delay: Optional[Name] = None
    bw: Optional[Name] = None

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

parser = Lark("""
    start: program

    program: statement+

    ?statement: controller | node | switch | link | up
              | ping | down

    controller: "controller" value
    node: "node" NAME "ip" ip_addr "image" value
    switch: "switch" name+
    cls: "cls" NAME
    delay: "delay" STRING
    bw: "bw" DEC_NUMBER
    link: "link" NAME "src" NAME "dst" NAME cls? delay? bw?
    up: "up"
    ping: value+
    down: "down"

    value: name | STRING | DEC_NUMBER
    name: NAME
    ip_addr: STRING

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
        return transformer.transform(tree)
