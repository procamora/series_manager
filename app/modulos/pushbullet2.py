#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pushbullet import Pushbullet

from app import logger


# https://github.com/randomchars/pushbullet.py


class PB2:
    def __init__(self, api):
        self.pb = Pushbullet(api)

    def send_text_pb(self, titulo, texto):
        self.pb.push_note(titulo, texto)

    def send_link_pb(self, titulo, link):
        self.pb.push_link(titulo, link)

    def send_file_pb(self, fichOriginal, fichFinal=None):
        """
        Envia un fichero, primero lo sube y despues lo envia, si solo se le da el nombre del fichero a la funcion lo
         envia con ese nombre si se le dan 2 nombres lo envia con el nombre del segundo
        """
        if fichFinal is None:
            fichFinal = fichOriginal
        with open(fichOriginal, "rb") as pic:
            file_data = self.pb.upload_file(pic, fichFinal)

        self.pb.push_file(**file_data)

    def show_all(self):
        for i in self.pb.devices:
            logger.info(i)

    def send_first_device(self):
        motog = self.pb.devices[0]
        motog.push_note("Hello world!", "We're using the api.")
