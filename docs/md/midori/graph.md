Module midori.graph
===================

Classes
-------

`Host(name: str, environment: Dict)`
:   

    ### Ancestors (in MRO)

    * midori.graph.Node

`Link(src: midori.graph.Node, dst: midori.graph.Node)`
:   

`MidoriGraph(graph: str = 'midori', host: str = 'redis', port: int = 6379)`
:   Interface to a graph database. To support experimentation with using
    Cypher as a DSL for manipulating data networs. 
    
    Initialze the graph.
    
    @param graph: The name of the graph to create.
    @param host: The host Redis is on.
    @param port: The port Redis is listening on.

    ### Methods

    `commit(self) ‑> None`
    :

    `create_edge(self, link: midori.graph.Link) ‑> None`
    :

    `create_host(self, node: midori.graph.Host) ‑> redisgraph.node.Node`
    :

    `create_node(self, node: midori.graph.Node, label: Union[str, List] = []) ‑> redisgraph.node.Node`
    :   Create a node.

    `create_switch(self, node: midori.graph.Host) ‑> redisgraph.node.Node`
    :

    `get_shortest_path(self, src: str, dst: str)`
    :

    `query(self, query: str) ‑> Any`
    :

`Node(name: str)`
:   

    ### Descendants

    * midori.graph.Host
    * midori.graph.Switch

`Switch(name: str)`
:   

    ### Ancestors (in MRO)

    * midori.graph.Node