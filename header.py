import struct


class DNSHeader:
    def __init__(self, packet_identifier=1234, query_response=1, operation_code=0, authoritative_answer=0,
                 truncation=0, recursion_desired=0, recursion_available=0, reserved=0, response_code=0,
                 question_count=0, answer_record_count=0, authority_record_count=0, additional_record_count=0):
        
        self.packet_identifier = packet_identifier
        # Combine all flags into one 16-bit integer
        self.query_response = query_response
        self.operation_code = operation_code
        self.authoritative_answer = authoritative_answer
        self.truncation = truncation
        self.recursion_desired = recursion_desired
        self.recursion_available = recursion_available
        self.reserved = reserved
        self.response_code = response_code

        self.flags = 0  # Initialize flags as 0
        self.question_count = question_count
        self.answer_record_count = answer_record_count
        self.authority_record_count = authority_record_count
        self.additional_record_count = additional_record_count

        self._build_flags()  # Build the flags field

    def _build_flags(self):
        # Combine all flag fields into a 16-bit value
        self.flags |= (self.query_response << 15)   # 1-bit
        self.flags |= (self.operation_code << 11)   # 4-bit
        self.flags |= (self.authoritative_answer << 10)  # 1-bit
        self.flags |= (self.truncation << 9)        # 1-bit
        self.flags |= (self.recursion_desired << 8) # 1-bit
        self.flags |= (self.recursion_available << 7)  # 1-bit
        self.flags |= (self.reserved << 4)          # 3-bit
        self.flags |= (self.response_code)          # 4-bit

    def build_header(self):
        # Use struct to pack the header fields into a binary format
        return struct.pack('!HHHHHH',
                           self.packet_identifier,
                           self.flags,
                           self.question_count,
                           self.answer_record_count,
                           self.authority_record_count,
                           self.additional_record_count)

    def __repr__(self):
        return (f'''DNSHeader(packet_identifier={self.packet_identifier}, query_response={self.query_response}, 
                operation_code={self.operation_code}, authoritative_answer={self.authoritative_answer}, 
                truncation={self.truncation}, recursion_desired={self.recursion_desired}, 
                recursion_available={self.recursion_available}, reserved={self.reserved}, 
                response_code={self.response_code}, question_count={self.question_count}, 
                answer_record_count={self.answer_record_count}, authority_record_count={self.authority_record_count}, 
                additional_record_count={self.additional_record_count})''')
