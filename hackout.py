#!/usr/bin/env python2.7
from __future__ import print_function

import argparse
import base64
from collections import namedtuple
from email.mime.text import MIMEText
import errno
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import yaml


def main():
    parser = argparse.ArgumentParser(
        description='Email outreach tool for hackers.'
    )
    subparsers = parser.add_subparsers(dest='command')

    parser_send = subparsers.add_parser(
        'send',
        description='Send an outreach campaign.'
    )
    parser_send.add_argument('campaign_file')

    parser_authn = subparsers.add_parser(
        'authn',
        description='Authenticate in GMail',
        parents=[tools.argparser]
    )

    args = parser.parse_args()

    if args.command == 'authn':
        authn(args)
    elif args.command == 'send':
        send(args)
    else:
        raise(RuntimeError("unknown command {}".format(args.command)))


def authn(args):
    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    return credentials, http


def send(args):
    credentials, http = authn(args)
    service = discovery.build('gmail', 'v1', http=http)
    campaign = load_campaign_from_file(args.campaign_file)
    gmail_client = GMailClient(service)
    campaign_sender = CampaignSender(gmail_client)
    campaign_sender.send(campaign)


class CampaignSender(object):
    '''An outreach campaign sender.'''

    def __init__(self, email_client):
        self._email_client = email_client

    def send(self, campaign_emails):
        '''Send a list of CampaignEmails.'''
        log('Sending {} emails.', len(campaign_emails))

        self._email_client.create_label('Outreach')
        for campaign_email in campaign_emails:
            self._send_campaign_email(campaign_email)

        log('Done.')

    def _send_campaign_email(self, campaign_email):
        label_id = self._email_client.create_label(
            'Outreach/{}'.format(campaign_email.campaign)
        )
        already_sent = self._email_client.has_sent(campaign_email.email.to,
                                                   label_id)
        if already_sent:
            log('Campaign "{}" was already sent to {}; skipping',
                campaign_email.campaign,
                campaign_email.email.to)
        else:
            log('Sending "{}" to {}', campaign_email.campaign,
                campaign_email.email.to)
            message_id = self._email_client.send_email(campaign_email.email)
            self._email_client.add_label(message_id, label_id)


class GMailClient(object):
    '''A GMail client class.'''

    def __init__(self, service):
        self._service = service

    def create_label(self, name):
        '''Return the label ID. Create the label if it doesn't exist.'''
        labels = self._labels().list(userId='me').execute().get('labels', [])
        for label in labels:
            if label['name'] == name:
                return label['id']
        return self._labels().create(
            userId='me',
            body={'name': name}
        ).execute()['id']

    def has_sent(self, to, label_id):
        '''Return True if an email with the label was sent to the recipient.'''
        return bool(self._messages().list(
            userId='me',
            labelIds=[label_id],
            q='to:{}'.format(to)
        ).execute().get('messages', []))

    def send_email(self, email):
        '''Send the email and return its ID.'''
        return self._messages().send(
            userId='me',
            body=self.email_to_gmail_message(email)
        ).execute()['id']

    def add_label(self, message_id, label_id):
        '''Attach a label to a message.'''
        self._messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()

    def _labels(self):
        return self._service.users().labels()

    def _messages(self):
        return self._service.users().messages()

    @staticmethod
    def email_to_mime_text(email):
        '''Convert Email to MIMEText.'''
        mime_text = MIMEText(email.content)
        mime_text['from'] = email.from_
        mime_text['to'] = email.to
        mime_text['subject'] = email.subject
        return mime_text

    @staticmethod
    def mime_text_to_gmail_message(mime_text):
        '''Convert MIMEText to a GMail API message.'''
        return {'raw': base64.urlsafe_b64encode(mime_text.as_string())}

    @staticmethod
    def email_to_gmail_message(email):
        '''Convert Email to a GMail API message.'''
        return GMailClient.mime_text_to_gmail_message(
            GMailClient.email_to_mime_text(email)
        )


Template = namedtuple('Template', 'subject content')
Email = namedtuple('Email', 'from_ to subject content')
CampaignEmail = namedtuple('CampaignEmail', 'campaign email')


def load_campaign_from_file(path):
    with open(path, 'rt') as file_:
        data = yaml.load(file_)
        template = load_email_template(data['template'])
        return [
            CampaignEmail(
                campaign=data['name'],
                email=render_email_template(
                    template,
                    from_=data['from'],
                    **target
                )
            ) for target in data['targets']
        ]


def render_email_template(template, from_, to, **kwargs):
    '''Return an Email which is the result of rendering an Template.'''
    return Email(
        from_=from_,
        to=to,
        subject=template.subject.format(**kwargs),
        content=template.content.format(**kwargs)
    )


def load_email_template(path):
    '''Return an Template loaded from a file.'''
    with open(path, 'rt') as file_:
        subject = file_.readline().strip()
        content = file_.read()
    return Template(subject, content)


SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = "Hacker's Outreach"
DEFAULT_CREDENTIALS_PATH = '~/.credentials/outreach-credentials.json'


def get_credentials(args):
    credential_path = os.path.expanduser(DEFAULT_CREDENTIALS_PATH)
    mkdirp(os.path.dirname(credential_path))

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, args)
        log('Storing credentials to {}', credential_path)
    return credentials


def mkdirp(path):
    '''Create a directory including parent directors if they don't exist.'''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def log(message, *args, **kwargs):
    '''Log a message to stdout.'''
    print(message.format(*args, **kwargs))

if __name__ == '__main__':
    main()
