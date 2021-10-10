# midori
A network simulation compiler for [Containernet](https://containernet.github.io/)

After tinkering with a [compiler](https://github.com/stevencox/nyko/edit/main/README.md) for [Faucet](https://docs.faucet.nz/en/latest/intro.html), I found [Mininet](http://mininet.org/), a virtual network layer that simplifies network simulations. Mininet does awesome things but I've been using containers for years and the virtual machine oriented development environment was cumbersome for me.

Then I found Containernet, a Docker friendly fork of Mininet. Containernet networks are [built in Python](https://containernet.github.io/#get-started), which works fine but it made me wonder if a more idiomatic form would be possible. This Midori program builds the same network:

```
controller c0
node d1 ip "10.0.0.251" image "ubuntu:trusty"
node d2 ip "10.0.0.252" image "ubuntu:trusty"

switch s1 s2
link l1 src d1 dst s1
link l2 src s1 dst s2 cls TCLink delay "100ms" bw 1
link l3 src s2 dst d2

up
ping d1 d2
down
```

## Design
Midori provided a chance to try Lark, a Python parser library I've been looking at for a while. I've been using Pyparsing for years contentedly. But so far, I prefer Lark. More on that in a minute. First, an overview:

![image](https://user-images.githubusercontent.com/306971/136678115-dae6a844-a391-400d-bfdd-339ad0e4f567.png)

It could be confused with almost any compiler except for a couple of specifics:

### Lark

#### Grammar
Lark's grammar syntax is very elegant and compact. This is a big contrast to Pyparsing where the grammar syntax is a hybrid domain specific language within Python.  This is the whole Midori parser: 
```
parser = Lark("""
    start: program

    program: statement+

    ?statement: controller | node | switch | link | up
              | ping | down

    controller: "controller" value
    node: "node" NAME "ip" ip_addr "image" value
    switch: "switch" name+
    cls: "cls" NAME
    delay: "delay" STRING
    bw: "bw" DEC_NUMBER
    link: "link" NAME "src" NAME "dst" NAME cls? delay? bw?
    up: "up"
    ping: value+
    down: "down"

    value: name | STRING | DEC_NUMBER
    name: NAME
    ip_addr: STRING

    %import python (NAME, STRING, DEC_NUMBER)
    %import common.WS
    %ignore WS
    """,
    parser="lalr",
)
```

#### Abstract Syntax Tree
I noted in my description of Nyko that creating an abstract syntax tree was likely to require a good deal of tedious work and be a gating factor. Lark provides an interesting facility for ASTs. It doesn't eliminate the work but it makes it predictable and semi-automated. We define [dataclasses](https://docs.python.org/3/library/dataclasses.html) for AST elements and Lark instantiates and populates them based on the grammar.

## Jinja2
Jinja2 is a very widely used templating language. Ansible users will be familiar with its syntax. We use it to generate the Containernet Python program by iterating over the statements in a program which is the abstract syntax tree resulting from the Lark parse tree of a Midori program. Here's Midori's code emitter:
```


