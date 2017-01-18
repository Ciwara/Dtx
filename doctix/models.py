#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from schedule.models import Calendar


@python_2_unicode_compatible  # only if you need to support Python 2
class Specialtie(models.Model):
    slug = models.CharField("Slug", max_length=200, primary_key=True)
    name = models.CharField("Name", max_length=200)
    description = models.CharField(
        "Name", max_length=200, null=True, blank=True)
    update_date = models.DateTimeField("Update date", default=timezone.now)

    def __str__(self):
        return "{} {}".format(self.name, self.description)

    @classmethod
    def get_or_none(cls, cid):
        try:
            return cls.objects.get(post_id=cid)
        except cls.DoesNotExist:
            return None


@python_2_unicode_compatible  # only if you need to support Python 2
class Department(models.Model):
    post_id = models.IntegerField(primary_key=True)
    slug = models.CharField("Slug", max_length=200)
    title = models.CharField("Title", max_length=250)
    date = models.DateTimeField()
    date_modified = models.DateTimeField('Date modified')
    update_date = models.DateTimeField("Update date", default=timezone.now)
    dept_shortinfo = models.CharField(
        "Short info", max_length=250, null=True, blank=True)
    guid = models.CharField("guid", max_length=250)

    def __str__(self):
        return "{title} {info}".format(title=self.title,
                                       info=self.dept_shortinfo)

    @classmethod
    def get_or_none(cls, cid):
        try:
            return cls.objects.get(post_id=cid)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_or_create(cls, data):
        app = cls.get_or_none(data.get('post_id'))
        if app is None:
            app = cls.objects.create(**data)
        else:
            app.objects.update(**data)
            app.save()
        return app


@python_2_unicode_compatible  # only if you need to support Python 2
class Doctor(models.Model):
    post_id = models.IntegerField(primary_key=True)
    slug = models.CharField("Slug", max_length=200)
    full_name = models.CharField("Nom", max_length=200)
    location = models.CharField("Location", max_length=200)
    phone = models.IntegerField("Phone Number(s)", null=True, blank=True)
    email = models.EmailField("E-mail", max_length=250, null=True, blank=True)
    clinic_hrs_desc = models.CharField("Desc Clinic Hours", max_length=200)
    sms_submit = models.BooleanField(default=False)
    date = models.DateTimeField('Date published')
    date_modified = models.DateTimeField('Date modified')
    sticky = models.BooleanField()
    link = models.CharField("Link", max_length=250)
    specialty = models.ForeignKey(Specialtie, verbose_name=_("Specailty"))
    calendar = models.ForeignKey(Calendar, verbose_name=_('Calendar'))

    @classmethod
    def get_or_none(cls, cid):
        try:
            return cls.objects.get(post_id=cid)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_or_create(cls, data):
        app = cls.get_or_none(data.get('post_id'))
        if app is None:
            app = cls.objects.create(**data)
        else:
            app.update(**data)
            app.save()
        return app

    def __str__(self):
        return "{full_name}/{phone}/{location}".format(full_name=full_name, location=location, phone=phone)


