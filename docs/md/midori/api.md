Module midori.api
=================

Functions
---------

    
`create_network(network: midori.api.NetworkSchema)`
:   Create a network simulation job.

    
`get_failed()`
:   Get information about failed jobs.

    
`get_network_result(network_id)`
:   Get network simulation result.

    
`get_networks()`
:   Get all networks.

Classes
-------

`Context(networks=None)`
:   The API's runtime data model.

`NetworkSchema(**data: Any)`
:   Schema for a network. 
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `description: Optional[str]`
    :

    `id: int`
    :   Source code in Midori for the network.

    `source: str`
    :   An optional description of the network.

`Settings(**values: Any)`
:   FastAPI application settings.

    ### Ancestors (in MRO)

    * pydantic.env_settings.BaseSettings
    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `log_level: str`
    :

    `midori_api_app: str`
    :

    `midori_api_host: str`
    :

    `midori_api_port: int`
    :   Reload the API when source changes.

    `redis_host: str`
    :

    `redis_port: int`
    :

    `reload: bool`
    :