# Better LANTIS & LANTISWeb

### Please note: LANTIS Web isn't complete. More information coming soon.

A better configuration wrapper for LANTIS Router 2.

LANTIS is a free, opensource bash based watchdog for SSH tunnels. 
It allows you to use cheap, throwaway servers from any hosting company to hide any IP.

LANTIS itself has a horrid config file & guide, so this is my way of fixing it.

You can run BT-LANTIS from any platform, but LANTIS only works on a bash bashed system.
Download a version of LANTIS [here](code.acr.moe/kazari/LANTIS/)

![Image](https://i.imgur.com/FFk2Ee6.png)

## Getting Started with BT-LANTIS config

Make a file called 'config.json' - Or what ever you want to call it, that's what I'll be calling it from now on.
Or rename example.config.json to config.json

Now edit that file in any editor. You have a few choices:

1) Use global
2) Don't use global.

Using a global configuration allows you to add new port maps without repeating the IP & login information for every one.

```json

{
    "globalSettings": {
      "rServer": "IP of your throwaway server",
      "rPort": SSH Port for your throwaway server.,
      "rUser": "username on your remote server (recommended root)",
      "lUser": "Username of the system running LANTIS (recommended root)",
      "lServer": "IP of the LANTIS server on the internet (~ for dynamic)",
      "lPort": SSH port to get back to this machine,
      "setupEndpoint": "Setup remote server (0 / 1) (SEE LANTIS DOCS!!)",
      "bypassNAT": "Bypass NAT (0 /1) (SEE LANTIS DOCS!!)",
      "hijackPort": "Hijack the remote port (See lantis docs)"
    }
}
```
After setting these, if you want a port mapping to use these settings, just put
```
"useGlobal": true
```
## Configuring port maps

You again have 2 choices

1) Single connection
2) Linked connection

A single connections means it's one tunnel for 1 service/port, linked uses one tunnel for multiple ports/services.
Here's how to make a single connection:
```json
"test": {
	"enabled": true <- If set to false, LANTIS won't run these.,
	"type": "single", 
	"useGlobal": true,
	"portMapping": {
		"serverPort": 22 <- This is the port on the server that you want to be public,
		"remotePort": 2950 <- This is the port that you want '22' to be published to.,
		"server": "10.0.0.5" <- This is where that service is running (can be 127.0.0.1)
	}
}
```
Making a linked connection is similar, but you can have more than one portMapping:
(DO NOT PROVIDE JUST 1 SERVICE! THAT COULD CAUSE LANTIS TO DIE!)
```
"test-2": {
	"enabled": true,
	"type": "linked",
	"useGlobal": true,
	"portMapping": {
		"0": {
			"serverPort": 2950,
			"remotePort": 2950,
			"server": "10.0.0.5"
          	},
		"1": {
		    "serverPort": 28015,
		    "remotePort": 28015,
		    "server": "127.0.0.1"
		},
		"2": {
		    "serverPort": 9090,
		    "remotePort": 8893,
		    "server": "127.0.0.1"
		}
      }
}
```

## Deploying your changes
### Argument -d will be able to do this automatically in the future automatically.
```
btl -c config.json ports.lantis.conf
```
```
bash lantis.bash -L
```
### Setting up LANTIS
Clone code.acr.moe/kazari/LANTIS/
and type 'bash lantis.bash -Z' & follow the instructions for setting up your key.

```
