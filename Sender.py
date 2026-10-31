import sys
import getopt

import Checksum
import BasicSender


'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug

    # Main sending loop.
    def start(self):
        from time import sleep
        r_address = (dest,port)
        INIT = 1
        base = 1
        nextseqnum = 1
        N = 3 # window size, should be seven
        packetBuffer = [None]*N
        kinds = ("syn", "ack", "fin", "dat")
        chunk = 100 # should be 1471
        marker = 0
        delay = .01
        
        cache = self.infile.read()
        self.infile.seek(0,2)
        size = self.infile.tell()
        self.infile.seek(0)
        
        nPack = size//chunk + 1
        print "number of packets %d" % nPack
        #start handshake - make packet w/ seq #0 then send
        init_handshake = super(Sender, self).make_packet(kinds[0], 0,"")
        super(Sender, self).send(init_handshake, r_address);
        packetBuffer[0] = init_handshake
        
        #send and loop until valid syn-ack received 
        init_handshake_response = super(Sender, self).receive(delay)
        while init_handshake_response == None or Checksum.validate_checksum(init_handshake_response)==False:
            super(Sender, self).send(packetBuffer[0], r_address)
            init_handshake_response = super(Sender, self).receive(delay)
        #validate connect and start main loop    
        splitMessage = super(Sender, self).split_packet(init_handshake_response)
        kind, ack, data, cksm = splitMessage[0], int(splitMessage[1]), splitMessage[2], splitMessage[3]
        start = Checksum.validate_checksum(init_handshake_response) and ack==INIT
        
        while base<nPack: #
            while nextseqnum<base+N and nextseqnum<nPack:
                if chunk>size:
                    start = False
                data = cache[marker:chunk] #get data from cache,
                marker=chunk
                if chunk<size:
                    chunk+=chunk
                else:
                    chunk+=size-chunk
                packPos = nextseqnum%N  #a packet's position in d'buffer is mod window size              
                #print data
                data_packet = super(Sender, self).make_packet(kinds[3],nextseqnum, data)
                packetBuffer[packPos] = data_packet #buffer packet incase of loss
                super(Sender, self).send(data_packet, r_address)
                nextseqnum+=1  
#####################################################################            
            print "Stopped sending packets"
            response = super(Sender, self).receive(delay)
            while response == None:
                super(Sender, self).send(packetBuffer[packPos], r_address)
                response = super(Sender, self).receive(delay)
                    #print response
            splitResp = super(Sender, self).split_packet(response)
            kind, ack, data, cksm = splitResp[0], int(splitResp[1]), splitResp[2], splitResp[3]
            if kind == "sack":
                sackData = ack.split(";")
                qack, sacks= int(sackData[0]), sackData[1]
                print qack
            if ack > base and Checksum.validate_checksum(response):
                base = ack
                #lrAck time = 
            else:
                super(Sender, self).send(packetBuffer[base%N], r_address)
                response = super(Sender, self).receive(delay)
            base = ack
                
            #print ack
            #start==false
            #print packetBuffer
        #fin = super(Sender, self).make_packet(kinds[2],nextseqnum, "")
        #super(Sender, self).send(data_packet, r_address)
        #self.infile.close()
        

                
            
        
'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest,port,filename,debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
