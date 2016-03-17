import base64
from email.mime.text import MIMEText


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
