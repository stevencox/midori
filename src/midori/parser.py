import logging
import random
import ipaddress
import sys
from dataclasses import dataclass, field
from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta
from midori.utils import LoggingUtil, Resource
from typing import List, Optional

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

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
    name: Name

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
class Host(_Statement):
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
class Intent(_Statement, ast_utils.AsList):
    name: List[Name]

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

    def NAME(self, item):
        return item.value
    
    def ip_addr(self, item):
        return item[0]
    
    def object(self, item):
        return item if item else {}

    def string(self, items):
        return str(items[0])

    def array(self, items):
        return [ item.value for item in items ]

    def pair(self, key_value):
        k, v = key_value
        return k, v.value

    def int_pair(self, key_value):
        k, v = key_value
        return int(k), int(v)

    def int_object(self, items):
        return items

class MACGenerator:
    
    def __init__(self):
        self.seed = [ 0, 0, 0, 0, 0, 0 ]
        self.cell = len(self.seed) - 1
        
    def next(self):
        if self.seed[self.cell] >= 255:
            if self.cell == 0:
                raise ValueError("MAC address range exceeded")
            else:
                self.cell -= 1
        self.seed[self.cell] += 1
        return "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(self.seed)
            
class IPGenerator:
    
    def __init__(self):
        self.pool = [ str(ip) for ip in ipaddress.IPv4Network('10.0.0.0/22') ]
        self.index = 0
        
    def next(self):
        self.index += 1
        if self.index >= len(self.pool):
            raise ValueError("The pool of random IP addresses has been exhausted.")
        return self.pool[self.index]

#
#   Define the Midori language's grammar productions.
#
parser = Lark("""
    start: program

    program: statement+

    ?statement: control | host | switch | link | intent | up | ping | down

    ?control: controller | remote_controller
    controller: "controller" value
    remote_controller: "remote_controller" NAME "host" STRING "port" DEC_NUMBER

    host: "host" NAME ["ip" ip_addr] "image" STRING ["mac" STRING] \
           ["ports" array] ["port_bindings" int_object] ["env" object] \
           ["cmd" array]

    switch: "switch" NAME+
    cls: "cls" NAME
    delay: "delay" STRING
    bw: "bw" DEC_NUMBER

    link: "link" NAME "src" NAME "dst" NAME \
           ["port1" DEC_NUMBER] ["port2" DEC_NUMBER] \
           ["cls" NAME ] ["delay" STRING] ["bw" DEC_NUMBER]

    ?intent: "intent" NAME "->" NAME ("->" NAME)* 

    up: "up"
    ping: "ping" NAME+
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

    COMMENT: /#.*/

    %import common.ESCAPED_STRING
    %import python (NAME, STRING, DEC_NUMBER)
    %import common.WS
    %ignore WS
    %ignore COMMENT
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
        logger.debug(tree.pretty())
        ast = transformer.transform(tree)
        """ Until we have a better way to ensure default values are set... """
        if ast:
            ip_generator = IPGenerator ()
            mac_generator = MACGenerator ()
            for statement in ast.statements:
                if isinstance(statement, Host):
                    statement.ip_addr = statement.ip_addr if statement.ip_addr else ip_generator.next()
                    statement.mac = statement.mac if statement.mac else mac_generator.next()
                    statement.env = statement.env if statement.env else []
                    statement.ports = statement.ports if statement.ports else []
                    statement.port_bindings = statement.port_bindings if statement.port_bindings else []
        return ast
