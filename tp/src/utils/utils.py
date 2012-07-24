#!/usr/bin/env python

import os
import sys

from netifaces import interfaces, ifaddresses
import ipaddr



def convert_netmask_to_cidr(netmask):
    """
    Converts a netmask (255.255.255.0) to CIDR notation 24
    """
    count = 0
    for octect in netmask.split("."):
        octect = int(octect)
        while octect != 0:
            if octect % 2 == 1:
                count = count + 1
            octect = octect / 2
    return count

def get_networks_to_scan():
    """
    This will get every interface on the node that this is running on
    and report back the ip address, netmask, and CIDR in a dictionary
    """
    gnts = {}
    valid_interfaces = interfaces()[1:]
    for interface in valid_interfaces:
        iface = ifaddresses(interface)[2][0]
        addr = iface['addr']
        netmask = iface['netmask']
        cidr = convert_netmask_to_cidr(netmask)
        gnts[addr] = {
                      'addr' : addr,
                      'netmask' : netmask,
                      'cidr' : cidr,
                     } 
    return gnts

def verify_network(network):
    is_valid = None
    try:
        addr = ipaddr.IPv4Network(network)
        if not addr.is_reserved and not addr.is_multicast \
            and not addr.is_loopback:
            is_valid = True
        else:
            is_valid = False
    except Exception as e:
        is_valid = False
    return is_valid

