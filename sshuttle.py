#!/usr/bin/env python
## REQUIRES MINIMUM PY VERSION 2.7
from __future__ import print_function

import os
import sys
import json
import signal
import socket
import subprocess
from subprocess import CalledProcessError
import logging
import logging.handlers

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

conf = "/etc/sshuttle/config.json"
ssh_user = "sshuttle"  ## username thats used for SSH connection

def precheck():
    if len(sys.argv) < 2:
        print("need to pass argument: start | stop | restart | status ")
        sys.exit()
    
    if sys.argv[1] in ["help", "-h", "--help", "h"]:
        print("sshuttle.py start | stop | restart | status")
        sys.exit()

    if not sys.argv[1] in ["start", "stop", "restart", "status"]:
        print("usage: sshuttle.py start | stop | restart | status")
        sys.exit()
    
    if not os.path.exists(conf):
        print("no sshuttle config file present, exiting.")
        sys.exit()
    
    # check if sshuttle is installed
    try:
        subprocess.check_output(["which", "sshuttle"]).strip()
    except CalledProcessError:
        print("sshuttle is not installed on this host")
        sys.exit()
        
def start():

    with open(conf) as jsondata:
        data = json.load(jsondata)

    for rhost in data.keys():
        netrange = ""

        # if single network, turn into List
        if not type(data[rhost]) is list:
            networks = data[rhost].split()
        else:
            networks = data[rhost]

        for network in networks:
            
            # check if CIDR format
            if "/" in network:
                netrange = netrange + " " + network
            else:
                netrange = netrange + " " + socket.gethostbyname(network)
        netrange = netrange.strip()
        
        # build rpath
        rpath = "-r {0}@{1} {2} -l listen '0.0.0.0' --ssh-cmd 'ssh -o ServerAliveInterval=60' --no-latency-control".format(ssh_user, rhost, netrange)
        try:
            print("starting sshuttle..")
            log.info("starting sshuttle for networks: %s via %s" % (netrange, rhost))
            subprocess.Popen("sshuttle {}".format(rpath), shell=True) 
        except CalledProcessError as err:
            log.error("error running sshuttle: %s" % str(err))

def get_pid():
    search = "ps -ef | grep '/usr/bin/python /usr/share/sshuttle/main.py /usr/bin/python -r' | grep -v grep | awk {'print $2'}"    
    pids = []
    for line in os.popen(search):
        fields = line.split()
        pids.append(fields[0])
    return pids

def stop():
    pids = get_pid()
    for pid in pids:
        print("stopping sshuttle PID %s " % pid)
        log.info("stopping sshuttle")
        os.kill(int(pid), signal.SIGTERM)

def status():
    pids = get_pid()
    if pids:
        print("sshuttle is running..")
    else:
        print("sshuttle is not running..")

if __name__ == "__main__":

    precheck()

    cmd = sys.argv[1].lower()

    if cmd == "start":
        start()

    if cmd == "stop":
        stop()
    
    if cmd == "restart":
        print("restarting sshuttle..")
        stop()
        start()
        
    if cmd == "status":
        status()
