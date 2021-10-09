import argparse
import logging
from midori.utils import LoggingUtil, Resource
from midori.parser import Parser, Program
from typing import List, Dict

LoggingUtil.setup_logging ()

logger = logging.getLogger ("midori.compiler")

class Compiler:

    def __init__(self, dry_run:bool) -> None:
        self.dry_run = dry_run
        message = ", ".join ([
            f"dry_run={self.dry_run}"
        ])
        logger.debug (f"{message}")
        self.parser = Parser ()

    def _parse (self, source: str) -> None:
        text = Resource.read_file (source)
        return self.parser.parse (text)

    def _emit_network (self, path: str, ast: Program) -> None:
        Resource.render_file (
            template_path="network.jinja2",
            context={
                "ast": ast
            },
            path=path.replace (".midori", ".py"))
        
    def _emit (self, path: str, ast: Program) -> None:
        self._emit_network (path, ast)

    def process (self, path: str) -> None:
        ast: Program = self._parse (path)
        self._emit (path, ast)

def main ():
    
    """ Process arguments. """
    arg_parser = argparse.ArgumentParser(
        description='Midori',
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
        compiler.process (args.source)

if __name__ == '__main__':
    main ()
