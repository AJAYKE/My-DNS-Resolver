from app.answer import DNSRecord, DNSRecordPreamble
from app.header import DNSMessageHeader
from app.message import DNSMessage
from app.question import DNSQuestion


class DNSMessageEncoder(object):
    @staticmethod
    def __encode(number: int, number_of_bytes: int) -> bytes:
        # Get the sequence of bytes representing the number in big-endian format as required by the DNS specification
        return (number).to_bytes(number_of_bytes, byteorder='big')

    # Get the bytes representing the domain name (it will be encoded as a sequence of labels)
    @staticmethod
    def __encode_label_sequence(name: str) -> bytes:
        label_sequence = b''

        for segment in name.split('.'):
            label_sequence += DNSMessageEncoder.__encode(len(segment), 1) + segment.encode('UTF-8')
        label_sequence += b'\x00'

        return label_sequence
    
    @staticmethod
    def get_header_bytes(header: DNSMessageHeader) -> bytes:
        header_bytes: bytes = b''

        header_bytes += DNSMessageEncoder.__encode(header.packet_id, 2)

        # Encode this next byte composed by multiple header fields
        next_byte_as_binary_string = str(header.query_or_response_indicator) + '{0:04b}'.format(header.operation_code) + str(header.authoritative_answer) + str(header.truncation) + str(header.recursion_desired)
        header_bytes += DNSMessageEncoder.__encode(int(next_byte_as_binary_string, 2), 1)

        # Encode this next byte composed by multiple header fields
        next_byte_as_binary_string = str(header.recursion_available) + '{0:03b}'.format(header.reserved) + '{0:04b}'.format(header.response_code)
        header_bytes += DNSMessageEncoder.__encode(int(next_byte_as_binary_string, 2), 1)

        header_bytes += DNSMessageEncoder.__encode(header.question_count, 2)
        header_bytes += DNSMessageEncoder.__encode(header.answer_record_count, 2)
        header_bytes += DNSMessageEncoder.__encode(header.authority_record_count, 2)
        header_bytes += DNSMessageEncoder.__encode(header.additional_record_count, 2)

        return header_bytes
    
    @staticmethod
    def get_question_bytes(question: DNSQuestion) -> bytes:
        question_name = DNSMessageEncoder.__encode_label_sequence(question.domain_name)
        question_bytes: bytes = question_name + DNSMessageEncoder.__encode(question.record_type, 2) + DNSMessageEncoder.__encode(question.question_class, 2)
        
        return question_bytes
        
    @staticmethod
    def get_preamble_bytes(preamble: DNSRecordPreamble) -> bytes:
        preamble_bytes: bytes = DNSMessageEncoder.__encode_label_sequence(preamble.domain_name)
        preamble_bytes += DNSMessageEncoder.__encode(preamble.record_type, 2)
        preamble_bytes += DNSMessageEncoder.__encode(preamble.record_class, 2)
        preamble_bytes += DNSMessageEncoder.__encode(preamble.TTL, 4)
        preamble_bytes += DNSMessageEncoder.__encode(preamble.data_length, 2)

        return preamble_bytes

    @staticmethod
    def get_record_bytes(record: DNSRecord):
        encoded_ip = b''.join(DNSMessageEncoder.__encode(int(ip_byte), 1) for ip_byte in record.ip.split('.'))

        return DNSMessageEncoder.get_preamble_bytes(record.preamble) + encoded_ip
    
    
    @staticmethod
    def encode_message(dns_message: DNSMessage) -> bytes:
        message_bytes: bytes = DNSMessageEncoder.get_header_bytes(dns_message.header)
        message_bytes += b''.join([DNSMessageEncoder.get_question_bytes(question) for question in dns_message.questions])
        message_bytes += b''.join([DNSMessageEncoder.get_record_bytes(record) for record in dns_message.answers])

        return message_bytes
