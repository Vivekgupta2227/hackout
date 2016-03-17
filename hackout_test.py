import unittest

from hackout import CampaignEmail, CampaignSender, Email


EMAIL1 = Email(from_='sender@example.com', to='recipient@example.com',
               subject='Hello, World!', content='PS This is a test.')
EMAIL2 = Email(from_='other.sender@example.com', to='recipient@example.com',
               subject='Hey, There!', content='Another test.')
EMAIL3 = Email(from_='sender@example.com', to='other.recipient@example.com',
               subject='Hey, There!', content='Another test.')

class CampaignSenderTest(unittest.TestCase):
    CAMPAIGN_EMAIL1 = CampaignEmail(campaign='Test Campaign', email=EMAIL1)
    CAMPAIGN_EMAIL2 = CampaignEmail(campaign='Test Campaign', email=EMAIL2)
    CAMPAIGN_EMAIL3 = CampaignEmail(campaign='Test Campaign', email=EMAIL3)

    ANOTHER_CAMPAIGN_EMAIL1 = CampaignEmail(campaign='Another Campaign',
                                            email=EMAIL1)

    def setUp(self):
        self.client = FakeEmailClient();
        self.sender = CampaignSender(self.client)

    def test_send_one_email(self):
        self.sender.send([self.CAMPAIGN_EMAIL1])

        self.assertIn('Outreach', self.client.labels)
        self.assertIn('Outreach/Test Campaign', self.client.labels)
        self.assertEqual(1, len(self.client.emails))
        self.assertEqual(['Outreach/Test Campaign'], self.client.labelling[0])

    def test_send_at_most_once(self):
        self.sender.send([self.CAMPAIGN_EMAIL1])
        self.sender.send([self.CAMPAIGN_EMAIL2])

        self.assertEqual(1, len(self.client.emails))

    def test_send_many_emails(self):
        self.sender.send([self.CAMPAIGN_EMAIL1, self.CAMPAIGN_EMAIL3,
                          self.ANOTHER_CAMPAIGN_EMAIL1])

        self.assertEqual(3, len(self.client.emails))


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


class FakeEmailClientTest(unittest.TestCase):
    def setUp(self):
        self.client = FakeEmailClient()

    def test_labels_are_created_once(self):
        self.assertEqual('Campaign', self.client.create_label('Campaign'))
        self.assertEqual('Campaign', self.client.create_label('Campaign'))
        self.assertEqual(1, len(self.client.labels))

    def test_emails_are_sent(self):
        self.assertEqual(0, self.client.send_email(EMAIL1))
        self.assertEqual([EMAIL1], self.client.emails)

    def test_label_can_be_added(self):
        label_id = self.client.create_label('Campaign')
        message_id = self.client.send_email(EMAIL1)
        self.client.add_label(message_id, label_id)

        self.assertTrue(self.client.has_sent(EMAIL1.to, label_id))

    def test_can_add_only_existent_label(self):
        message_id = self.client.send_email(EMAIL1)

        with self.assertRaises(RuntimeError):
            self.client.add_label(message_id, 0)

    def test_has_sent(self):
        label_id = self.client.create_label('Campaign')

        self.assertFalse(self.client.has_sent(EMAIL1.to, label_id))

        message_id = self.client.send_email(EMAIL1)

        self.assertFalse(self.client.has_sent(EMAIL1.to, label_id))

        self.client.add_label(message_id, label_id)

        self.assertTrue(self.client.has_sent(EMAIL1.to, label_id))


if __name__ == '__main__':
    unittest.main()
