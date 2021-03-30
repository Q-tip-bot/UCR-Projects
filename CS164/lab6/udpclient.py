import socket   #for sockets
import sys  #for exit
import threading
import time
import logging
from check import ip_checksum # Use Checksum function provided
 
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
 
host = 'localhost'
port = 8519
SeqNum = 0
packet = ""
j = 3 # make this equal to 5 when testing delay

def Timeout():
  print 'Timed Out: Retry sending Packet' + str(SeqNum)
  msg = 'Hello ' + str(SeqNum)
  check = ip_checksum(msg)
  packet = str(SeqNum) + str(len(msg)) + msg + check
  s.sendto(packet, (host, port))

Corrupt = raw_input("Do you want there to be a corrupt packet?(Y or N)")

while(1) :
    progress = raw_input("Press Enter to send more packets")
    for i in range(0, j):
      t = threading.Timer(2.0, Timeout)
      msg = 'Hello ' + str(SeqNum)
      if i == 1 and Corrupt == 'Y':
        check = str(1) + ip_checksum(msg)
      else:
        check = ip_checksum(msg)
      packet = str(SeqNum) + str(len(msg)) + msg + check

      try :
        #Send the whole string
        t.start()
        s.sendto(packet, (host, port))
        d = s.recvfrom(1024)
        packet = d[0]
        AckNum = int(packet[0])
        replylength = int(packet[1])
        reply = packet[2:replylength+2]
        check = packet[replylength+2:]
        addr = d[1]

        if check == ip_checksum(reply) and AckNum == SeqNum:
          t.cancel()
          print 'Server reply : ' + reply
          if SeqNum == 1:
            SeqNum = 0
          elif SeqNum == 0:
            SeqNum = 1
        else:
          print 'Error: Message Corrupt or has wrong sequence number, waiting for another ACK'
             
        if not d:
          break

      except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

s.close()
