from typing import List, Optional, Union, Any
from email.message import EmailMessage, Message
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass
import datetime
import logging
import sys

LOG_FILE = 'generatemail.log'
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = logging.getLogger('logger')
logger.setLevel(LOGGING_LEVEL)

@dataclass
class Participant:
    email: str
    name: Optional[str]
    def __str__(self) -> str:
        return f'{self.email} "{self.name}"' if self.name else self.email

class StandardReplyGenerator:
    def make_reply(self, msg: EmailMessage, prior_msg: EmailMessage) -> EmailMessage:
        def walk(component):
            for part in component.iter_parts():
                if part.get_content_disposition() != 'attachment':
                    if not self._make_reply_body(part, prior_msg):
                        walk(part)

        if not msg['subject']:
            prior_subject = prior_msg['subject']
            del msg['subject']
            msg.add_header('subject', prior_subject if prior_subject.lower().startswith("re:") else f'Re: {prior_msg["subject"]}' )

        walk(msg)        
        return msg

    def _make_reply_body(self, body, prior_msg):
        if body['content-type'].subtype == 'html':
            prior_body = prior_msg.get_body()
            prior_subtype = prior_body['content-type'].subtype
            from_hdr = f"<b>From:</b> {prior_msg['from']}<br>"
            to_hdr = f"<b>To:</b> {prior_msg['to']}<br>"
            cc_hdr = f"<b>Cc:</b> {prior_msg['cc']}<br>" if prior_msg['cc'] else ""
            bcc_hdr = f"<b>Cc:</b> {prior_msg['bcc']}<br>" if prior_msg['bcc'] else ""
            date_hdr = f"<b>Date:</b> {prior_msg['date']}<br>" if prior_msg['date'] else ""
            subject_hdr = f"<b>Subject:</b> {prior_msg['subject']}<br>"
            reply_header = f"""<p><div><div style="border:none;border-top:solid #E1E1E1 1.0pt;padding:3.0pt 0in 0in 0in"><p class="MsoNormal">{date_hdr}{from_hdr}{to_hdr}{cc_hdr}{bcc_hdr}{subject_hdr}</p></div></div>"""
            reply_body = f'<pre>{prior_body.get_content()}</pre>' if prior_subtype == 'plain' else self._strip_right_tag(self._strip_left_tag(prior_body.get_content(), 'body'), 'body')
            body_content = self._strip_right_tag(self._strip_left_tag(body.get_content(), 'html'), 'body')
            body.set_content(f'<html>{body_content}{reply_header}<p/>{reply_body}</body></html>', subtype='html')
            return True
        elif body['content-type'].subtype == 'plain':
            prior_body = prior_msg.get_body(preferencelist=('plain', 'html'))
            from_hdr = f"From: {prior_msg['from']}\n"
            to_hdr = f"To: {prior_msg['to']}\n"
            cc_hdr = f"Cc: {prior_msg['cc']}\n" if prior_msg['cc'] else ""
            bcc_hdr = f"Cc: {prior_msg['bcc']}\n" if prior_msg['bcc'] else ""
            date_hdr = f"Date: {prior_msg['date']}\n" if prior_msg['date'] else ""
            subject_hdr = f"Subject: {prior_msg['subject']}\n"
            reply_header = f'\n----------------------------------------\n{date_hdr}{from_hdr}{to_hdr}{cc_hdr}{bcc_hdr}{subject_hdr}'
            reply_body = prior_body.get_content()
            body.set_content(f'{body.get_content()}{reply_header}\n\n{reply_body}', subtype='plain')
            return True
        return False

    def _strip_left_tag(self, text, tag='html'):
        open_tag = f'<{tag}>'
        open_offset = text.find(open_tag)
        return text[open_offset+len(open_tag):] if open_offset >= 0 else text

    def _strip_right_tag(self, text, tag='html'):
        close_tag = f'</{tag}>'
        close_offset = text.find(close_tag)
        return text[:close_offset] if close_offset >= 0 else text

def write_message(message: EmailMessage, stream):
    from email import generator
    generator = generator.Generator(stream)
    generator.flatten(message)

