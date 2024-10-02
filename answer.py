import struct


class DNSAnswer:
    def __init__(self, domain_name, record_type=1, record_class=1, time_to_live=60, ip_address='8.8.8.8'):
        self.domain_name = domain_name
        self.record_type = record_type
        self.record_class = record_class
        self.time_to_live = time_to_live
        self.ip_address = ip_address

    def encode_domain_name(self):
        labels = self.domain_name.split('.')
        encoded_name = b''
        for label in labels:
            encoded_name += struct.pack('B', len(label)) + label.encode('ascii')
        
        encoded_name += b'\x00'
        return encoded_name
    
    def encode_ipaddress(self):
        return struct.pack('!BBBB',*[int(octet) for octet in self.ip_address.split('.')])

    def build_answer(self):
        encoded_name = self.encode_domain_name()
        encoded_ipaddress = self.encode_ipaddress()
        return (encoded_name + struct.pack('!HHI', self.record_type, self.record_class,self.time_to_live)+struct.pack('!H',len(encoded_ipaddress)) + encoded_ipaddress)
