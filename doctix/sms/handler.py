#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django.utils import timezone
from doctix.models import Appointment, Doctor
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
    print("message", message)
    try:
        kw, args = message.content.split(" ", 1)
        post_id = args.split(" ", 1)[0]
        resp = args.split(" ", 1)[1]
    except Exception as e:
        message.respond("Format SMS Invaide.")
        return True
    try:
        doc = Doctor.objects.get(phone=message.identity)
    except Exception as e:
        print(e)
    try:
        print("Get Appointment")
        appoint = Appointment.objects.get(post_id=post_id)
        if appoint.phone == "":
            return False
        resp_ = appoint.format_doct_answer_sms(resp)
        print("Reponse ", resp_)
        if not resp_:
            message.respond(
                "Reponse incorrecte. Contactez l'assistance doctix.")
            return True
        args = resp_
        message.identity = appoint.phone
    except Exception as e:
        print(e)
        args = "{p_id} n existe pas".format(p_id=post_id)
    message.respond(args)
    return True


def doctix_sms_handler(message):
    '''
    format SMS
        d
    '''
    # if message.content.startswith('d '):
    #     message.text = message.content[0:]
    # message.save()

    logger.debug("Incoming SMS from {}: {}".format(
        message.identity, message.content))

    keywords = {'test': test,
                'echo': echo,
                'd': response_appoint}

    for keyword, handler in keywords.items():
        if message.content.lower().startswith(keyword):
            print("keyword")
            return handler(message)
    # message.respond("Message non pris en charge.")
    return False
