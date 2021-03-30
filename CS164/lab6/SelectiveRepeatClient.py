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
port = 8520

N = 4 # This is the window size
base = 0
nextseqnum = 0
sndpkt = []
rcvacks = []
packet = ""
AckNum = 0
Resend = False

def Timeout(i):
  #t = threading.Timer(2.0, Timeout, [i])
  #t.start()
  print 'Timed Out: Retry sending Packet' + str(i)
  s.sendto(sndpkt[i], (host, port))

Corrupt = raw_input("Do you want there to be a corrupt packet?(Y or N)")
t = threading.Timer(2.0, Timeout, [base])

while(1):
    # Only start timer for packets whose ACKS have not been buffered
    if AckNum+1 == base and nextseqnum <8:
      t = threading.Timer(2.0, Timeout, [base])
      t.start()

    # Send all the data up to the window size
    while nextseqnum < base+N and nextseqnum < 8:
      msg = 'Hello ' + str(nextseqnum)
      if nextseqnum == 2 and Corrupt == 'Y' or Corrupt == 'y':
        check = str(1) + ip_checksum(msg)
      else:
        check = ip_checksum(msg)
      packet = str(nextseqnum) + str(len(msg)) + msg + check
      sndpkt.append(packet)

      try :
        #Send the whole string
        s.sendto(packet, (host, port))

        # if the packet was corrupted, make sure to send a non corrupt one later
        if nextseqnum == 2 and (Corrupt == 'Y' or Corrupt == 'y'):
          check = ip_checksum(msg)
          packet = str(nextseqnum) + str(len(msg)) + msg + check
          sndpkt[2] = packet
        nextseqnum+=1
        
      except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    # Wait for a reply to increment the window
    d = s.recvfrom(1024)
    packet = d[0]
    AckNum = int(packet[0])
    replylength = int(packet[1])
    reply = packet[2:replylength+2]
    check = packet[replylength+2:]
    addr = d[1]

    if not d:
      break

    if check == ip_checksum(reply) and AckNum == base:
      # ack the arriving packet
      print 'Server reply : ' + reply
      base+=1
      t.cancel()

      # ack all the recorded ack's and move the window
      for i in range(len(rcvacks)):
        pkt = rcvacks[i]
        rplylength = int(pkt[1])
        rply = pkt[2:replylength+2]
        print 'Server reply : ' + rply
        base+=1
      del rcvacks[:]
      
    elif check == ip_checksum(reply) and AckNum > base and AckNum < base+N:
      print 'Received ACK' + str(AckNum) + " recording..."
      rcvacks.append(packet)

    else:
      print 'Packet Corrupt: Ignoring...'

s.close()
