#!/usr/bin/python
"""
Generate a containernet network.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

net = Containernet(controller=Controller)


   SetVar(name=Token('NAME', 'a'), value=Value(meta=<lark.tree.Meta object at 0x7fc6a94917f0>, value=1))

   If(cond=Value(meta=<lark.tree.Meta object at 0x7fc6a9491d30>, value=Name(name=Token('NAME', 'a'))), then=CodeBlock(statements=[Print(value=Value(meta=<lark.tree.Meta object at 0x7fc6a9471b50>, value='a is 1')), SetVar(name=Token('NAME', 'a'), value=Value(meta=<lark.tree.Meta object at 0x7fc6a94712e0>, value=2))]))



info('*** Adding controller\n')
net.addController('c0')
info('*** Adding docker containers\n')
d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty")
d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty")
info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
info('*** Creating links\n')
net.addLink(d1, s1)
net.addLink(s1, s2, cls=TCLink, delay='100ms', bw=1)
net.addLink(s2, d2)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([d1, d2])

info('*** Stopping network')
net.stop()
