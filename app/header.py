class DNSMessageHeader:
    def __init__(self, packet_id: int = 0, query_response: int = 0):
        self.packet_id = packet_id
        self.query_or_response_indicator = query_response
        self.operation_code = 0
        self.authoritative_answer = 0
        self.truncation = 0
        self.recursion_desired = 0
        self.recursion_available = 0
        self.reserved = 0
        self.response_code = 0
        self.question_count = 0
        self.answer_record_count = 0
        self.authority_record_count = 0
        self.additional_record_count = 0
