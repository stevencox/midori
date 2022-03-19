import argparse
import logging
from midori.utils import LoggingUtil, Resource
from midori.parser import Parser, Program
from typing import List, Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger ("midori.compiler")

class Compiler:

    def __init__(self,
                 dry_run:bool = False) -> None:
        self.dry_run = dry_run
        message = ", ".join ([
            f"dry_run={self.dry_run}"
        ])
        logger.debug (f"{message}")
        self.parser = Parser ()
        
    def _emit (self,
               ast: Program,
               path: str=None,
               output_path:str=None) -> str:

        for statement in ast.statements:
            logger.debug(f"{statement}")
            
        result = None
        if output_path:
            Resource.render_file (
                template_path="network.jinja2",
                context={
                    "ast": ast
                },
                path=output_path)
        else:
            result = Resource.render (
                template_path="network.jinja2",
                context={
                    "ast": ast
                })
        return result
    
    def process_file (self,
                      path: str,
                      output_path:str=None) -> str:
        text = Resource.read_file (path)
        return self.process (source=text, path=path, output_path=output_path)
        
    def process (self,
                 source: str,
                 path: str=None,
                 output_path:str=None) -> str:
        ast: Program = self.parser.parse (source)
        return self._emit (ast=ast, path=path, output_path=output_path)

def main ():
    
    """ Process arguments. """
    arg_parser = argparse.ArgumentParser(
        description='Midori Compiler',
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog,
            max_help_position=180))
    
    arg_parser.add_argument('-s', '--source',
                            help="The program's source file")
    arg_parser.add_argument('--dry-run',
                             help="Don't write any output.",
                             action="store_true",
                             default=False)
    
    args = arg_parser.parse_args ()
    if args.source:
        compiler = Compiler (dry_run=args.dry_run)
        compiler.process_file (path=args.source,
                               output_path=args.source.replace (".midori", ".py"))

if __name__ == '__main__':
    main ()
