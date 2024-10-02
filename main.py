import socket

from answer import DNSAnswer
from header import DNSHeader
from question import DNSQuestion


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
    
            dns_header = DNSHeader(packet_identifier=1234, query_response=1, question_count=1)
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
