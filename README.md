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

