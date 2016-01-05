import logging
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders

import html2text
from plone import api
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('iomedia.plonemail')


class EmailBase():

    attachments = []

    def send_email(self):

        # Build the outer message
        msg = MIMEMultipart('mixed')
        msg.preamble = 'This is a multi-part message in MIME format.'
        msg_from = ' '.join([self.sender['firstname'],
                             self.sender['lastname']])
        msg.add_header('From', '"%s" <%s>' % (msg_from, self.sender['email']))
        msg_to = ' '.join([self.recipient['firstname'],
                           self.recipient['lastname']])
        msg.add_header('To', '"%s" <%s>' % (msg_to, self.recipient['email']))
        msg.add_header('Subject', self.subject)
        version = (api.portal.get().portal_quickinstaller.getProductVersion(
            'iomedia.plonemail'))
        msg.add_header('User-Agent', 'iomedia.plonemail/%s' % str(version))

        # Create the message text part
        transformer = html2text.HTML2Text()
        transformer.ignore_images = True
        textval = transformer.handle(self.message)
        text = MIMEText(textval, 'plain', 'utf-8')
        html = MIMEText(self.message, 'html', 'utf-8')
        msg_text = MIMEMultipart('alternative')
        msg_text.attach(text)
        msg_text.attach(html)
        msg.attach(msg_text)

        # Add any attachmets to the message
        for attach in self.attachments:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(attach['data'])
            Encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                'inline; filename="%s"; size=%i' % (attach['filename'],
                                                    attach['size']))
            msg.attach(attachment)

        # Send the message
        host = getToolByName(self.context, 'MailHost')
        try:
            host.send(msg, immediate=True)
        except Exception as error:
            logger.error('Email could not be sent: %s' % error)

    def add_attachment(self, filename, data, size, ctype=None):
        """ Adds a file attachment to the email. """
        self.attachments.append({
            'filename': filename,
            'data': data,
            'size': size,
            'ctype': ctype})

    def admin_property(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        pprops = getToolByName(self.context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        admin_name = (
            site_props.getProperty('email_from_name')
            or
            portal.getProperty('email_from_name'))
        admin_addr = (
            site_props.getProperty('email_from_address')
            or portal.getProperty('email_from_address'))
        return {'firstname': admin_name,
                'lastname': '',
                'email': admin_addr}

    def site_name(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        pprops = getToolByName(self.context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        site_name = (
            site_props.getProperty('email_from_name')
            or
            portal.getProperty('email_from_name'))
        return site_name
