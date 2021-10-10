# Midori
A network simulation compiler for [Containernet](https://containernet.github.io/)

After tinkering with a [compiler](https://github.com/stevencox/nyko/edit/main/README.md) for [Faucet](https://docs.faucet.nz/en/latest/intro.html), I found [Mininet](http://mininet.org/), a virtual network layer that simplifies network simulations. Mininet does awesome things but I've been using containers for years and the virtual machine oriented development environment was cumbersome for me.

Then I found Containernet, a Docker friendly fork of Mininet. Containernet networks are [built in Python](https://containernet.github.io/#get-started), which works great. But it did make me wonder if I could develop a form more idiomatic to folks in a networking domain. This Midori program builds the same network:

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


Midori is a compiler comprising the classic phases:
  * Lexical analysis scans an input document to generate a token stream
  * A parser applies grammar productions to determine if the token stream is accepted by the language
  * Productions are converted into an abstract syntax tree (AST), or structure describing each concept in the language
  * Code generation (the emitter) generates an executable by processing the AST
![image](https://user-images.githubusercontent.com/306971/136678115-dae6a844-a391-400d-bfdd-339ad0e4f567.png)

### Parser
Midori also provided a chance to try Lark, a Python parser library I've been looking at for a while. I've been using Pyparsing for years contentedly. But so far, I prefer Lark. The two principal reasons for my positive review of Lark are the grammar syntax and its elegant support for abstract syntax trees.

#### Grammar

Midori's parser uses an LALR parser generated from a grammar described in [Lark's EBNF syntax](https://lark-parser.readthedocs.io/en/latest/grammar.html?highlight=ebnf#general-syntax-and-notes).

[Lark](https://lark-parser.readthedocs.io/en/latest/index.html)'s grammar syntax is very elegant and compact. This is a contrast to [Pyparsing](https://github.com/helxplatform/tranql/blob/master/src/tranql/grammar.py) where the grammar syntax is a hybrid domain specific language within Python. This is the whole Midori parser: 
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

### Emitter
For now, we have one code emitter for Midori. It writes a Containernet Python program.

Jinja2 is a very widely used templating language. Ansible users will be familiar with its syntax. I've used it in [Tycho](https://github.com/helxplatform/tycho/blob/master/tycho/template/pod.yaml) and [smartBag](https://github.com/NCATS-Tangerine/smartBag/blob/master/app.py.j2) in the past. We [use it to generate](https://github.com/stevencox/midori/blob/main/src/midori/network.jinja2) the Containernet Python by iterating over the statements in a `program` which is the abstract syntax tree resulting from the Lark parse tree of a Midori program.

## Using

First, a few environment notes:
  * I followed the ["bare metal"](https://containernet.github.io/#installation) Container installation instructions with no trouble on an Ubuntu 18.04 VMWare virtual machine. 
  * I used Python 3.10 for Midori.
  * Lark's most recent published version seemed out of sync with the docs so I cloned it and installed from source.

We first compile our program with:
```
scox@ubuntu:~/dev/midori$ bin/midori compile examples/net.midori
2021-10-09 17:43:35,165 - midori.compiler - DEBUG - dry_run=False
```
This generates net.py next to the source file. We then switch to the containernet environment which runs as root. I've configured Containernet on . Also, before each run, I use
```
$ sudo mn -c
```
to clean up remnants of any previous containernet runs.

```
(containernet) root@ubuntu:/home/scox/dev/nyko# python ../midori/examples/net.py 
*** Adding controller: c0
*** Adding node:d1 ip:10.0.0.251 img:ubuntu:trusty
1: 
d1: kwargs {'ip': '10.0.0.251'}
d1: update resources {'cpu_quota': -1}
*** Adding node:d2 ip:10.0.0.252 img:ubuntu:trusty
1: 
d2: kwargs {'ip': '10.0.0.252'}
d2: update resources {'cpu_quota': -1}
*** Adding switch s1
*** Adding switch s2
** Adding link src:d1 dst:s1 cls:None del:None bw:None** Adding link src:s1 dst:s2 cls:TCLink del:100ms bw:1(1.00Mbit 100ms delay) (1.00Mbit 100ms delay) (1.00Mbit 100ms delay) (1.00Mbit 100ms delay) ** Adding link src:s2 dst:d2 cls:None del:None bw:None*** Configuring hosts
d1 d2 
*** Starting controller
c0 
*** Starting 2 switches
s1 (1.00Mbit 100ms delay) s2 (1.00Mbit 100ms delay) ...(1.00Mbit 100ms delay) (1.00Mbit 100ms delay) 
d1 -> d2 
d2 -> d1 
*** Results: 0% dropped (2/2 received)
*** Stopping 1 controllers
c0 
*** Stopping 3 links
...
*** Stopping 2 switches
s1 s2 
*** Stopping 2 hosts
d1 d2 
*** Done
*** Removing NAT rules of 0 SAPs
```