def read_message(stream) -> EmailMessage:
    from email.policy import default
    import email
    return email.message_from_file(stream, policy=default)

def make_reply(msg: EmailMessage, prior_msg: EmailMessage) -> EmailMessage:
    return StandardReplyGenerator().make_reply(msg, prior_msg)

def create_message(
    sender: Union[Participant, str],
    subject: Optional[str] = None,
    text: Optional[str] = None,
    html: Optional[str] = None,
    date: datetime.datetime = None,
    recipients: List[Union[Participant, str]] = [],
    cc_recipients: List[Union[Participant, str]] = [],
    bcc_recipients: List[Union[Participant, str]] = [],
    attachments: Optional[str] = [],
    language: Optional[str] = 'en',
    charset: Optional[str] = 'utf-8'
):
    if not text and not html:
        raise Exception("At least one of text and html content needs to be provided")
    if not recipients and not cc_recipients and not bcc_recipients:
        raise Exception("At least one of recipients, cc_recipients, bcc_recipients needs to be provided")

    result = EmailMessage()
    result['From'] = str(sender)
    result['Subject'] = subject if subject else ''
    if recipients:
        result['To'] = ', '.join([str(x) for x in recipients])
    if cc_recipients:
        result['Cc'] = ', '.join([str(x) for x in cc_recipients])    
    if bcc_recipients:
        result['Bcc'] = ', '.join([str(x) for x in bcc_recipients])
    result['Date'] = (date if date else datetime.datetime.now()).strftime('%c %z')

    result.add_header('Language', language)
    result.add_header('Charset', charset)

    if text and html:
        result.make_alternative()
        result.add_alternative(text, subtype='plain')
        result.add_alternative(html, subtype='html')
    elif text:
        result.set_content(text)
        result.set_type('text/plain')
    elif html:
        result.set_content(html)
        result.set_type('text/html')
    
    # NEW ATTACHMENT STUFF
    if len(attachments) != 0:
        sepattachments = str(attachments).split(';')
        for a in sepattachments:
            try:
                with open(str(a), 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {f.name}')
                    #result.attach(part)
                    result.add_attachment(part, filename=f.name)
            except IOError:
                logger.error('File not accessible or readable')

    '''for name, content in attachments.items():
        result.add_attachment(content, filename=name)'''

    return result

def inspect(msg: Message, name='email'):
    from email.iterators import _structure
    print(f"################### STRUCTURE {name} ################")
    _structure(msg)
    print(f"################### CONTENT {name} ################")
    write_message(msg, sys.stdout)

def add_html_tokens(text):
    return ' '.join([x if i%2 == 0 else f'<em>{x}</em>' for i,x in enumerate(text.split())])

def html(text):
    return f'<html><head><meta></meta></head><body>{text}</body></html>'

def test():
    
    p1 = "test@test.com"
    p2 = Participant("test2@test.com", "Red Rover")
    p3 = Participant("test3@test.com", "Humpty Dumpty")
    text = "down with the kings for years, about ten of them."
    text2 = "it's gonna be a long time before I'm finished"
    text3 = "Hey you guys!!"
    text4 = 'this is a test :smile:'

    m1 = create_message(text=text, date=datetime.datetime.now()-datetime.timedelta(2), html=html(text), subject="hello", sender=p1, recipients=[p2,p1], cc_recipients=[p1])
    m2 = create_message(text=text2, html=html(text2), sender=p2, recipients=[p1,p3], attachments={'file2.txt': "message 2 attachment"})
    m3 = create_message(text=text3, html=html(text3), subject="hey!", sender=p3, bcc_recipients=[p1], recipients=[p2], attachments={'file3.txt': "message 3 attachment"})
    m4 = create_message(text=text4, html=html(text4), subject='test run', sender=p3, recipients=[p1])

    make_reply(m2, m1)
    # inspect(m2, 'm2')
    make_reply(m3, m2)
    inspect(m3, 'm3')
    inspect(m4, 'm4')

if __name__ == '__main__':
    test()