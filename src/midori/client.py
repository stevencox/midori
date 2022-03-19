from midori.utils import Resource
import argparse
import json
import requests
import time
import logging
from typing import Dict
from midori.utils import LoggingUtil, Resource

LoggingUtil.setup_logging ()

logger = logging.getLogger ("midori.client")

class MidoriClient:    
    """ Client for interacting with the Midori API. """
    
    def __init__(self, protocol: str="http", host: str="127.0.0.1", port: int=8000) -> None:
        """ Constructor. Configure API URI components. """
        self.protocol=protocol
        self.host=host
        self.port = port
        
    def get_operation(self, name: str) -> str:
        """ Normalize the construction of URLs. 

        @param name: Name of the operation, path relative to the API URI."""        
        return f"{self.protocol}://{self.host}:{self.port}/{name}"

    def create_network(self, source: str, net_id: int=0) -> Dict:
        """ Create a network given a source file, send it to the API, and track progress. """
        network = Resource.read_file(source)

        url = self.get_operation("network/queue")
        print (f"--------> {url}")
        job_id = requests.post (
            url=self.get_operation("network/queue"),
            json={
                "id" : net_id,
                "source" : json.dumps(network),
                "description" : "Source for an emulated network."
            }).json ()
    
        logger.debug("Queued network simulation job {source} with job_id {job_id} for execution.")
        start = time.time ()
        result = None
        while True:
            result = requests.get (
                url=self.get_operation(f"network/result?network_id={job_id}")).json ()
            now = time.time ()
            if result or now - start > 60:
                break
            time.sleep (5)
        
        return result

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue

def main() -> None:
        
    """ Process arguments. """
    arg_parser = argparse.ArgumentParser(
        description='Midori Client',
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog,
            max_help_position=180))
    
    arg_parser.add_argument('-s', '--source', help="The program's source file", default="examples/onos-alpha.midori")
    arg_parser.add_argument('-i', '--iterations', help="Number of iterations to run", type=check_positive, default=1)
    
    args = arg_parser.parse_args ()
    if args.source:
        client = MidoriClient()
        for iteration in range(0, args.iterations):
            response = client.create_network(source=args.source,
                                             net_id=iteration)
            print(json.dumps(response, indent=2))

if __name__ == '__main__':
    main ()
