# My-DNS-Resolver

(TO UNDERSTAND DNS BETTER)[https://github.com/EmilHernvall/dnsguide/blob/b52da3b32b27c81e5c6729ac14fe01fef8b1b593/chapter1.md]

All communications in the DNS protocol are carried in a single format called a "message".

This Entire message must be 512 bytes or less.

Each message consists of 5 sections:

1. header - 12 bytes fixed
2. question
3. answer
4. authority
5. an additional space.

## Header

Its 12 byte long with multiple data points inside it.

1. packet_identifier
2. query_response
3. operation_code
4. authoritative_answer
5. truncation
6. recursion_desired
7. recursion_available
8. reserved
9. response_code
10. question_count
11. answer_record_count
12. authority_record_count
13. additional_record_count

This is the order of contents in header.

packet_identifier, question_count, answer_record_count, authority_record_count, additional_record_count are 16bit parts
and remaining 2-9 are together make another 16bit long message.

To reduce the number of variables and align with how dns works, we pack these 2-9 parts into a single 16-bit section in the header.

## Question

The question section contains a list of questions (usually just 1) that the sender wants to ask the receiver. This section is present in both query and reply packets.

Each question has the following structure:

Name: A domain name, represented as a sequence of "labels"
Type: 2-byte int; the type of record
Class: 2-byte int; usually set to 1

## Answer

The answer section contains a list of RRs (Resource Records), which are answers to the questions asked in the question section.
Each RR has the following structure:

1. Name ------------------ Label ------------ Sequence The domain name encoded as a sequence of labels.
2. Type ------------------ 2-byte Integer --- 1 for an A record, 5 for a CNAME record etc., full list here
3. Class ----------------- 2-byte Integer --- Usually set to 1 (full list here)
4. TTL (Time-To-Live) ---- 4-byte Integer --- The duration in seconds a record can be cached before requerying.
5. Length (RDLENGTH) ----- 2-byte Integer --- Length of the RDATA field in bytes.
6. Data (RDATA) ---------- Variable --------- Data specific to the record type.
