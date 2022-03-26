import json
import jsonpickle
import redis
from midori.config import get_config
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge
from redis.commands.graph.path import Path
from redis.commands.graph import Graph
from typing import Dict, List, Union, Any
from string import Template

config = get_config()

class MidoriGraph:
    """ Interface to a graph database. To support experimentation with using
    Cypher as a DSL for manipulating data networks. """
    def __init__(self,
                 graph: str = config.get("redis", "graph"),
                 host: str = config.get("redis", "host"),
                 port: int = config.getint("redis", "port")) -> None:
        """ Initialze the graph.
        
        Args:
            graph (str): The name of the graph to create.
            host (str): The host Redis is on.
            port (int): The port Redis is listening on.

        """        
        redis_client = redis.Redis(host=host, port=port)
        self.graph = Graph(client=redis_client, name=graph)

    def add_node(self,
                 alias: str,
                 properties: Dict = {},
                 labels: List[str] = []
    ) -> Node:
        """ Create a graph node.
        
        Args:
            alias (str): A name for the node.
            properties (dict): Node properties. Values may be primitives or arrays.
            labels (list[str]): Labels describing the type of the node.
        Returns:
            Returns a Redisgraph Node object.
        """
        node = Node(alias=alias, label=labels, properties=properties)
        self.graph.add_node(node)
        return node

    def add_host(self, alias: str, properties: Dict = {}) -> Node:
        """ Create a host with appropriate labels. """
        return self.add_node(alias, properties, labels=["Host", "Node"])
    
    def add_switch(self, alias: str, properties: Dict = {}) -> Node:
        """ Create a swtich with appropriate labels. """
        return self.add_node(alias, properties, labels=["Switch", "Node"])
    
    def add_intent(self, alias: str, properties: Dict = {}) -> Node:
        """ Create an intent object with appropriate labels. """
        return self.add_node(alias, properties, labels=["Intent"])
    
    def add_edge(self,
                 subject: Node,
                 predicate: str,
                 object: Node,
                 properties: Dict = {}
    ) -> None:
        """ Create an edge linking subject and object via a predicate. """
        edge = Edge(subject, predicate, object, properties)
        self.graph.add_edge(edge)
        return edge

    def commit(self) -> None:
        """ Commit writes since the last commit.
        """
        self.graph.commit ()

    def query(self, query: str) -> Any:
        """ Query the database given a Cypher query. 

        Args:
            query (str): A cypher query.

        Returns:
            Returns a query result binding to names in the input query.
        """
        return self.graph.query(query)

    def get_shortest_path(self, src: str, dst: str) -> Any:
        """ Find the shortest path between two nodes where the names correspond to the input values.

        Args:
            src (str): The name of the source node.
            dst (str): The name of the destination node.
            
        Returns:
            Returns the result of a shortest path query.
        """
        query = Template(
            """MATCH (src:Host {name: "$src_name"}), (dst:Host {name: "$dst_name"})
            WITH src, dst
            MATCH p=allShortestPaths((src)-[link:visited*]->(dst))
            RETURN nodes(p) as nodes""").safe_substitute ({
                "src_name" : src,
                "dst_name" : dst
            })
        return self.graph.query(query)

    def clean(self) -> None:
        self.query("MATCH (n) DELETE n")
