import socket
import sys
import threading
import time
from check import ip_checksum
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8519 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
ExpectedSeqNum = 0;
delay = True
which_packet = 0

normal = raw_input("Do you want to delay the ACK? (Y or N)")
if normal == 'Y':
  delay = True
else:
  delay = False

#now keep talking with the client
while 1:
      # receive data from client (data, addr)
      d = s.recvfrom(1024)
      packet = d[0]
      SeqNum = int(packet[0])
      datalength = int(packet[1])
      data = packet[2:datalength+2]
      check = packet[datalength+2:]
      addr = d[1]
 
      if not data: 
        break
      elif check == ip_checksum(data) and ExpectedSeqNum == SeqNum:
        msg = "ACK" + str(ExpectedSeqNum)
        check = ip_checksum(msg)
        packet = str(ExpectedSeqNum) + str(len(msg)) + msg + check
        if delay and which_packet == 1:
          time.sleep(3)
          delay = False
        which_packet+=1
        s.sendto(packet, addr)
        if ExpectedSeqNum == 1:
          ExpectedSeqNum = 0
        elif ExpectedSeqNum == 0:
          ExpectedSeqNum = 1
        print 'Message[' + str(addr[1]) + ':' + str(addr[1]) + '] - ' + data.strip()
      else:
        print 'Error: Message Corrupt or received duplicate packet'
        if ExpectedSeqNum != SeqNum:
          msg = "ACK" + str(SeqNum)
          check = ip_checksum(msg)
          packet = str(SeqNum) + str(len(msg)) + msg + check
          s.sendto(packet,addr)

s.close()
