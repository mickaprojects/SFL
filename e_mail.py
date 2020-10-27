#!/usr/bin/env python
# -*- coding: utf8  -*-

from email.utils import COMMASPACE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email import Encoders

from datetime import date
import datetime

from email.MIMEText import MIMEText
import smtplib
import os
import sys
import psycopg2.extras
reload(sys)
sys.setdefaultencoding('utf8')

class CMail(object):
                       
    def __init__(self, sujet="",dateenv="", sbodymail=""):
        self.html = ""
#        self.tto = ["hasina@vivetic.mg"]
#        self.cc   = ["hasina@vivetic.mg", "hasina@vivetic.mg"]
        self.tto = ["hasina.cp@vivetic.mg"]
        self.cc   = ["haja@vivetic.mg", "infodev@vivetic.mg","alex@vivetic.mg","mamisoa@vivetic.mg"]
        self.sender = "infodev@vivetic.mg"
       
        self.sujet = sujet
        
        self.Email = None
        self.SmtpLink = None
        self.dateenvoi=dateenv
        self.sbodymail=sbodymail
        self.setUp()


    def setUp(self):
        self.Email = MIMEMultipart()
        self.Email['Date']           = datetime.datetime.strftime(self.dateenvoi, '%m/%d/%Y')+ ' '
        self.Email['From']           = self.sender
        self.Email['To']      = ', '.join(self.tto)
        self.Email['Cc']      = ', '.join(self.cc)
        
        self.SmtpLink = smtplib.SMTP("192.168.10.4")
        self.contentmail()

    def contentmail(self):
     
        
        html = ""
        html += """\
                <html>"""
        
        html += """\
     
        
        
        <BODY bgColor=#ffffff> 
        
        """
        
      
        html += """<DIV><FONT face=Arial size=2>&nbsp;</FONT></DIV>"""
        html += """<DIV><FONT face=Arial size=2>Bonjour,</FONT></DIV>"""
        html += """<DIV><FONT face=Arial size=2>&nbsp;</FONT></DIV>"""
        html += """<DIV><FONT face=Arial size=2>"""+self.sbodymail+""" </FONT></DIV>."""
       
        html += """<DIV><FONT face=Arial size=2>Cordialement</FONT></DIV>"""
        html += """<DIV><FONT face=Arial size=2></FONT>L'&eacute;quipe IAM</DIV>"""
       
        
        html += """\
        </body>
        </html>"""
        
        
        self.html = html.encode("utf8")
        

    def envoyer_mail(self):
        #try:
        self.Email.attach(MIMEText(self.html.encode('utf8','ignore'), 'html'))
        self.Email['Subject']        = self.sujet
        self.SmtpLink.sendmail(self.Email['From'], self.tto+self.cc, self.Email.as_string())
        self.SmtpLink.quit()
        return True
        #

##TODO UTILISATION
#commande= "TST001"
#nombre = "99"
#sujet =  "LIVRAISON TST001 - Test"
#serveur = "\\\\mctana\prod$"
#mail = CMail(commande,nombre,sujet,serveur)
#if mail.envoyer_mail():
#    print "ok"
#else:
#    print "ko"