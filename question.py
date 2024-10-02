import struct


class DNSQuestion:
    def __init__(self,domain_name, record_type=1,record_class=1):
        self.domain_name = domain_name
        self.record_type = record_type
        self.record_class = record_class

    
    def encode_domain_name(self):
        labels = self.domain_name.split('.')
        encoded_name = b''
        for label in labels:
            encoded_name += struct.pack('B',len(label))+label.encode('ascii')
        encoded_name += b'\x00'
        return encoded_name
    
    def build_question(self):
        encoded_name = self.encode_domain_name()
        return encoded_name + struct.pack('!HH',self.record_type,self.record_class)
    

