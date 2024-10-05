class DNSRecordPreamble:
    def __init__(self, domain_name, record_type, record_class, time_to_live, data_length):
        self.domain_name: str = domain_name
        self.record_type: int = record_type
        self.record_class = record_class
        self.TTL = time_to_live
        self.data_length = data_length

class DNSRecord:
    def __init__(self, preamble: DNSRecordPreamble, ip_address: str):
        self.preamble = preamble
        self.ip = ip_address