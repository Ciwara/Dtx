#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin

from doctix.models import (SMSMessage, Appointment, Doctor, Department,
                           DoctorSpecialty, PersonalClinicHour, Specialtie)


class SMSMessageAdmin(admin.ModelAdmin):
    list_display = (
        'direction', 'identity', 'event_on', 'text', 'handled', 'delivery_status')
    list_filter = ('direction', 'event_on', 'handled')


class AppointmentAdmin(admin.ModelAdmin):

    """docstring for AppointmentAdmin"""
    list_display = ('post_id', 'status', 'doctor', 'gender', 'description',
                    'appointmentdatetime', 'date_modified', 'dob', 'phone', 'email')
    list_filter = ('status', 'doctor', 'date', 'email', 'phone')


class PersonalClinicHourInline(admin.TabularInline):
    model = PersonalClinicHour


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'slug', 'post_id', 'location', 'phone',
                    'date', 'email', )
    list_filter = ('date_modified', 'date', 'location', 'phone')
    inlines = [
        PersonalClinicHourInline,
        # AppointmentInline,
    ]


class SpecialtieAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'update_date',)
    list_filter = ('update_date',)


class DoctorSpecialtyAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'specialty', 'update_date',)
    list_filter = ('update_date',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'slug', 'title', 'date', 'date_modified',
                    'update_date', 'dept_shortinfo', 'guid')
    list_filter = ('date', 'date_modified', 'update_date')


class PersonalClinicHourAdmin(admin.ModelAdmin):

    list_display = ('doctor', 'day_name', 'open_hr', 'close_hr')
    list_filter = ('doctor', 'day_name', 'open_hr', 'close_hr')


admin.site.register(DoctorSpecialty, DoctorSpecialtyAdmin)
admin.site.register(Specialtie, SpecialtieAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(PersonalClinicHour, PersonalClinicHourAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)
