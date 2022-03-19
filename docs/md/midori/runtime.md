Module midori.runtime
=====================

Functions
---------

    
`importCode(code: str, name: str = 'tmp', add_to_sys_modules: int = 0)`
:   code can be any object containing code -- string, file object, or
    compiled code object. Returns a new module object initialized
    by dynamically importing the given code and optionally adds it
    to sys.modules under the given name.

    
`midori_job_exception_handler(job, exc_type, exc_value, traceback)`
:   

    
`run_simulation(network)`
:   

Classes
-------

`Context(controller: midori.runtime.Controller, graph: midori.graph.MidoriGraph)`
:   An execution context for a Midori simulation. Provides acces to system 
    services including 
       * An SDN control plane
       * A graph database
       * Logging

    ### Methods

    `log(self, message)`
    :

`Controller(api_host: str, api_port: int, username: str = None, password: str = None)`
:   

    ### Descendants

    * midori.runtime.Onos

    ### Methods

    `get_api(self, api: str = '') ‑> str`
    :

`Device(ip: str, port: int)`
:   Model of a device, for the time being, used to model intents only.

`Intent(priority: int, ingress: midori.runtime.Device, egress: midori.runtime.Device, protocol: int, eth_type: str, dest_port: int)`
:   

`MidoriException(*args, **kwargs)`
:   A general error pertaining to a simulation has occurred.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * midori.runtime.MidoriExecutionError
    * midori.runtime.MidoriNetworkError

`MidoriExecutionError(*args, **kwargs)`
:   A simulation failed due to the failure of a computation or lack of computing resources.

    ### Ancestors (in MRO)

    * midori.runtime.MidoriException
    * builtins.Exception
    * builtins.BaseException

`MidoriNetworkError(*args, **kwargs)`
:   A simulation failed due to a network or communication error.

    ### Ancestors (in MRO)

    * midori.runtime.MidoriException
    * builtins.Exception
    * builtins.BaseException

`Onos(api_host: str = 'localhost', api_port: int = 8181, username: str = 'onos', password: str = 'rocks')`
:   

    ### Ancestors (in MRO)

    * midori.runtime.Controller

    ### Methods

    `calculate_intent(self, ingress_device: str, egress_device: str) ‑> None`
    :