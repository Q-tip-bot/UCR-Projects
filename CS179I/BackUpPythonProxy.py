# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
#Copyright (c) <2009> <F?bio Domingues - fnds3000 in gmail.com>
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

"""\
Copyright (c) <2009> <F?bio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy ? um Elie Proxy.

Suporta os m?todos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conex?es dos cliente em IPv4 ou IPv6;
 - Conex?es ao alvo em IPv4 e IPv6;
 - Conex?es todo o tipo de transmiss?o de dados TCP (CONNECT tunneling),
     p.e. liga??es SSL, como ? o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente est? correcto;
   - Enviar os devidos HTTP erros se n?o, ou simplesmente quebrar a liga??o;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excep??es nos s?tios onde ? previs?vel a ocorr?ncia de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     vari?veis e m?todos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy an?nimo e transparente;
 - Suportar FTP?.


(!) Aten??o o que se segue s? tem efeito em conex?es n?o CONNECT, para estas o
 proxy ? sempre Elite.

Qual a diferen?a entre um proxy Elite, An?nimo e Transparente?
 - Um proxy elite ? totalmente an?nimo, o servidor que o recebe n?o consegue ter
     conhecimento da exist?ncia do proxy e n?o recebe o endere?o IP do cliente;
 - Quando ? usado um proxy an?nimo o servidor sabe que o cliente est? a usar um
     proxy mas n?o sabe o endere?o IP do cliente;
     ? enviado o cabe?alho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informa??o que
     se est? a usar um proxy.
     S?o enviados os cabe?alhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

import socket, thread, select

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        
        #print the request and it extracts the protocol and path
        self.method, self.path, self.protocol = self.get_base_header()
        
        if self.method=='CONNECT':
            self.method_CONNECT()

        #handle the GET request
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):            
            self.method_others()

        self.client.close()
        self.target.close()

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break

        #print the request
        print '%s'%self.client_buffer[:end]#debug
        
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()        

    #forward the packet to its final destination
    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]        
        path = self.path[i:]
        self._connect_target(host)

        #TO DO: first find out the Content-Length by sending a RANGE request
#--------------------------------------------------------------------------------
        # First we send a HEAD Request by changing the self.method to 'HEAD'
        
        temp_method = self.method
        self.method = 'HEAD'
        self.target.send('%s %s %s\n'%(self.method,path,self.protocol)+
			self.client_buffer)

        # After sending the HEAD request we then save the reply as a string
        # and parse it to find the Content-Length
        Header_String = str(self.target.recv(BUFLEN))
        Position = Header_String.find("Content-Length:")
        Parsed_String = Header_String[Position:]
        End_Parse = Parsed_String.find('\n')
        Content_Length = int(Parsed_String[len("Content-Length: "):End_Parse])
        Split_Content = Content_Length / 2

        # After finding the Content-Length we then change self.method to 'GET'
        self.method = temp_method

        # The first GET only asks for RANGE bytes=0-Split_Content (half the content)
        self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+
                         "Range: bytes=0-"+str(Split_Content)+'\n'+
			self.client_buffer)

        #TO DO: need to send another request to "target2" that GETs a different range of bytes
#-------------------------------------------------------------------------------
	# This second GET will ask for RANGE bytes=Split_Content-Content_length
	# and will do it through a separate socket
	self.target2.send('%s %s %s\n'%(self.method, path, self.protocol)+
			  "Range: bytes="+str(Split_Content+1)+"-"
			  +str(Content_Length)+'\n'+self.client_buffer)
 
	'''
	# For testing the throughput when using a single port
	self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+ 
			self.client_buffer)
	'''
       
	self.client_buffer = ''

        #start the read/write function
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
  
	# Both targets are the same but are contacted through different sockets
	# Creates the first socket to send data out of
        self.target = socket.socket(soc_family)
        self.target.connect(address)

	# Creates the second socket to send data out of
        self.target2 = socket.socket(soc_family)
        self.target2.connect(address)

    #"revolving door" to re-direct the packets in the right direction
    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
#TO DO: merge the data from both interfaces into one big data, if we are receiving
#------------------------------------------------------------------------------
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break

#start the proxy server and listen for connections on port 8080
def start_server(host='localhost', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port)#debug
    soc.listen(0)
    try:
        while 1:
            thread.start_new_thread(handler, soc.accept()+(timeout,))
    except:
        self.target.close()

if __name__ == '__main__':
    start_server()
