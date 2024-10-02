import socket
import struct

from app.answer import DNSAnswer
from app.header import DNSHeader
from app.question import DNSQuestion


def parse_dns_header(data):
    header = struct.unpack('!HHHHHH',data[:12])
    packet_identifier = header[0]
    flags = header[1]
    operation_code = (flags >> 11 ) & 0xF #4 bits
    recursion_desired = (flags >> 8) & 1 # 1 bit
    question_count = header[2]

    return packet_identifier, operation_code, recursion_desired, question_count


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))
    
    while True:
        try:
            buf, source = udp_socket.recvfrom(512)

            packet_identifier, operation_code, recursion_desired, question_count = parse_dns_header(buf)

            dns_header = DNSHeader(packet_identifier=packet_identifier, operation_code=operation_code, recursion_desired=recursion_desired, query_response=1, question_count=question_count, answer_record_count=1)
            response_header = dns_header.build_header()

            dns_question = DNSQuestion(domain_name='codecrafters.io',record_type=1,record_class=1)
            response_question = dns_question.build_question()

            dns_answer = DNSAnswer(domain_name='codecrafters.io')
            response_answer = dns_answer.build_answer()

            response = response_header+response_question+response_answer
            udp_socket.sendto(response, source)

    
        except Exception as e:
            print(f"Error receiving data: {e}")
            break


if __name__ == "__main__":
    main()
