import common

logger = common.logger


class CampaignSender(object):
    '''An outreach campaign sender.'''

    def __init__(self, email_client):
        self._email_client = email_client

    def send(self, campaign_emails):
        '''Send a list of CampaignEmails.'''
        logger.info('Sending %i emails.', len(campaign_emails))

        self._email_client.create_label('Outreach')
        for campaign_email in campaign_emails:
            self._send_campaign_email(campaign_email)

        logger.info('Done.')

    def _send_campaign_email(self, campaign_email):
        label_id = self._email_client.create_label(
            'Outreach/{}'.format(campaign_email.campaign)
        )
        already_sent = self._email_client.has_sent(campaign_email.email.to,
                                                   label_id)
        if already_sent:
            logger.info('Campaign "%s" was already sent to %s; skipping',
                        campaign_email.campaign,
                        campaign_email.email.to)
        else:
            logger.info('Sending "%s" to %s', campaign_email.campaign,
                        campaign_email.email.to)
            message_id = self._email_client.send_email(campaign_email.email)
            self._email_client.add_label(message_id, label_id)
