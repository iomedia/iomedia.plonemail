from iomedia.plonemail.plonemail import EmailBase
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging; logger=logging.getLogger('iomedia.plonemail.examples')

class SampleEmail(BrowserView,EmailBase):
    """ Simple browserview to send an email """
    test_email = ViewPageTemplateFile('emails/email.pt')

    def __call__(self):
        self.recipient = self.getRecipient()
        self.sender= self.getSender()
        if self.request.get('send-test-email'):
            logger.info('Sending test email to %s' % self.recipient['email'])
            self.subject='Test Email'
            self.message=self.test_email()
            self.send_email()
        return super(SampleEmail, self).__call__()

    def getSender(self):
        return {
            'firstname':'Firstname',
            'lastname':'Lastname',
            'email':'test@example.com'
        }

    def getRecipient(self):
        return {
            'firstname':'Firstname',
            'lastname':'Lastname',
            'email':'test@example.com'
        }
