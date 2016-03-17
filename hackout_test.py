import unittest

from hackout import Email


class FakeEmailClient(object):
    def __init__(self):
        self.labels = []
        self.emails = []
        self.labelling = []

    def create_label(self, name):
        if name not in self.labels:
            self.labels.append(name)
            return len(self.labels) - 1
        else:
            return self.labels.index(name)

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
        if not (0 <= label_id < len(self.labels)):
            raise RuntimeError("unknown label ID %r" % label_id)
        self.labelling[message_id].append(label_id)


class FakeEmailClientTest(unittest.TestCase):
    EMAIL = Email(from_='sender@example.com', to='recipient@example.com',
                  subject='Hello, World!', content='PS This is a test.')

    def setUp(self):
        self.client = FakeEmailClient()

    def test_labels_are_created_once(self):
        self.assertEqual(0, self.client.create_label('Campaign'))
        self.assertEqual(0, self.client.create_label('Campaign'))

    def test_emails_are_sent(self):
        self.assertEqual(0, self.client.send_email(self.EMAIL))
        self.assertEqual([self.EMAIL], self.client.emails)

    def test_label_can_be_added(self):
        label_id = self.client.create_label('Campaign')
        message_id = self.client.send_email(self.EMAIL)
        self.client.add_label(message_id, label_id)

        self.assertTrue(self.client.has_sent(self.EMAIL.to, label_id))

    def test_can_add_only_existent_label(self):
        message_id = self.client.send_email(self.EMAIL)

        with self.assertRaises(RuntimeError):
            self.client.add_label(message_id, 0)

    def test_has_sent(self):
        label_id = self.client.create_label('Campaign')

        self.assertFalse(self.client.has_sent(self.EMAIL.to, label_id))

        message_id = self.client.send_email(self.EMAIL)

        self.assertFalse(self.client.has_sent(self.EMAIL.to, label_id))

        self.client.add_label(message_id, label_id)

        self.assertTrue(self.client.has_sent(self.EMAIL.to, label_id))


if __name__ == '__main__':
    unittest.main()
