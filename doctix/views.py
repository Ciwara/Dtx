#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.shortcuts import render

from .models import Appointment


def index(request):
    latest_question_list = Appointment.objects.order_by('-date')[:5]
    context = {}
    return render(request, 'index.html', context)
