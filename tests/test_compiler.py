import os
from midori.compiler import Compiler
from midori.utils import Resource

class TestCompiler:

    def test_compiler (self) -> None:
        source = os.path.join (
            os.path.dirname(os.path.dirname (__file__)),
            "examples",
            "net.midori")
        output = os.path.join (
            os.path.dirname (__file__),
            "net.py")
        expect = os.path.join (
            os.path.dirname (__file__),
            "net.py.expected")
        compiler = Compiler ()
        compiler.process (path=source)

        output_text = Resource.read_file (output)
        expect_text = Resource.read_file (expect)
        assert output_text == expect_text, f"Output does not match expectations. Diff output {output} and expected {expect}"
        
