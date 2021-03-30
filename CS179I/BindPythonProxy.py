# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
#Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com>
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
Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy é um Elie Proxy.

Suporta os métodos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conexões dos cliente em IPv4 ou IPv6;
 - Conexões ao alvo em IPv4 e IPv6;
 - Conexões todo o tipo de transmissão de dados TCP (CONNECT tunneling),
     p.e. ligações SSL, como é o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente está correcto;
   - Enviar os devidos HTTP erros se não, ou simplesmente quebrar a ligação;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excepções nos sítios onde é previsível a ocorrência de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     variáveis e métodos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy anónimo e transparente;
 - Suportar FTP?.


(!) Atenção o que se segue só tem efeito em conexões não CONNECT, para estas o
 proxy é sempre Elite.

Qual a diferença entre um proxy Elite, Anónimo e Transparente?
 - Um proxy elite é totalmente anónimo, o servidor que o recebe não consegue ter
     conhecimento da existência do proxy e não recebe o endereço IP do cliente;
 - Quando é usado um proxy anónimo o servidor sabe que o cliente está a usar um
     proxy mas não sabe o endereço IP do cliente;
     É enviado o cabeçalho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informação que
     se está a usar um proxy.
     São enviados os cabeçalhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

Content_Length = 0
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
	
        global Content_Length 
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
			  "Range: bytes="+str(Split_Content+3)+"-"
			  +str(Content_Length)+'\n'+self.client_buffer)
 
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
        #(soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
  
	# Both targets are the same but are contacted through different sockets
	# Creates the first socket to send data out of
        self.target = socket.socket(socket.AF_INET)
	self.target.bind(('192.168.1.29',4444))
        self.target.connect(('speedtest.ftp.otenet.gr',80))

	# Creates the second socket to send data out of
        self.target2 = socket.socket(socket.AF_INET)
	self.target.bind(('192.168.1.22',4440))
        self.target2.connect(('speedtest.ftp.otenet.gr',80))

    #"revolving door" to re-direct the packets in the right direction
    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target, self.target2]
	target2_buff = ''
	target1_buff = ''
        count = 0
	global Content_Length
	done = False
        while not done:
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
#---------------------------------------------------------------------------------
			# when the data is coming from the target's then buffer
			# them so we can merge them
			if in_ is self.target2:
			    target2_buff = target2_buff + str(data)
			elif in_ is self.target:
			    target1_buff = target1_buff + str(data)
 			else:
			    out.send(data)


			if (len(target1_buff) + len(target2_buff)) >= Content_Length+300:
			    # In order to merge the data we first must parse the 
			    # header to look like A normal GET request instead of 
			    # a Partial Request
			    target1_buff = target1_buff.replace("206", "200",1)
			    target1_buff = target1_buff.replace("Partial", "OK",1)
			    target1_buff = target1_buff.replace("Content", "",1)
			    beginning_pos = target1_buff.find("Content-Length:")
			    end_pos = target1_buff.find('\n',beginning_pos)
			    target1_buff = target1_buff.replace(target1_buff[beginning_pos+16:end_pos],str(Content_Length))
			    beginning_pos = target1_buff.find("Content-Range:")
			    end_pos = target1_buff.find('\n',beginning_pos)
			    target1_buff = target1_buff[:beginning_pos] + target1_buff[end_pos+1:]

			    # Now we must remove the Header from Target2 and 
			    # append the data onto the first packet
			    beginning_pos = target2_buff.find("Content-Range: ")
			    end_pos = target2_buff.find('\n',beginning_pos)
			    target2_buff = target2_buff[end_pos+1:] 	

			    merged_data = target1_buff + target2_buff
			    self.client.send(merged_data)
			    done = True

                        count = 0

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
