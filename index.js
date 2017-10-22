#! /usr/bin/env node
var debug = false;
var fs = require('fs')
var pack = require('./package.json')

function convert(args, callback) {
    var string = "# LANTIS EasyLink port Router 2\n# Config written by: - BT-LANTIS (btl) on " + new Date() + "\n# LANTIS: https://code.acr.moe/kazari/LANTIS/\n# BT-LANTIS: https://github.com/nevexo/BT-LANTIS"
    try {
        var jsonCfg = require("./" + args[args.indexOf('-c') + 1])
    }catch (err) {
        m('[<ERR>] Config file not found!')
        d(err)
        process.exit(1)
    }
    if (jsonCfg.globalSettings != undefined) {
        d('[INFO] Found a globalConfiguration')
        var global = jsonCfg.globalSettings
    }
    for (var key in jsonCfg.rules) {
        string = string + '\n';
        d('Found rule: ' + key)
        var obj = jsonCfg.rules[key]
        //Check for required things
        //Stage 1.
        if (obj.type == undefined || obj.useGlobal == undefined || obj.enabled == undefined || obj.portMapping == undefined) {
            m('[<ERR>] [STAGE 1] A directive is missing from the rule: ' + key)
            process.exit(1)
        }else {
            d('[STAGE 1] Checks complete, starting stage 2 checks.')
        }
        //Stage 2
        if (obj.useGlobal == false) {
            d(key + ' is not using a globalConfiguration')
            if (obj.rPort == undefined || obj.lPort == undefined || obj.lServer == undefined || obj.rUser == undefined || obj.lUser == undefined || obj.bypassNAT == undefined || obj.hijackPort == undefined || obj.setupEndpoint == undefined || obj.rServer == undefined) {
                m('[<ERR>] [STAGE 2] A missing directive in the server config has been detected in rule: ' + key)
                process.exit(1)
            }else {
                d('[STAGE 2] Stage 2 checks have passed, the config will now be written!')
            }
        }
        if (obj.type == 'single') {
            if (obj.enabled) {
                obj.enabled = 'e'
            }else {
                obj.enabled = 'd'
            }
            rule = obj.portMapping
            if (obj.useGlobal) {
                string = string + obj.enabled + ';' + key + ';' + global.rServer + ';' + global.rPort + ';' + global.rUser + ';' + global.lServer + ';' + global.lPort + ';' + global.lUser + ';' + global.setupEndpoint + ';' + global.bypassNAT + ';' + global.hijackPort + ';'
                string = string + rule.remotePort + ';' + rule.server + ';' + rule.serverPort + ';1;'
                //m('Your configuration for ' + key + '\n' + string)
            }else {
                string = string + obj.enabled + ';' + key + ';' + obj.rServer + ';' + obj.rPort + ';' + obj.rUser + ';' + obj.lServer + ';' + obj.lPort + ';' + obj.lUser + ';' + obj.setupEndpoint + ';' + obj.bypassNAT + ';' + obj.hijackPort + ';'
                string = string + rule.remotePort + ';' + rule.server + ';' + rule.serverPort + ';1;'
                //m('Your configuration for ' + key + '\n' + string)
            }
        }else {
            d(key + ' is a linked connection.') //LINKED CONVERSION
            var rules = obj.portMapping
            if (obj.portMapping.length == 0 || obj.portMapping.rPort != undefined) {
                m('[<ERR>] ' + key + ' is a linked connection that only has one port mapping! Change this to a single connection!!')
                d('[CAUTION] Aborted at stage 3.')
                process.exit(1)
            }else {
                d('Starting a linked connection creation.')
                if (len == 0) {
                    m('[<ERR>] Rule, ' + key + ' has a directive only holding 1 config.')
                    d('[CAUTION] Aborted at stage 3.')
                    process.exit(1)
                }else {
                    var rule = obj.portMapping[0]
                    if (obj.enabled) {
                        obj.enabled = 'l'
                    }else {
                        obj.enabled = 'd'
                    }
                    if (obj.useGlobal) {
                        string = string + obj.enabled + ';' + key + ';' + global.rServer + ';' + global.rPort + ';' + global.rUser + ';' + global.lServer + ';' + global.lPort + ';' + global.lUser + ';' + global.setupEndpoint + ';' + global.bypassNAT + ';' + global.hijackPort + ';'
                        string = string + rule.remotePort + ';' + rule.server + ';' + rule.serverPort + ';1;'
                    }else {
                        string = string + obj.enabled + ';' + key + ';' + obj.rServer + ';' + obj.rPort + ';' + obj.rUser + ';' + obj.lServer + ';' + obj.lPort + ';' + obj.lUser + ';' + obj.setupEndpoint + ';' + obj.bypassNAT + ';' + obj.hijackPort + ';'
                        string = string + rule.remotePort + ';' + rule.server + ';' + rule.serverPort + ';1;'
                    }
                    d('[' + key + '] Written first line.')
                    string = string + '\n'
                    var loop = 0
                    var len = Object.keys(obj.portMapping).length;
                    for (var rule in obj.portMapping) {
                        d('[' + key + '] Is working on rule: ' + rule)
                        if (loop != 0) {
                            if (loop == len - 1) {
                                string = string + '>;' + rules[rule].remotePort + ';' + rules[rule].server + ';' + rules[rule].serverPort + ';1;'
                            }else {
                                string = string + '^;' + rules[rule].remotePort + ';' + rules[rule].server + ';' + rules[rule].serverPort + ';1;\n'
                            }
                        }
                        loop++;
                    }
                }
            }
        }
    }
    d('Finished conversion.')
    callback(string);
}

