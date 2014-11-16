from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_quopri
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface

import html2text

import logging; logger=logging.getLogger('iomedia.plonemail')

class EmailBase():

    def send_email(self):
        transforms = getToolByName(self.context,'portal_transforms')
        msg = MIMEMultipart('alternative')

        transformer = html2text.HTML2Text()
        transformer.ignore_images = True

        textval = transformer.handle(self.message)
        text = MIMEText(textval,'plain','utf-8')

        html = MIMEText(self.message,'html','utf-8')
        msg.attach(text)
        msg.attach(html)
        msg_from = ' '.join([
            self.sender['firstname'],
            self.sender['lastname']
        ])
        msg.add_header('From','"%s" <%s>' % (msg_from,self.sender['email']))
        msg_to = ' '.join([
            self.recipient['firstname'],
            self.recipient['lastname']
        ])
        msg.add_header('To','"%s" <%s>' % (msg_to,self.recipient['email']))
        msg.add_header('Subject',self.subject)
        version = (
            api.portal.get().portal_quickinstaller
            .getProductVersion('iomedia.plonemail')
        )
        msg.add_header('User-Agent','iomedia.plonemail/%s' % str(version))
        host = getToolByName(self.context, 'MailHost')
        try:
            host.send(msg,immediate=True)
        except Exception as error:
            logger.error('Email could not be sent: %s' % error)

    def admin_property(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        pprops = getToolByName(self.context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        admin_name=(
            site_props.getProperty('email_from_name')
            or
            portal.getProperty('email_from_name')
        )
        admin_addr=(
            site_props.getProperty('email_from_address')
            or
            portal.getProperty('email_from_address')
        )
        return {
            'firstname': admin_name,
            'lastname' : '',
            'email'    : admin_addr
        }

    def site_name(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        pprops = getToolByName(self.context, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        site_name = (
            site_props.getProperty('email_from_name')
            or
            portal.getProperty('email_from_name')
        )
        return site_name