@python_2_unicode_compatible  # only if you need to support Python 2
class Appointment(models.Model):

    CONFIRMED = 'confirmed'
    UNCONFIRMED = 'unconfirmed'
    CANCELLED = 'cancelled'
    STATUS = {
        CONFIRMED: _("confirmed"),
        UNCONFIRMED: _("unconfirmed"),
        CANCELLED: _("cancelled")
    }
    FEMALE = 'Female'
    MALE = 'Male'
    GENDERS = {
        FEMALE: _("Femme"),
        MALE: _("Homme"),
    }

    post_id = models.IntegerField(primary_key=True)
    slug = models.CharField("Slug", max_length=200)
    date = models.DateTimeField('Date published')
    date_modified = models.DateTimeField(
        'Date modified', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, verbose_name=u'Doctor')
    appointmentdatetime = models.DateTimeField('Date appointment', null=True)
    department = models.ForeignKey(Department, verbose_name=u'Department')
    description = models.CharField(max_length=200)
    dob = models.DateField(max_length=200, null=True, blank=True)
    email = models.EmailField("E-mail", max_length=250, null=True, blank=True)
    lastname = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    gender = models.CharField(max_length=200, choices=GENDERS.items())
    phone = models.CharField(max_length=200)
    status = models.CharField(max_length=200, choices=STATUS.items())
    update_date = models.DateTimeField('Date update', default=timezone.now)
    guid = models.CharField(max_length=200)

    @property
    def full_name(self):
        return "{first} {last}".format(first=self.firstname, last=self.lastname)

    def __str__(self):
        return "{} {} {} {}".format(self.full_name, self.email,
                                    self.status, self.phone)

    # @property
    def format_notiv_doct_sms(self):
        text = "Patient {full_name} {gender} {age} Motif {des}".format(
            full_name=self.full_name, gender=self.get_gender(), age=self.get_age(), des=self.description)
        if len(text) == 120:
            text = text[:117] + "..."
        return text + " Demande RDV {id} pour le {datetime}".format(id=self.post_id,
                                                                    datetime=self.appointmentdatetime.strftime("%d %b %Y a %Hh %Mm"))

    def get_gender(self):
        if self.gender == "Male":
            return "sexe M"
        elif self.gender == "Female":
            return "sexe F"
        else:
            return ""

    def get_age(self):
        from datetime import date
        if not self.dob:
            return ""
        today = date.today()
        year = today.year - self.dob.year - ((today.month, today.day)
                                             < (self.dob.month, self.dob.day))
        if year > 1:
            p = "ans" if year > 1 else "an"
        else:
            p = ""
        return "{}{}".format(year, p)

    def format_doct_answer_sms(self, resp):
        ok_list = ["ok", "yes", "accord", "oui"]
        decline_list = ["no", "non", "pas dispo", "absent", "occupé"]
        if len([p for p in ok_list if p in resp.lower()]) > 0:
            text = "{} a confirmé votre RDV pour le {}. "
        elif len([p for p in decline_list if p in resp.lower()]) > 0:
            text = "{} n'est disponible pour le {} merci. "
        else:
            return None
        text = text.format(self.doctor.full_name,
                           self.appointmentdatetime.strftime("%d %b %Y a %Hh %Mm"))
        return text + "Prompt rétablissement."

    @classmethod
    def get_or_create(cls, data):
        app = cls.get_or_none(data.get('post_id'))
        if app is None:
            app = cls.objects.create(**data)
        else:
            app.update(**data)
            app.save()
        return app

    @classmethod
    def get_or_none(cls, cid):
        try:
            return cls.objects.get(post_id=cid)
        except cls.DoesNotExist:
            return None


@python_2_unicode_compatible  # only if you need to support Python 2
class SMSMessage(models.Model):

    class Meta:
        app_label = 'doctix'
        verbose_name = _("SMS Message")
        verbose_name_plural = _("SMS Messages")

    INCOMING = 'incoming'
    OUTGOING = 'outgoing'
    DIRECTIONS = {
        INCOMING: _("Incoming"),
        OUTGOING: _("Outgoing")
    }

    SUCCESS = 'success'
    FAILURE = 'failure'
    BUFFERED = 'buffered'
    SMSC_SUBMIT = 'smsc_submit'
    SMSC_REJECT = 'smsc_reject'
    SMSC_NOTIFS = 'smsc_notifications'
    UNKNOWN = 'unknown'

    DELIVERY_STATUSES = {
        UNKNOWN: "Unknown",
        SUCCESS: "Delivery Success",
        FAILURE: "Delivery Failure",
        BUFFERED: "Message Buffered",
        SMSC_SUBMIT: "SMSC Submit",
        SMSC_REJECT: "SMSC Reject",
        SMSC_NOTIFS: "SMSC Intermediate Notifications",
    }

    direction = models.CharField(max_length=75,
                                 choices=DIRECTIONS.items())
    identity = models.CharField(max_length=100)
    created_on = models.DateTimeField(default=timezone.now)
    event_on = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    handled = models.BooleanField(default=False)
    # minutes of validity
    validity = models.PositiveIntegerField(blank=True, null=True)
    # minutes after creation time to send the SMS at
    deferred = models.PositiveIntegerField(blank=True, null=True)
    # DLR statuses
    delivery_status = models.CharField(max_length=75, default=UNKNOWN,
                                       choices=DELIVERY_STATUSES.items())

    def str(self):
        return self.text

    @property
    def message(self):
        return self.text

    @property
    def content(self):
        return self.message

    def respond(self, text):
        SMSMessage.objects.create(
            direction=self.OUTGOING,
            identity=self.identity,
            event_on=timezone.now(),
            text=text)


@python_2_unicode_compatible  # only if you need to support Python 2
class PersonalClinicHour(models.Model):
    DAY_NAMES = (
        ('M', _('Monday')),
        ('T', _('Tuesday')),
        ('W', _('Wednesday')),
        ('H', _('Thursday')),
        ('F', _('Friday')),
        ('S', _('Saturday')),
        ('U', _('Sunday')),
    )
    doctor = models.ForeignKey(Doctor, verbose_name=_("Doctor"))
    day_name = models.CharField(max_length=1, choices=DAY_NAMES)
    open_hr = models.TimeField()
    close_hr = models.TimeField()

    def __str__(self):
        return "{doc} {day_name} {open_hr} {close_hr}".format(
            doc=self.doctor, day_name=self.day_name, open_hr=self.open_hr, close_hr=self.close_hr)
