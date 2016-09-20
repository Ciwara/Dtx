#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django.utils import timezone
from doctix.models import Appointment
# from snisi_sms.common import test, echo, change_passwd, ask_for_help

logger = logging.getLogger(__name__)


def test(message):
    msg = "Received on {date}"
    try:
        _, content = message.content.split()
        msg += ": {content}"
    except:
        content = None

    message.respond(msg.format(date=timezone.now(), content=content))
    return True


def echo(message):
    try:
        kw, args = message.content.split(" ", 1)
    except:
        args = "-"
    message.respond(args)
    return True


def response_appoint(message):
    try:
        kw, args = message.content.split(" ", 1)
        post_id = args.split(" ", 1)[0]
        resp = args.split(" ", 1)[1]
    except Exception as e:
        args = "Format SMS Invaide."
        message.respond(args)
        return True
    try:
        doc = Doctor.objects.get(phone=message.identity)
    except:
        pass
    try:
        appoint = Appointment.objects.get(post_id=post_id)
        message.identity = appoint.phone
        if "ok" in resp.lower() or "yes" in resp.lower():
            args = "{doc} a valider votre rendez-vous pour {date_time}".format(
                doc=appoint.doctor.full_name, date_time=appoint.appointmentdatetime)
        elif "no" in resp.lower() or "non" in resp.lower():
            args = "{doc} n est pas disponible pour {date_time}".format(
                doc=appoint.doctor.full_name, date_time=appoint.appointmentdatetime)
    except Exception as e:
        print(e)
        args = "{p_id} est n existe pas".format(p_id=post_id)
    message.respond(args)
    return True


def doctix_sms_handler(message):

    # migration to non-snisi prefixed SMS
    if message.content.startswith('d '):
        message.text = message.content[0:]
        message.save()

    logger.debug("Incoming SMS from {}: {}".format(
        message.identity, message.content))

    keywords = {'test': test,
                'echo': echo,
                'd': response_appoint}

    for keyword, handler in keywords.items():
        if message.content.lower().startswith(keyword):
            return handler(message)
            print("keyword")
    # message.respond("Message non pris en charge.")
    return False
