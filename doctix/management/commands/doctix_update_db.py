import re
import kronos
import datetime
import pytz

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.conf import settings

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods.posts import GetPosts
from doctix.models import (Appointment, Doctor, Department, Specialtie,
                           PersonalClinicHour, SMSMessage)

from schedule.models import Calendar
from schedule.models import Event


@kronos.register('1 * * * * *')
class Command(BaseCommand):
    help = 'Closes the specified apptts for voting'

    def add_arguments(self, parser):
        # parser.add_argument('apptts_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):

        # retrives the list of all posts in the blog. Optional: you can supply
        # filters and fields to sort by.
        wp = Client(settings.CLIENT_URL, settings.LOGIN_WP, settings.PASS_WP)
        self.update_department(wp)
        self.update_doctor_info(wp)
        self.update_appointment(wp)
        self.stdout.write(self.style.SUCCESS('Successfully update finist '))

    def add_tz(self, date):
        tz = pytz.timezone(settings.TIME_ZONE)
        return date.replace(tzinfo=tz)

    def update_doctor_info(self, wp):
        """wordpress_xmlrpc.methods.options.GetOptions """
        # get pages in batches of 20

        offset = 0
        increment = 20
        while True:
            posts = wp.call(GetPosts({'post_type': 'doctor',
                                      'number': increment, 'offset': offset}))
            if len(posts) == 0:
                break  # no more posts returned
            for doc in posts:
                specialty_id = self.save_specialty(doc.terms)
                if doc.slug == "":
                    continue

                cal, s = Calendar.objects.update_or_create(name=doc.title,
                                                           slug=doc.slug)
                data = {
                    "post_id": doc.id,
                    "slug": doc.slug,
                    "full_name": doc.title,
                    # "sms_submit": doc.sms_submit,
                    "date": self.add_tz(doc.date),
                    "date_modified":  self.add_tz(doc.date_modified),
                    "sticky": doc.sticky,
                    "link": doc.link,
                    "specialty": specialty_id,
                    "calendar": cal,
                }
                for custom in doc.custom_fields:
                    clinic_hrs_desc = ""
                    if custom['key'] == 'iva_dr_location':
                        data.update({"location": custom['value']})
                    if custom['key'] == 'iva_clinic_hrs_desc':
                        data.update({"clinic_hrs_desc": custom['value']})
                    if custom['key'] == 'iva_dr_phone':
                        data.update({"phone": custom['value']})
                    if custom['key'] == 'iva_doctor_email':
                        data.update({"email": custom['value']})
                doctor, created = Doctor.objects.update_or_create(
                    post_id=doc.id, defaults=data)

            offset = offset + increment
        # update_hrs_opens_closes_per_doc(doctor)

    def update_hrs_opens_closes_per_doc(self, doctor):
        pass

    def save_specialty(self, spties):
        """Un doc peut avoir combien de specialité ?
           """
        for spty in spties:
            data = {
                "slug": spty.slug,
                "name": spty.name,
                "description": spty.description,
            }
            specialty = Specialtie(**data)
            specialty.save()
            break
        return specialty

    def update_department(self, wp):

        offset = 0
        increment = 20
        while True:
            posts = wp.call(GetPosts({'post_type': 'department',
                                      'number': increment, 'offset': offset}))
            if len(posts) == 0:
                break  # no more posts returned
            for depart in posts:
                data = {
                    "post_id": depart.id,
                    "slug": depart.slug,
                    "title": depart.title,
                    "date":  self.add_tz(depart.date),
                    "date_modified": self.add_tz(depart.date_modified),
                    "guid": depart.guid
                }
                for custom in depart.custom_fields:
                    if custom['key'] == 'iva_dept_shortinfo':
                        data.update({"dept_shortinfo": custom['value']})

                depat, created = Department.objects.update_or_create(
                    post_id=depart.id, defaults=data)

            offset = offset + increment

    def update_appointment(self, wp):

        offset = 0
        increment = 20

        now = timezone.now()
        while True:
            posts = wp.call(GetPosts({'post_type': 'appointment',
                                      'number': increment, 'offset': offset}))
            if len(posts) == 0:
                break  # no more posts returned
            for post in posts:
                data = {
                    'firstname': post.title,
                    'post_id': post.id,
                    'slug': post.slug,
                    'date':  self.add_tz(post.date),
                    'guid': post.guid
                }
                for custom in post.custom_fields:
                    if custom['key'] == 'iva_appt_gender':
                        data.update({"gender": custom['value']})
                    if custom['key'] == 'iva_appt_appointmentdate':
                        appointmentdate = int(custom['value'])
                    if custom['key'] == 'iva_appt_appointmenttime':
                        appointmenttime = custom['value']
                    if custom['key'] == 'iva_appt_department':
                        data.update({"department": Department.objects.get(
                            post_id=int(custom['value']))})
                    if custom['key'] == 'iva_appt_description':
                        data.update({"description": custom['value']})
                    if custom['key'] == 'iva_appt_dob' and custom['value'] != "":
                        timestamp = int(custom['value'])
                        data.update(
                            {"dob": datetime.date.fromtimestamp(timestamp)})
                    if custom['key'] == 'iva_appt_doctor':
                        data.update({"doctor": Doctor.objects.get(
                            post_id=int(custom['value']))})
                    if custom['key'] == 'iva_appt_email':
                        data.update({"email": custom['value']})
                    if custom['key'] == 'iva_appt_lastname':
                        data.update({"lastname": custom['value']})
                    # if custom['key'] == 'iva_appt_firstname':
                    #     data.update({"firstname": custom['value']})
                    if custom['key'] == 'iva_appt_phone':
                        data.update({"phone": custom['value']})
                    if custom['key'] == 'iva_appt_status':
                        data.update({"status": custom['value']})

                data.update({"appointmentdatetime":
                             self.timestamp_date_with_tz(appointmentdate, appointmenttime)})
                appoint, created = Appointment.objects.update_or_create(
                    post_id=post.id, defaults=data)
                phone = appoint.doctor.phone
                appoint_date = appoint.date
                if appoint.status != Appointment.CANCELLED:
                    if not phone:
                        # phone = 76433890
                        continue
                        # print(
                        #     u"{} n'a pas de numéro de téléphone.".format(appoint.doctor.full_name))
                        # return
                    data = {
                        'direction': SMSMessage.OUTGOING,
                        'identity': phone,
                        'event_on': appoint_date,
                        'text': appoint.format_notiv_doct_sms(),
                        'created_on': now,
                        # 'handled': True,
                    }
                    try:
                        msg, created = SMSMessage.objects.update_or_create(
                            event_on=appoint_date, defaults=data)
                        print(created)
                    except Exception as e:
                        print("EEE", e)
                    if appoint.status == Appointment.CONFIRMED:
                        data = {
                            'title': appoint.description,
                            'start': appoint.appointmentdatetime,
                            'end': appoint.appointmentdatetime + datetime.timedelta(minutes=30),
                            # 'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
                            # 'rule': rule,
                            'calendar': Calendar.objects.get(slug=appoint.doctor.slug)
                        }
                        event, s = Event.objects.update_or_create(data)
                    # self.stdout.write(self.style.SUCCESS(
                    #     'Successfully save appointment : {}'.format(app.title)))
            offset = offset + increment

    # def format_notiv_sms_appointment(self, appoint):
    #     text = "Demande RDV num {id}. {full_name} {des}".format(
    #         id=appoint.post_id, full_name=appoint.full_name(), des=appoint.description)
    #     if len(text) == 120:
    #         text = text[:117] + "..."
    #     return text

    def timestamp_date_with_tz(self, timestamp, time_):
        date = datetime.date.fromtimestamp(timestamp)
        hrs = int(re.search('(?<="appt_time_hrs";s:2:")\w+', time_).group(0))
        mnts = int(re.search('(?<="appt_time_mnts";s:2:")\w+', time_).group(0))
        period = re.search(
            '(?<="appt_time_period";s:2:")\w+', time_).group(0)
        if period == "PM":
            hrs += 12 if hrs < 12 else -12
        return self.add_tz(datetime.datetime(date.year, date.month, date.day, hrs, mnts))
