import socket
import sys
import threading
import time
from check import ip_checksum
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8520 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

# Variables
ExpectedSeqNum = 0
N = 4
msg = "ACK" + str(ExpectedSeqNum)
check = ip_checksum(msg)
packet = str(ExpectedSeqNum) + str(len(msg)) + msg + check
rcvpkts = []
base = 0

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

      # If packet received is the base packet
      elif check == ip_checksum(data) and SeqNum == base:
        msg = "ACK" + str(SeqNum)
        check = ip_checksum(msg)
        packet = str(SeqNum) + str(len(msg)) + msg + check
        s.sendto(packet, addr)
        base+=1
        print 'Message[' + str(addr[1]) + ':' + str(addr[1]) + '] - ' + data.strip()
        
        # Check to see if any other saved data needs to be sent up
        for i in range(len(rcvpkts)):
          pkt = rcvpkts[i]
          data = pkt[2:datalength+2]
          print 'Message['+str(addr[1]) + ':' + str(addr[1]) + '] - ' + data.strip()
          base+=1
        del rcvpkts[:]

      # If packet received is greater that the base
      elif check == ip_checksum(data) and SeqNum > base and SeqNum < base+N:
        print 'Packet' + str(SeqNum) + ' received, saving packet...'
        rcvpkts.append(packet)
        msg = "ACK" + str(SeqNum)
        check = ip_checksum(msg)
        packet = str(SeqNum) + str(len(msg)) + msg + check
        s.sendto(packet, addr)
      
      # If packet sent is older than the window size resend that ACK
      #elif SeqNum < base:
      #  print 'Resending packet' + str(SeqNum)
      #  msg = 'ACK' + str(SeqNum)
      #  check = ip_checksum(msg)
      #  packet = str(SeqNum) + str(len(msg)) + msg + check
      #  s.sendto(packet, addr)

      # if packet is corrupt then ignore it
      else:
        print 'Packet Corrupt: ignoring'

s.close()
