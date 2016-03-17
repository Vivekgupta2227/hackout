import unittest

from hackout import CampaignEmail, CampaignSender, Email
from test_support import FakeEmailClient, EMAIL1, EMAIL2, EMAIL3


class CampaignSenderTest(unittest.TestCase):
    CAMPAIGN_EMAIL1 = CampaignEmail(campaign='Test Campaign', email=EMAIL1)
    CAMPAIGN_EMAIL2 = CampaignEmail(campaign='Test Campaign', email=EMAIL2)
    CAMPAIGN_EMAIL3 = CampaignEmail(campaign='Test Campaign', email=EMAIL3)

    ANOTHER_CAMPAIGN_EMAIL1 = CampaignEmail(campaign='Another Campaign',
                                            email=EMAIL1)

    def setUp(self):
        self.client = FakeEmailClient()
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


if __name__ == '__main__':
    unittest.main()
