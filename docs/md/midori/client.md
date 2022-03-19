Module midori.client
====================

Functions
---------

    
`check_positive(value)`
:   

    
`main() ‑> None`
:   Process arguments.

Classes
-------

`MidoriClient(protocol: str = 'http', host: str = '127.0.0.1', port: int = 8000)`
:   Client for interacting with the Midori API. 
    
    Constructor. Configure API URI components.

    ### Methods

    `create_network(self, source: str, net_id: int = 0) ‑> Dict`
    :   Create a network given a source file, send it to the API, and track progress.

    `get_operation(self, name: str) ‑> str`
    :   Normalize the construction of URLs. 
        
        @param name: Name of the operation, path relative to the API URI.