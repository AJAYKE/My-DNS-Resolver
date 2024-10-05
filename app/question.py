class DNSQuestion:
    def __init__(self, domain_name, record_type, question_class):
        self.domain_name: str = domain_name
        self.record_type: int = record_type
        self.question_class: int = question_class

    def __str__(self):
        return f'Question -> Domain name: {self.domain_name}. Record Type: {self.record_type}. Question class: {self.question_class}'
        
