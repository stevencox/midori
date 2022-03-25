import argparse
import logging
from midori.utils import LoggingUtil, Resource
from midori.parser import Parser, Program
from typing import List, Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger (__name__)

class Compiler:
    """ The compiler accetps a domain specific language (DSL) describing
    a network including elements like SDN controllers, hosts as containers,
    switches, and links. The compiler parses the input source code into an
    abstract syntax tree, then projects that intermediate representation
    through a template to generate executable Containernet(Mininet) Python code. """
    def __init__(self,
                 dry_run: bool = False,
                 debug: bool = False
    ) -> None:
        """ Initialize the compiler. 
        Args:
            dry_run (bool): Compile but don't actually write output.
            debug (bool): Print verbose runtime information.
        """
        self.dry_run = dry_run
        self.debug = debug
        logger.debug (f"dry_run={self.dry_run}, debug={self.debug}")
        self.parser = Parser ()
        """ The lexical analyzer (parser) that will assemble tokens into an AST. """
        
    def _emit (self,
               ast: Program,
               output_path:str=None) -> str:
        """ Write an executable output program.
        Args:
            ast (Program): Parsed statements from the grammar.
            path (str): The path to the input file.
            output_path (str): Path to the output file.
        """
        if logger.isEnabledFor(logging.DEBUG):
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
        return self.process (source=text, output_path=output_path)
        
    def process (self,
                 source: str,
                 output_path:str=None) -> str:
        ast: Program = self.parser.parse (source)
        return self._emit (ast=ast, output_path=output_path)

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
    arg_parser.add_argument('--debug',
                             help="Print very verbose runtime information.",
                             action="store_true",
                             default=False)
    
    args = arg_parser.parse_args ()
    if args.source:
        compiler = Compiler (dry_run=args.dry_run, debug=args.debug)
        compiler.process_file (path=args.source,
                               output_path=args.source.replace (".midori", ".py"))

if __name__ == '__main__':
    main ()
