# bt-lantis

Welcome to the BetterLANTIS GitHub Repository

## LANTIS

Lain Anonymous NetworkIng System (LANTIS) is a reverse port forwarding server & SSH tunnel daemon designed
for use with throw-away public cloud servers.

LANTIS can be used to port forward services on a private network to a public host with SSH tunnels, with it's
bypass NAT system turned on, it can operate without needing to open ports on the private network.

The remote (throw-away) server only needs SSH exposing to the internet on any port. SSH keys are used for authentication.
Root access may be required if you wish to use [Priviliged ports](https://www.w3.org/Daemon/User/Installation/PrivilegedPorts.html)

[Get LANTIS](https://code.acr.moe/kazari/LANTIS)

## The Problem

LANTIS is an extremely powerful tool, but unfortunately it's configuration file can be daunting to someone 
with no prior experience. This project hopes to configuring LANTIS easier and faster.

## Terminology

For those unfamiliar with networking and LANTIS, the following section should give
some guidance on the terminology used throughout this document and the
configuration files.

### NAT - Network Address Translation

NAT is a technology that was created to help deal with the shortage of IPv4
addresses available. Every home internet connection uses NAT, this means your
house is assigned a single IP address (a 'public' address) and your router then 
gives out private IP addresses. When your computer wants to get a resource from the internet, it contacts your gateway (aka your router) which takes the request, removes your private IP and places your public IP in its place. Once the server sends a response, your router swaps the public IP back to your private IP and sends it onto the LAN. This is called masquerading.

When you port forward something you're telling your router that whenever it sees traffic coming in from the internet to that port, it should send it to this specific host.

### SSH Tunneling

SSH tunneling is a feature built into OpenSSH that allows us to send non-SSH data (such as HTTP) down an SSH connection. 

[Learn more about SSH Tunneling](https://www.youtube.com/watch?v=bKZb75TaRyI)

## Configuration

bt-LANTIS is an abstraction layer for 'ports.lantis.csv' - LANTIS' usual configuration file.

It uses YAML (see example.lantis.yaml) and simple English options.

Below are some explanations of the sections.

### Global Settings

LANTIS has some settings of it's own and allows you to define the remote/local
settings once and use them throughout the rest of the config. 

#### Remote

This is the 'throw-away' or cloud-hosted server that you want the ports to be exposed on. This should be a server that you don't mind sharing the IP address for, as all of your users will connect to it, then be sent back to your private server.

The "host" must be set to the IP address LANTIS should use to connect to the server, note you must have installed the LANTIS key into authorized_keys for the user you wish to use.

The "user" field will likely just be 'root' as LANTIS doesn't support privilege escalation and if you want to use a port below 1024, you must be root.

Port, as it's name suggests, is the port to connect to. This is the port that your SSH server is listening on (default 22)

#### Local

This is the server the LANTIS router will be running on. It's usually within a private network that you want to forward ports from.

'host' is the IP address of the machine you're using. This IP address must be accessible by the remote server (unless you're using bypass_nat) - you can enter auto in this field to have LANTIS automatically detect your IP address.

#### Options

LANTIS has a collection of it's own options.

- setup_mode
  When you first run LANTIS, it needs to SSH into the remote server and deploy the required keys. Write your config, set this to yes and run the connection, once you've verified the connection started correctly, turn this back off.

- bypass_nat
  One of the most important features of LANTIS is it's ability to bypass NAT, if this is set to true, you don't need to open a port on your private network. A connection will be opened to your remote server then the remote server will use that connection to connect to your local machine again. This adds complication and overhead, so only use it if you have no way of port-forwarding the server any other way.

- hijack_port 
  If there is a process on the remote server using the port that LANTIS wants to use, it will kill it. Be careful using this during configuration testing, especially under production conditions.

### Services

This is a feature specific to bt-lantis, it splits services and rules from each other, the services are ports that you want to forward, and the rules are how you will forward them.

Services can be re-used in different connections to remotes, but can not be used on the same remote (as the port will already be allocated)

- local_port
  This is the port the service is using on the machine it's running on.

- remote_port
  This is the port you want the service to be visible by on the remote server

- local_address
  This is the IP address of the server with that service (it can be localhost)

### Rules

These work in the same way that dst-nat (port forward) rules work on your router/firewall. 

- enable
  Rules that are disabled will still be placed into your LANTIS file, but in the disabled state, meaning when you run the bring-all-up LANTIS command, the rule will remain down.

- mode
  This sets how the rule should be created, if set to single, the 'service' directive should be added, multiple services are not supported in this mode.
  If set to 'shared', the 'services' directive must be used, even if you're only using a single service. See the next section for more information on this feature.

- use_global_remote
  This tells the rule wether it should use the global remote settings set at the top of the file, or use ones set within the rule. It uses the same settings (see the example)

- service
  If using 'single' mode, this directive sets which service (from the services section) should be used

- services
  If using the 'shared' mode, this directive sets which services (from the services section) should be used

### Single vs Shared Connections

LANTIS has support for 'linked' or as I call them 'shared' connections.

Connection sharing is great for low-bandwidth services such as web servers as it will share a single SSH tunnel for multiple services, reducing the route table size and load on the server.

Single connections mean only one service can be sent down a tunnel, this is recommended if the service you're using uses a lot of bandwidth, such as a game server.