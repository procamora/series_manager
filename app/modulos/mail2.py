#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mailer


# http://stackoverflow.com/questions/10147455/trying-to-send-email-gmail-as-mail-provider-using-python


class ML2:

    def __init__(self, user, passwd):
        self.message = mailer.Message()
        self.message.From = 'notificaciones <%s>' % user
        self.message.Subject = 'Notificacion Serie'
        # self.message.charset = 'utf-8'

        self.mail = mailer.Mailer("smtp.gmail.com")
        self.mail.use_tls = True  # sin esto no se establece la conexion
        self.mail.login(user, passwd)

    def send_mail(self, remitente, texto):
        self.message.To = remitente
        self.message.Html = texto
        # self.message.Html = open('letter.txt', 'rb').read()
        self.mail.send(self.message)

    def send_mail_adjunto(self, remitente, texto, adjuntos=''):
        self.message.To = remitente
        self.message.Html = texto
        # self.message.Html = open('letter.txt', 'rb').read()
        if len(adjuntos) != 0:
            self.message.attach(adjuntos)

        self.mail.send(self.message)
