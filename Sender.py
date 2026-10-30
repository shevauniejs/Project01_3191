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
        r_address = (dest,port)
        INIT = 1
        base = 1
        nextseqnum = 1
        N = 3 # window size, should be seven
        packetBuffer = [None]*N
        kinds = ("syn", "ack", "fin", "dat")
        chunk = 1472
        marker = 0
        
        file = self.infile.read()
        self.infile.seek(0,2)
        size = self.infile.tell()
        self.infile.seek(0)
        
        #start handshake
        init_handshake = super(Sender, self).make_packet(kinds[0], 0,"")
        super(Sender, self).send(init_handshake, r_address);
        packetBuffer[0] = ""
        
        init_handshake_response = super(Sender, self).receive()
        while init_handshake_response == None or Checksum.validate_checksum(init_handshake_response)==False:
                    super(Sender, self).send(packetBuffer[packPos], r_address)
        splitMessage = super(Sender, self).split_packet(init_handshake_response)
        kind, ack, data, cksm = splitMessage[0], int(splitMessage[1]), splitMessage[2], splitMessage[3]
        start = Checksum.validate_checksum(init_handshake_response) and ack==INIT           
            
        while start:
            if marker>=size:
                fin = super(Sender, self).make_packet(kinds[2],nextseqnum, "")
                super(Sender, self).send(data_packet, r_address)
                self.infile.close()
                break
            if nextseqnum<base+N :
                data = file[marker:chunk]
                marker=chunk
                chunk+=chunk
                packPos = nextseqnum%N                
                print "make packet \n"
                data_packet = super(Sender, self).make_packet(kinds[3],nextseqnum, data)
                packetBuffer[packPos] = data_packet
                super(Sender, self).send(data_packet, r_address)
                nextseqnum+=1
            print "receive packet\n"
            response = super(Sender, self).receive(.005)
            while response== None:
                    super(Sender, self).send(packetBuffer[packPos], r_address)
            splitResp = super(Sender, self).split_packet(response)
            kind, ack, data, cksm = splitResp[0], int(splitResp[1]), splitResp[2], splitResp[3]
            base = ack
        

                
            
        
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
