Module midori.parser
====================

Variables
---------

    
`parser`
:   Use Lark tools to build the abstract syntax tree.

Classes
-------

`Controller(value: midori.parser.Value)`
:   Controller(value: midori.parser.Value)

    ### Ancestors (in MRO)

    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast

    ### Descendants

    * midori.parser.RemoteController

    ### Class variables

    `value: midori.parser.Value`
    :

`Down()`
:   Down()

    ### Ancestors (in MRO)

    * midori.parser._Ast
    * lark.ast_utils.Ast

`IPAddr(meta: lark.tree.Meta, value: object)`
:   IPAddr(meta: lark.tree.Meta, value: object)

    ### Ancestors (in MRO)

    * midori.parser.Value
    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.WithMeta

`Image(meta: lark.tree.Meta, value: object)`
:   Image(meta: lark.tree.Meta, value: object)

    ### Ancestors (in MRO)

    * midori.parser.Value
    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.WithMeta

`Link(name: midori.parser.Value, src: midori.parser.Value, dst: midori.parser.Value, port1: Optional[midori.parser.Value] = None, port2: Optional[midori.parser.Value] = None, cls: Optional[midori.parser.Value] = None, delay: Optional[midori.parser.Value] = None, bw: Optional[midori.parser.Value] = None)`
:   Link(name: midori.parser.Value, src: midori.parser.Value, dst: midori.parser.Value, port1: Optional[midori.parser.Value] = None, port2: Optional[midori.parser.Value] = None, cls: Optional[midori.parser.Value] = None, delay: Optional[midori.parser.Value] = None, bw: Optional[midori.parser.Value] = None)

    ### Ancestors (in MRO)

    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast

    ### Class variables

    `bw: Optional[midori.parser.Value]`
    :

    `cls: Optional[midori.parser.Value]`
    :

    `delay: Optional[midori.parser.Value]`
    :

    `dst: midori.parser.Value`
    :

    `name: midori.parser.Value`
    :

    `port1: Optional[midori.parser.Value]`
    :

    `port2: Optional[midori.parser.Value]`
    :

    `src: midori.parser.Value`
    :

`Name(name: str)`
:   Name(name: str)

    ### Ancestors (in MRO)

    * midori.parser._Ast
    * lark.ast_utils.Ast

    ### Class variables

    `name: str`
    :

`Node(name: midori.parser.Name, ip_addr: midori.parser.Value, image: midori.parser.Value, mac: Optional[midori.parser.Value] = None, ports: Optional[midori.parser.Value] = <factory>, port_bindings: Optional[midori.parser.Value] = <factory>, env: Optional[midori.parser.Value] = <factory>, cmd: Optional[midori.parser.Value] = None)`
:   Node(name: midori.parser.Name, ip_addr: midori.parser.Value, image: midori.parser.Value, mac: Optional[midori.parser.Value] = None, ports: Optional[midori.parser.Value] = <factory>, port_bindings: Optional[midori.parser.Value] = <factory>, env: Optional[midori.parser.Value] = <factory>, cmd: Optional[midori.parser.Value] = None)

    ### Ancestors (in MRO)

    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast

    ### Class variables

    `cmd: Optional[midori.parser.Value]`
    :

    `env: Optional[midori.parser.Value]`
    :

    `image: midori.parser.Value`
    :

    `ip_addr: midori.parser.Value`
    :

    `mac: Optional[midori.parser.Value]`
    :

    `name: midori.parser.Name`
    :

    `port_bindings: Optional[midori.parser.Value]`
    :

    `ports: Optional[midori.parser.Value]`
    :

`Parser()`
:   The parser performs lexixal analysis, executes gammar productions,
    and generates the abstract syntax tree.

    ### Methods

    `parse(self, text: str) ‑> midori.parser.Program`
    :

`Ping(name: List[midori.parser.Name])`
:   Ping(name: List[midori.parser.Name])

    ### Ancestors (in MRO)

    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.AsList

    ### Class variables

    `name: List[midori.parser.Name]`
    :

`Program(statements: List[midori.parser._Statement])`
:   Program(statements: List[midori.parser._Statement])

    ### Ancestors (in MRO)

    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.AsList

    ### Class variables

    `statements: List[midori.parser._Statement]`
    :

`RemoteController(value: midori.parser.Value, host: midori.parser.Name, port: midori.parser.Value)`
:   RemoteController(value: midori.parser.Value, host: midori.parser.Name, port: midori.parser.Value)

    ### Ancestors (in MRO)

    * midori.parser.Controller
    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast

    ### Class variables

    `host: midori.parser.Name`
    :

    `port: midori.parser.Value`
    :

`Switch(name: List[midori.parser.Name])`
:   Switch(name: List[midori.parser.Name])

    ### Ancestors (in MRO)

    * midori.parser._Statement
    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.AsList

    ### Class variables

    `name: List[midori.parser.Name]`
    :

`ToAst(visit_tokens: bool = True)`
:   Transformers visit each node of the tree, and run the appropriate method on it according to the node's data.
    
    Methods are provided by the user via inheritance, and called according to ``tree.data``.
    The returned value from each method replaces the node in the tree structure.
    
    Transformers work bottom-up (or depth-first), starting with the leaves and ending at the root of the tree.
    Transformers can be used to implement map & reduce patterns. Because nodes are reduced from leaf to root,
    at any point the callbacks may assume the children have already been transformed (if applicable).
    
    ``Transformer`` can do anything ``Visitor`` can do, but because it reconstructs the tree,
    it is slightly less efficient.
    
    To discard a node, return Discard (``lark.visitors.Discard``).
    
    All these classes implement the transformer interface:
    
    - ``Transformer`` - Recursively transforms the tree. This is the one you probably want.
    - ``Transformer_InPlace`` - Non-recursive. Changes the tree in-place instead of returning new instances
    - ``Transformer_InPlaceRecursive`` - Recursive. Changes the tree in-place instead of returning new instances
    
    Parameters:
        visit_tokens (bool, optional): Should the transformer visit tokens in addition to rules.
                                       Setting this to ``False`` is slightly faster. Defaults to ``True``.
                                       (For processing ignored tokens, use the ``lexer_callbacks`` options)
    
    NOTE: A transformer without methods essentially performs a non-memoized partial deepcopy.

    ### Ancestors (in MRO)

    * lark.visitors.Transformer
    * lark.visitors._Decoratable
    * abc.ABC
    * typing.Generic

    ### Methods

    `DEC_NUMBER(self, n)`
    :

    `STRING(self, s)`
    :

    `start(self, x)`
    :

`Up()`
:   Up()

    ### Ancestors (in MRO)

    * midori.parser._Ast
    * lark.ast_utils.Ast

`Value(meta: lark.tree.Meta, value: object)`
:   Uses WithMeta to include line-number metadata in the meta attribute

    ### Ancestors (in MRO)

    * midori.parser._Ast
    * lark.ast_utils.Ast
    * lark.ast_utils.WithMeta

    ### Descendants

    * midori.parser.IPAddr
    * midori.parser.Image

    ### Class variables

    `meta: lark.tree.Meta`
    :

    `value: object`
    :