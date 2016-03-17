#!/usr/bin/env python2.7
from __future__ import print_function

import argparse
from collections import namedtuple
import errno
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import yaml

from campaign import CampaignSender
import common
from gmail import GMailClient


logger = common.logger


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
                    to=target['to'],
                    **target['params']
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
        logger.info('Storing credentials to %s', credential_path)
    return credentials


def mkdirp(path):
    '''Create a directory including parent directors if they don't exist.'''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    main()
