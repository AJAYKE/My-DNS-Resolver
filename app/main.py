import argparse
import socket

from app.answer import DNSRecord, DNSRecordPreamble
from app.encoder import DNSMessageEncoder
from app.message import DNSMessage
from app.parser import DNSMessageParser


def handle_dns_query(server_udp_socket, buffer: bytes, source, resolver):
    try:
        parser = DNSMessageParser(buffer)
        message = parser.message

        # Set up the response message properties
        message.header.query_or_response_indicator = 1
        message.header.authoritative_answer = 0
        message.header.truncation = 0
        message.header.recursion_available = 0
        message.header.reserved = 0
        message.header.response_code = 0 if not message.header.operation_code else 4

        response: bytes = None

        # If a resolver address argument has been provided, we need to forward the questions received in the query message
        # to a different resolver server
        if resolver:
            resolver_ip, resolver_port = resolver.split(':', 1)
            resolver_address = (resolver_ip, int(resolver_port))

            response = forward_query(resolver_address, message)
        
        # If we don't get the address of a resolver server to forward the query, we can return a mock record value as the 
        # answer to each question in the query
        else:
            for question in message.questions:
                message.add_message_answer(DNSRecord(DNSRecordPreamble(question.domain_name, 1, 1, 60, 4), '8.8.8.8'))

            response = DNSMessageEncoder.encode_message(message)

        server_udp_socket.sendto(response, source)

    except Exception as e:
        print(f"Error handling DNS query: {e}")

def forward_query(resolver_address, message) -> bytes:
    try:
        # The socket object is a context manager, upon calling the 'with' statement, the __enter__ method
        # of the socket object will be called, and after exiting the scope of the with block, the __exit__
        # method of the socket object will be called to close the socket, ensuring the correct disposal
        # of the resources related to the socket object when this object is not needed anymore
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as resolver_socket:
            # The forward server only allows a single question in the query per UDP message,
            # split every question in the original message into its own forward message
            forward_query_counter = 1
            for question in message.questions:
                forward_query_message = DNSMessage(forward_query_counter)
                forward_query_message.add_message_question(question)

                resolver_socket.sendto(DNSMessageEncoder.encode_message(forward_query_message), resolver_address)
                raw_forward_response, _ = resolver_socket.recvfrom(512)

                forward_response_parser = DNSMessageParser(raw_forward_response)

                # The forward server should only reply with an answer record per query message sent
                if forward_response_parser.message.header.answer_record_count == 1:
                    message.add_message_answer(forward_response_parser.message.answers[0])
                else:
                    # Set error response code. RCODE:2 -> SERVFAIL (Server failed to complete the DNS request)
                    message.header.response_code = 2
                    break
                
                forward_query_counter += 1

        return DNSMessageEncoder.encode_message(message)

    except Exception as e:
        print(f"Error forwarding DNS query: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resolver')
    args = parser.parse_args()

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("127.0.0.1", 2053))
    
    while True:
        try:
            # Receive an UDP packet (up to 512 bytes) from any source (UDP doesn't require a handshake/session between the two parties)
            buf, source = udp_socket.recvfrom(512)
            handle_dns_query(udp_socket, buf, source, args.resolver)
        except Exception as e:
            print(f"Error handling DNS query: {e}")
if __name__ == "__main__":
    main()
    