function d(string) {
    if (debug) {
        console.log("[DEBUG] " + string)
    }
}
function m(string) {
    if (silent == undefined || silent == false) {
        console.log(string)
    }
}

function normalPrint() {
    m('-----------------[BT-LANTIS]-----------------')
    m('A better config system for LANTIS.\ngithub.com/nevexo')
    m('Support: nevexo.space/contact\n')
}
function help() {
    m('Arguments:')
    m('-v --verbose - Verbose/debugging messages')
    m("-s --silent - Don't print anything to the console. (Apart from debug messages)")
    m('-a --about - About the project')
    m('-c - Pass a json file and export file (btl -c config.json ports.lantis.conf) - Leave the second arg blank to print to console.')
    m('-wa --web-app - Launch LANTISWeb Server. (This is a daemon)')
    process.exit(0)
}
function loadMods() { //Load modules later, so if the program is started with no args or -h, the program doesn't take ages to god damn start.
    fs = require('fs')
}

function webServer(config) {
    var koa = require('koa')
    var Router = require('koa-router')
    var router = new Router();
    const app = new koa();
    router.get('/', function(ctx, next) {
        ctx.body = 'Server'
    })
    app.use(router.routes())
    app.listen(config.port, function() {
        m('[WEBSERVER] Up on port: ' + config.port)
    })
}

var args = process.argv.slice(2); //Get CLI args.

if (args.indexOf('-s') > -1 || args.indexOf('--silent') > -1) { //Silent mode
    silent = true;
}else {
    silent = false;
}

normalPrint() //Print the intro messages
if (args.length == 0 || args.indexOf('-h') > -1) {
    help()
}
//Setup verbose mode
if (args.indexOf('-v') > -1 || args.indexOf('--verbose') > -1) {
    debug = true
    d('Verbose mode enabled.')
}
if (args.indexOf('-a') > -1 || args.indexOf('--about') > -1) {
    m('Welcome to BT-LANTIS (Better-LANTIS)\nLANTIS itself is an SSH port-forarding router.')
    m('It has a horrid config that is really hard to understand, this program allows you to make a nicely')
    m('formatted JSON config file, and have it converted over for you.')
    m('It also contains a webAPI, that can be activated with --webApp or -wa')
    m('For more information visit https://github.com/nevexo/bt-lantis')
    m('And to get a copy of LANTIS, visit https://code.acr.moe')
    process.exit(0)
}
if (args.indexOf('-c') > -1){
    d('[ARGS] Calling converter.')
    convert(args, function(result) {
        m('[INFO] Config processed!')
        if (args[args.indexOf('-c') + 2] == '' || args[args.indexOf('-c') + 2] == undefined){
            m(result)
        }else {
            m('[INFO] Config will be written to: ' + args[args.indexOf('-c') + 2])
            fs.writeFile(args[args.indexOf('-c') + 2], result, function(err) {
                d('[INFO] Disk callback!')
                if (err) {
                    m('[ERROR] ' + err)
                }else {
                    m('[INFO] Config written!')
                }
            })
        }
    })
}
if (args.indexOf('-wa') > -1 || args.indexOf('--web-app')> -1) {
    m('[WEBSERVER] The webserver will now be started.')
    
    try{
        var config = require('./webServer.json')
    }catch (err) {
        m('[ERROR] The webserver failed to spinup!')
        m('[WEBSERVER] No webServer.json was found. One has been generated, please edit it & restart BT-LANTIS.')
        var config = { //Default web server config
            "port": 3000,
            "user": 'admin',
            "password": "LANTIS@2018!",
            "lantisExe": "lantis.bash",
            "lantisConf": "ports.lantis.conf",
            "btlanConf": "config.json"
        }
        fs.writeFile('webServer.json', JSON.stringify(config), function(err) {
            if (err) {
                m('[ERROR] Failed to write new config: ' + err)
            }
        })
        process.exit(1)
    }
    webServer(config)
}