#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Appointment, SMSMessage
from .forms import SMSForm, LoginForm
from doctix.numbers import (normalized_phonenumber)


@login_required()
def smssender(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SMSForm(request.POST)
        # check whether it's valid:
        print(form)
        if form.is_valid():
            identities = form.get_number('identities')
            message = request.POST.get('text')
            for ident in identities:
                phone_number = normalized_phonenumber(ident)
                msg, created = SMSMessage.objects.get_or_create(
                    direction=SMSMessage.OUTGOING,
                    identity=ident,
                    # event_on=received_on,
                    text=message,
                    defaults={'created_on': timezone.now()})
            return HttpResponseRedirect('/sms-sender/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SMSForm()

    return render(request, 'sendsms.html', {'form': form})

def index(request):
    latest_question_list = Appointment.objects.order_by('-date')[:5]
    context = {}
    context.update({
        'latest_question_list':latest_question_list})
    return render(request, 'index.html', context)
