# bt-lantis YAML Converter
# By Cameron Fleming (Nevexo): MIT License

import yaml, getpass, datetime

class Converter:

    # Converter used by bt-lantis
    def __init__(self, verboseSubroutine, version, name, repo, LANTISRepo):
        self.verbose = verboseSubroutine
        self.version = version
        self.name = name
        self.repo = repo
        self.LANTISRepo = LANTISRepo

    def yamlLoad(self, fileStream):
        # SafeLoad the YAML (and validate it)
        self.verbose("[Converter] Testing RAM-loaded configuration.")

        try:
            self.yaml = yaml.safe_load(fileStream)
            return True

        except yaml.YAMLError as yamlError:
            print(yamlError)
            return False

    def addComments(self):
        string = ""
        string += f"# {self.name} ({self.version}) Generated Configuration File"
        string += f"\n# Created at {datetime.datetime.now()} by {getpass.getuser()}" 
        string += f"\n# For more information about {self.name}, see {self.repo}"  
        string += f"\n# For more information about LANTIS, see {self.LANTISRepo}" 
        string += f"\n# Keep hold of your YAML file, LANTIS files can not (yet) be reversed into YAML.\n\n# ##START LANTIS CONFIG##\n"
        return string

    def getServices(self):
        return self.yaml["services"]

    def getMode(self, rule):
        return self.yaml["rules"][rule]["mode"]

    def getRules(self):
        return self.yaml["rules"]

    def ruleEnabled(self, rule):
        return self.yaml["rules"][rule]["enable"]

    def ruleChecks(self, ruleName):
        services = self.getServices()
        rule = self.yaml["rules"][ruleName]
        state = True

        # Single mode specific features
        if rule["mode"] == "single":
            if rule["service"] not in services:
                print(f"[Sanity Check Error] {ruleName} has invalid service '{rule['service']}'")
                state = False
            
        # Shared mode specific features
        if rule["mode"] == "shared":
            if len(rule['services']) == 1:
                print(f"[Sanity Check Error] {ruleName} only has one service but is marked as a shared connection. Consider adding more services or switched to a single.")

            for service in rule["services"]:
                if service not in services:
                    print(f"[Sanity Check Error] {ruleName} has invalid service '{service}'")
                    state = False
            

        # Global features
        if rule["use_global_remote"] == False:
            if "remote" in rule:
                # Check for host
                if "server" not in rule["remote"]:
                    print(f"[Sanity Check Error] {ruleName} is missing remote 'server' configuration and global remote is disabled.")
                    state = False
                
                # Check for port
                if "port" not in rule["remote"]:
                    print(f"[Sanity Check Error] {ruleName} is missing remote 'port' configuration and global remote is disabled.")
                    state = False
                
                # Check for user
                if "user" not in rule["remote"]:
                    print(f"[Sanity Check Error] {ruleName} is missing remote 'user' configuration and global remote is disabled.")
                    state = False
                    
            else:
                print(f"[Sanity Check Error] {ruleName} is missing remote configuration and global remote is disabled.")
                state = False        

        return state
    
    def createRuleSingle(self, ruleName, ignoreDisabled):
        # Create the rule in LANTIS style (SINGLE)
        # This assumes all sanity checks have already passed.
        rule = self.yaml["rules"][ruleName]
        gRemote = self.yaml["global"]["remote"]
        gLocal = self.yaml["global"]["local"]
        options = self.yaml["global"]["options"]
        ruleStr = ""
        services = self.getServices()

        # Sanity check (mainly for debugging)
        if rule["mode"] != "single":
            return False

        # Enable/Disable rule
        if rule["enable"]:
            ruleStr += "e;"
        else:
            ruleStr += "d;"
        
        # Add rule name
        ruleStr += ruleName + ";"

        # Use global settings
        if rule["use_global_remote"]:
            # Use the settings from global
            ruleStr += gRemote["server"] + ";" # Remote Hostname/IP Address
            ruleStr += str(gRemote["port"]) + ";"   # Remote SSH Port
            ruleStr += gRemote["user"] + ";"   # Remote SSH Username
        
        # 'Local' LANTIS Server IP / Auto Discover
        if gLocal["server"] == "auto":
            ruleStr += '~;'
        else:
            ruleStr += gLocal["server"] + ";"
        
        # 'Local' LANTIS Server SSH Port
        ruleStr += str(gLocal["port"]) + ";"

        # 'Local' LANTIS Server SSH Username
        ruleStr += gLocal["user"] + ";"

        # LANTIS Runtime Specific Settings
        if options["setup_mode"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'
        
        if options["bypass_nat"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'

        if options["hijack_port"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'
        
        # Add public (exposed on remote) port
        ruleStr += str(services[rule['service']]['remote_port']) + ";"

        # Add local (service) Host
        ruleStr += services[rule['service']]['local_address'] + ";"

        # Add local (service) port
        ruleStr += str(services[rule['service']]['remote_port']) + ";"

        # Listen to all interfaces or loopback
        if services[rule['service']]['listen_interface'] == 'all':
            ruleStr += '1;'
        else:
            ruleStr += '0;'
            
        if ignoreDisabled and rule["enable"] == False:
            return False
        else:
            return ruleStr

    def createRuleShared(self, ruleName, ignoreDisabled):
        # Create the rule in LANTIS style (SINGLE)
        # This assumes all sanity checks have already passed.
        rule = self.yaml["rules"][ruleName]
        gRemote = self.yaml["global"]["remote"]
        gLocal = self.yaml["global"]["local"]
        options = self.yaml["global"]["options"]
        ruleStr = ""
        services = self.getServices()

        # Sanity check (mainly for debugging)
        if rule["mode"] != "shared":
            return False

        # Enable/Disable rule
        if rule["enable"]:
            ruleStr += "l;"
        else:
            if not ignoreDisabled:
                print("[CAUTION!] Disabling linked rules is not properly supported by LANTIS, LANTIS may fail to start.")
                print(" --> To avoid this error, re-run with '--ignore-disabled")
            ruleStr += "d;"
        
        # Add rule name
        ruleStr += ruleName + ";"

        # Use global settings
        if rule["use_global_remote"]:
            # Use the settings from global
            ruleStr += gRemote["server"] + ";" # Remote Hostname/IP Address
            ruleStr += str(gRemote["port"]) + ";"   # Remote SSH Port
            ruleStr += gRemote["user"] + ";"   # Remote SSH Username
        
        # 'Local' LANTIS Server IP / Auto Discover
        if gLocal["server"] == "auto":
            ruleStr += '~;'
        else:
            ruleStr += gLocal["server"] + ";"
        
        # 'Local' LANTIS Server SSH Port
        ruleStr += str(gLocal["port"]) + ";"

        # 'Local' LANTIS Server SSH Username
        ruleStr += gLocal["user"] + ";"

        # LANTIS Runtime Specific Settings
        if options["setup_mode"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'
        
        if options["bypass_nat"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'

        if options["hijack_port"]:
            ruleStr += '1;'
        else:
            ruleStr += '0;'
        
        # Add Services to configuration
        pointer = 0
        endPointer = len(rule['services']) - 1

        for service in rule["services"]:
            if pointer != 0 and pointer != endPointer:
                # Linked services start with '^'
                ruleStr += '^;'
            if pointer == endPointer:
                # The final service must start with '>'
                ruleStr += '>;'
            
            # Add the service
            serviced = services[service]
            # Service public port
            ruleStr += str(serviced['remote_port']) + ";"
            # Service host/IP
            ruleStr += serviced["local_address"] + ";"
            # Service local port
            ruleStr += str(serviced["local_port"]) + ";"
            # Service interface
            if serviced["listen_interface"] == 'all':
                ruleStr += '1;'
            else:
                ruleStr += '0;'
            
            if pointer != endPointer:
                ruleStr += '\n'
            pointer += 1

        if ignoreDisabled and rule["enable"] == False:
            return False
        else:
            return ruleStr