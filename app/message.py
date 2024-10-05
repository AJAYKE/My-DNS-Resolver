from app.header import DNSMessageHeader


class DNSMessage:
    def __init__(self, packet_id: int = 0, query_response: int = 0):
        self.__header: DNSMessageHeader = DNSMessageHeader(packet_id, query_response)
        self.__questions = []
        self.__answers = []

    @property
    def header(self):
        return self.__header

    @property
    def questions(self):
        return self.__questions

    @property
    def answers(self):
        return self.__answers
    
    def add_message_question(self, dns_question):
        self.questions.append(dns_question)
        self.__header.question_count += 1

    def add_message_answer(self, dns_record):
        self.answers.append(dns_record)
        self.__header.answer_record_count += 1

    def reset_message_questions(self):
        self.__questions = []
        self.__header.question_count = 0

    def reset_message_answers(self):
        self.__answers = []
        self.__header.answer_record_count = 0
        
