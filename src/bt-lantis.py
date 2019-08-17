# bt-lantis: A configuration wrapper for LANTIS.
# See https://code.acr.moe for information about LANTIS
# and github.com/nevexo/bt-lantis for a configuration guide.
# 
# Written by Cameron Fleming (Nevexo) under the MIT license. 
# NOTE: converter.py must be in the same directory as bt-lantis.py for this program to run.

import argparse  # Used for specifying setup variables
import converter # bt-lantis engine
import os        # Used for file management

# Setup globals
btlVers = "2.0"
configFileLocation = "lantis.yaml"
outputFileLocation = "ports.lantis.csv"
verboseOutput = False

# Setup global functions
def verbose(msg):
    if verboseOutput:
        print(f"[Verbose] {msg}")

# Setup argument parser
parser = argparse.ArgumentParser(description="BT-LANTIS (Better LANTIS) a YAML configuration wrapper for LANTIS.")

# Setup arguments
parser.add_argument("-c", "--config", type=str, help="Custom YAML config file (uses lantis.yaml by default)")
parser.add_argument("-o", "--output", type=str, help="Custom output file (uses ports.lantis.conf by default) (or 'shell' to output to shell)")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
parser.add_argument("--ignore-disabled", action="store_true", help="Ignore all disabled rules (don't place them in the file)")

def runConversion():
    # Run the conversion on converter.py
    bt_lantis.addComments()
    rules = bt_lantis.getRules()
    services = bt_lantis.getServices()
    if len(rules) == 0:
        print("[Error!] No Rules!")
        exit()
    else:
        verbose(f"[Main] Found {len(rules)} rules.")
    
    if len(services) == 0:
        print("[Error!] No Services!")
        exit()
    else:
        verbose(f"[Main] Found {len(services)} services.")

    rulesString = ""
    for rule in rules:
        verbose(f"[Main] Process Rule: {rule}")

        ruleSafety = bt_lantis.ruleChecks(rule)
        if not ruleSafety:
            print(f"Rule {rule} has invalid config. Please see the issue above.")
            continue
        else:
            verbose(f"[Main] [{rule}] Sanity checks passed.")

        # Generate the rule
        if bt_lantis.getMode(rule) == 'single':
            ruleString = bt_lantis.createRuleSingle(rule, args.ignore_disabled)
        else:
            ruleString = bt_lantis.createRuleShared(rule, args.ignore_disabled)
        
        if ruleString != False:
            rulesString += ruleString + "\n"

    rulesString = bt_lantis.addComments() + rulesString[:-1]
    print(f"Rule generation complete, writing to file: {outputFileLocation}")    

    if outputFileLocation == 'shell':
        print(rulesString)
    else:
        with open(outputFileLocation, "w+") as f:
            f.write(rulesString)
    
    print("-- bt-lantis complete! -- ")


if __name__ == "__main__":
    # Main routine
    args = parser.parse_args()

    # Setup variables/defaults
    if args.verbose:
        verboseOutput = True
        verbose("Output enabled.")

    if args.config:
        configFileLocation = args.config
        verbose(f"Using custom config {configFileLocation}")

    if args.output:
        outputFileLocation = args.output 
        verbose(f"Using custom output file/shell: {outputFileLocation}")

    # User greeting
    print("-----------------------------------")
    print(f"Welcome to bt-lantis {btlVers}")
    print("By Cameron Fleming (Nevexo)")

    # Setup converter class
    bt_lantis = converter.Converter(verbose, btlVers, "BT-LANTIS", "https://github.com/nevexo/bt-lantis", "https://code.acr.moe")

    # Check if config is present
    if os.path.exists(configFileLocation):
        verbose("[Main] Configuration file exists.")
        # Load configuration

        with open(configFileLocation, "r+") as stream:
            loadState = bt_lantis.yamlLoad(stream)
        
        if loadState:
            verbose("[Main] Config load success!")
            runConversion()

        else:
            print("[Error!] Failed to load configuration, please see possible YAML errors above or use a YAML-Lint to verify your YAML.")

    else:
        print(f"[Error!] {configFileLocation} is not a valid path/filename. Please check it and re-launch bt-lantis.")
else:
    print("[STOP!] BT-LANTIS is a standalone program. Please do not import it.")
    print("If you're planning to extend bt-lantis, you may import converter.py and read CONVERTER.md for documentation.")