from app.answer import DNSRecord, DNSRecordPreamble
from app.constants import *
from app.message import DNSMessage
from app.question import DNSQuestion


class DNSMessageParser(object):
    def __init__(self, raw_dns_message: bytes):
        self.__raw_message = raw_dns_message
        self.__message = DNSMessage()

        self.parse_header()
        pointer = self.parse_questions(self.message.header.question_count)
        self.raw_answer_bytes: bytes = self.__raw_message[pointer:]
        self.parse_answer_records(pointer, self.message.header.answer_record_count)
    
    @property
    def message(self):
        return self.__message


    def parse_header(self):
        header: bytes = self.__raw_message[0:HEADER_LENGTH_IN_BYTES]
        bytes_sequence_position = 0

        # Parse all the header fields/attributes
        packet_id = int.from_bytes(header[bytes_sequence_position:HEADER_PACKET_ID_LENGTH_IN_BYTES])
        bytes_sequence_position += HEADER_PACKET_ID_LENGTH_IN_BYTES

        # Take the next byte which is composed by multiple header fields
        next_composite_byte = header[bytes_sequence_position:bytes_sequence_position + 1]
        bytes_sequence_position += 1

        # From the byte to bits, removing the '0b' preffix
        next_composite_bits = format(int.from_bytes(next_composite_byte), '08b')
        query_response = int(next_composite_bits[0])
        operation_code = int(next_composite_bits[1:5], base=2)
        authoritative_answer = int(next_composite_bits[5])
        truncated_message = int(next_composite_bits[6])
        recursion_desired = int(next_composite_bits[7])

        self.message.header.packet_id = packet_id
        self.message.header.query_or_response_indicator = query_response
        self.message.header.operation_code = operation_code
        self.message.header.authoritative_answer = authoritative_answer
        self.message.header.truncation = truncated_message
        self.message.header.recursion_desired = recursion_desired

        next_composite_byte = header[bytes_sequence_position:bytes_sequence_position + 1]
        bytes_sequence_position += 1

        # From the byte to bits, removing the '0b' preffix
        next_composite_bits = format(int.from_bytes(next_composite_byte), '08b')
        recursion_available = int(next_composite_bits[0])
        reserved = int(next_composite_bits[1:4], base=2)
        response_code = int(next_composite_bits[4:8], base=2)

        self.message.header.recursion_available = recursion_available
        self.message.header.reserved = reserved
        self.message.header.response_code = response_code

        self.message.header.question_count = int.from_bytes(header[bytes_sequence_position : bytes_sequence_position + HEADER_QUESTION_COUNT_LENGTH_IN_BYTES])
        bytes_sequence_position += HEADER_QUESTION_COUNT_LENGTH_IN_BYTES


        self.message.header.answer_record_count = int.from_bytes(header[bytes_sequence_position : bytes_sequence_position + HEADER_ANSWER_COUNT_LENGTH_IN_BYTES])
        bytes_sequence_position += HEADER_ANSWER_COUNT_LENGTH_IN_BYTES

        self.message.header.authority_record_count = int.from_bytes(header[bytes_sequence_position : bytes_sequence_position + HEADER_AUTHORITY_COUNT_LENGTH_IN_BYTES])
        bytes_sequence_position += HEADER_AUTHORITY_COUNT_LENGTH_IN_BYTES

        self.message.header.additional_record_count = int.from_bytes(header[bytes_sequence_position : bytes_sequence_position + HEADER_ADDITIONAL_COUNT_LENGTH_IN_BYTES])

    def parse_question(self, starting_point_in_bytes: int):
        pointer, domain_name_slices = starting_point_in_bytes, []

        while True:
            current_label_byte = self.__raw_message[pointer : pointer + 1]
            
            # This null byte as the label length indicates that the current label sequence ends
            if current_label_byte == b'\x00':
                pointer += 1
                break

            label_length_as_bits = format(int.from_bytes(current_label_byte), '08b')
        
            # This means this is not a regular label sequence, but a pointer to a label that has appeared before in the message (instead of reapeating the domain name
            # we point to a previous occurrence)
            if label_length_as_bits[0:2] == '11':
                offset  = format(int.from_bytes(self.__raw_message[pointer : pointer + 2]), '016b')
                # We remove the MSB of the two bytes that conform the pointer, these are just flags, not actually part of the pointer
                offset = '00' + offset[2:]
                question, _ = self.parse_question(int(offset, base=2))
                pointer_after_offset = pointer + 2

                # At this point we found a pointer to a compressed label sequence (the pointer to a label sequence that has appeared already), we've parsed it
                # but we still need to append at the beginning all the labels we found for the current question before we found the compression pointer,
                # we could have something like {{ REGULAR_LABEL }}.{{ COMPRESSION_POINTER }}
                question.domain_name = '.'.join(domain_name_slices) + '.' + question.domain_name

                return (question, pointer_after_offset)
            
            else:
                # This means this is still a regular label sequence, move the pointer past the current label length byte
                pointer += 1
                # The the next label length (in bytes) from the variable that still contains the next label length (the pointer was moved already but this
                # variable still has the value)
                label_size = int.from_bytes(current_label_byte)
                # Get the next label in the sequence and append it to the domain name slices
                label = self.__raw_message[pointer : pointer + label_size].decode('UTF-8')
                pointer += label_size
                domain_name_slices.append(label)

        domain_name = '.'.join(domain_name_slices)
        record_type = int.from_bytes(self.__raw_message[pointer : pointer + 2])
        pointer += 2
        question_class = int.from_bytes(self.__raw_message[pointer : pointer + 2])
        pointer += 2

        return (DNSQuestion(domain_name, record_type, question_class), pointer)
    
    def parse_questions(self, question_count: int):
        pointer = HEADER_LENGTH_IN_BYTES

        while question_count > 0:
            question, pointer = self.parse_question(pointer)
            self.message.questions.append(question)
            question_count -= 1

        return pointer
    
    def parse_answer_record(self, starting_point_in_bytes: int):
        pointer, domain_name_slices = starting_point_in_bytes, []

        while True:
            current_label_byte = self.__raw_message[pointer : pointer + 1]

            # This null byte as the label length indicates that the current label sequence ends
            if current_label_byte == b'\x00':
                pointer += 1
                break

            label_length_as_bits = format(int.from_bytes(current_label_byte), '08b')

            # This means this is not a regular label sequence, but a pointer to a label that has appeared before in the message (instead of reapeating the domain name
            # we point to a previous occurrence)
            if label_length_as_bits[0:2] == '11':
                offset  = format(int.from_bytes(self.__raw_message[pointer : pointer + 2]), '016b')
                # We remove the MSB of the two bytes that conform the pointer, these are just flags, not actually part of the pointer
                offset = '00' + offset[2:]
                answer, _ = self.parse_answer_record(int(offset, base=2))
                pointer_after_offset = pointer + 2

                # At this pointe we found a pointer to a compressed label sequence (the pointer to a label sequence that has appeared already), we've parsed it
                # but we still need to append at the beginning all the labels we found for the current question before we found the compression pointer,
                # we could have something like {{ REGULAR_LABEL }}.{{ COMPRESSION_POINTER }}
                answer.preamble.domain_name = '.'.join(domain_name_slices) + '.' + answer.domain_name

                return (answer, pointer_after_offset)

            else:
                # This means this is still a regular label sequence, move the pointer past the current label length byte
                pointer += 1
                # The the next label length (in bytes) from the variable that still contains the next label length (the pointer was moved already but this
                # variable still has the value)
                label_size = int.from_bytes(current_label_byte)
                # Get the next label in the sequence and append it to the domain name slices
                label = self.__raw_message[pointer : pointer + label_size].decode('UTF-8')
                pointer += label_size
                domain_name_slices.append(label)

            
        domain_name = '.'.join(domain_name_slices)
        record_type = int.from_bytes(self.__raw_message[pointer : pointer + 2])
        pointer += 2
        record_class = int.from_bytes(self.__raw_message[pointer : pointer + 2])
        pointer += 2
        time_to_live = int.from_bytes(self.__raw_message[pointer : pointer + 4])
        pointer += 4
        data_length = int.from_bytes(self.__raw_message[pointer : pointer + 2])
        pointer += 2

        ip_numbers = []
        for i in range(4):
            next_ip_number = int.from_bytes(self.__raw_message[pointer : pointer + 1])
            ip_numbers.append(str(next_ip_number))

            pointer += 1

        ip_address = '.'.join(ip_numbers)


        return (DNSRecord(DNSRecordPreamble(domain_name, record_type, record_class, time_to_live, data_length), ip_address), pointer)
    
    def parse_answer_records(self, starting_point_in_bytes: int, answer_count: int):
        pointer = starting_point_in_bytes

        while answer_count:
            answer, pointer = self.parse_answer_record(pointer)
            self.message.answers.append(answer)
            answer_count -= 1


