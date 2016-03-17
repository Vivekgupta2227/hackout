from hackout import Email


EMAIL1 = Email(from_='sender@example.com', to='recipient@example.com',
               subject='Hello, World!', content='PS This is a test.')
EMAIL2 = Email(from_='other.sender@example.com', to='recipient@example.com',
               subject='Hey, There!', content='Another test.')
EMAIL3 = Email(from_='sender@example.com', to='other.recipient@example.com',
               subject='Hey, There!', content='Another test.')


class FakeEmailClient(object):
    def __init__(self):
        self.labels = []
        self.emails = []
        self.labelling = []

    def create_label(self, name):
        if name not in self.labels:
            self.labels.append(name)
        return name

    def has_sent(self, to, label_id):
        return any(
            email.to == to and label_id in labelling
            for (email, labelling) in zip(self.emails, self.labelling)
        )

    def send_email(self, email):
        self.emails.append(email)
        self.labelling.append([])
        return len(self.emails) - 1

    def add_label(self, message_id, label_id):
        if label_id not in self.labels:
            raise RuntimeError("unknown label ID %r" % label_id)
        self.labelling[message_id].append(label_id)
