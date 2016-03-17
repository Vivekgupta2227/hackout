import unittest

from test_support import FakeEmailClient, EMAIL1, EMAIL2, EMAIL3


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
