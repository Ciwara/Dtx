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


@python_2_unicode_compatible  # only if you need to support Python 2
class Doctor(models.Model):
    post_id = models.IntegerField(primary_key=True)
    slug = models.CharField("Slug", max_length=200)
    full_name = models.CharField("Location", max_length=200)
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

    def __str__(self):
        return "{full_name} {specialty}".format(full_name=self.full_name,
                                                specialty=self.specialty)


@python_2_unicode_compatible  # only if you need to support Python 2
class Appointment(models.Model):
    post_id = models.IntegerField(primary_key=True)
    slug = models.CharField("Slug", max_length=200)
    date = models.DateTimeField('Date published')
    date_modified = models.DateTimeField(
        'Date modified', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, verbose_name=u'Doctor')
    appointmentdatetime = models.DateTimeField('Date appointment', null=True)
    department = models.ForeignKey(Department, verbose_name=u'Department')
    description = models.CharField(max_length=200)
    dob = models.DateTimeField(max_length=200, null=True, blank=True)
    email = models.EmailField("E-mail", max_length=250, null=True, blank=True)
    lastname = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    update_date = models.DateTimeField('Date update', default=timezone.now)
    guid = models.CharField(max_length=200)

    def __str__(self):
        return "{} {} {} {}".format(self.lastname, self.email,
                                    self.status, self.phone)


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
