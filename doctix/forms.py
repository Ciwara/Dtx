#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class SMSForm(forms.Form):
    identities = forms.CharField(label='Destinateurs', max_length=100)
    text = forms.CharField(widget=forms.Textarea)

    def get_number(self, required):
        return self.cleaned_data.get('identities').split(",")

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
