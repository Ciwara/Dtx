import sys
import kronos

from django.core.management.base import BaseCommand, CommandError

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, GetPost
from doctix.models import (Appointment, Doctor, Department, Specialtie,
                           PersonalClinicHour)


@kronos.register('* * * * * *')
class Command(BaseCommand):
    help = 'Closes the specified apptts for voting'

    def add_arguments(self, parser):
        # parser.add_argument('apptts_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):

        # retrives the list of all posts in the blog. Optional: you can supply
        # filters and fields to sort by.

        print('Hello, world!')
        from django.conf import settings
        wp = Client('http://doctix.net/xmlrpc.php',
                    settings.LOGIN_WP, settings.PASS_WP)
        self.update_department(wp)
        self.update_doctor_info(wp)
        self.update_appointment(wp)
        self.stdout.write(self.style.SUCCESS('Successfully update finist '))

    def update_doctor_info(self, wp):
        """wordpress_xmlrpc.methods.options.GetOptions """
        # get pages in batches of 20

        from schedule.models import Calendar
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
                print(doc.title, doc.slug)
                cal, s = Calendar.objects.get_or_create(
                    name=doc.title, slug=doc.slug)
                print(cal)
                data = {
                    "post_id": doc.id,
                    "slug": doc.slug,
                    "full_name": doc.title,
                    # "sms_submit": doc.sms_submit,
                    "date": doc.date,
                    "date_modified": doc.date_modified,
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
                doctor = Doctor(**data)
                doctor.save()
                self.stdout.write(self.style.SUCCESS(
                    'Successfully save info. {}'.format(doc.title)))

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

        self.stdout.write(self.style.SUCCESS(
            'Successfully save department : {}'.format(specialty.name)))
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
                    "date": depart.date,
                    "date_modified": depart.date_modified,
                    "guid": depart.guid
                }
                for custom in depart.custom_fields:
                    if custom['key'] == 'iva_dept_shortinfo':
                        data.update({"dept_shortinfo": custom['value']})
                dept = Department(**data)
                dept.save()
                self.stdout.write(self.style.SUCCESS(
                    'Successfully save department : {}'.format(dept.title)))

            offset = offset + increment

    def update_appointment(self, wp):

        offset = 0
        increment = 20
        while True:
            posts = wp.call(GetPosts({'post_type': 'appointment',
                                      'number': increment, 'offset': offset}))
            if len(posts) == 0:
                break  # no more posts returned
            for app in posts:
                data = {
                    'post_id': app.id,
                    'slug': app.slug,
                    'date': app.date,
                    'guid': app.guid
                }
                for custom in app.custom_fields:
                    # if custom['key'] == 'iva_appt_appointmentdate':
                    #     data.update({"appointmentdate": custom['value']})
                    # if custom['key'] == 'iva_appt_appointmenttime':
                    #     data.update({"appointmenttime": custom['value']})
                    if custom['key'] == 'iva_appt_department':
                        data.update({"department": Department.objects.get(
                            post_id=int(custom['value']))})
                    if custom['key'] == 'iva_appt_description':
                        data.update({"description": custom['value']})
                    # if custom['key'] == 'iva_appt_dob':
                    #     data.update({"dob": custom['value']})
                    if custom['key'] == 'iva_appt_doctor':
                        data.update({"doctor": Doctor.objects.get(
                            post_id=int(custom['value']))})
                    if custom['key'] == 'iva_appt_email':
                        data.update({"email": custom['value']})
                    if custom['key'] == 'iva_appt_lastname':
                        data.update({"lastname": custom['value']})
                    if custom['key'] == 'iva_appt_phone':
                        data.update({"phone": custom['value']})
                    if custom['key'] == 'iva_appt_status':
                        data.update({"status": custom['value']})
                print(data)
                appoint = Appointment(**data)
                appoint.save()

                self.stdout.write(self.style.SUCCESS(
                    'Successfully save appointment : {}'.format(app.title)))
            offset = offset + increment

"""
[{'value': '', 'id': '16218', 'key': 'iva_hrs_Friday_close'},

 {'value': '18:00', 'id': '16216', 'key': 'iva_hrs_Friday_closes'},
 {'value': '09:00', 'id': '16217', 'key': 'iva_hrs_Friday_opens'},
 {'value': 'on', 'id': '16206', 'key': 'iva_hrs_Monday_close'},
 {'value': '18:00', 'id': '16204', 'key': 'iva_hrs_Monday_closes'},
 {'value': '09:00', 'id': '16205', 'key': 'iva_hrs_Monday_opens'},
  {'value': '', 'id': '16221', 'key': 'iva_hrs_Saturday_close'},
  {'value': '18:00', 'id': '16219', 'key': 'iva_hrs_Saturday_closes'},
  {'value': '09:00', 'id': '16220', 'key': 'iva_hrs_Saturday_opens'},
  {'value': '', 'id': '16224', 'key': 'iva_hrs_Sunday_close'},
  {'value': '18:00', 'id': '16222', 'key': 'iva_hrs_Sunday_closes'},
  {'value': '09:00', 'id': '16223', 'key': 'iva_hrs_Sunday_opens'},
  {'value': '', 'id': '16215', 'key': 'iva_hrs_Thursday_close'},
  {'value': '18:00', 'id': '16213', 'key': 'iva_hrs_Thursday_closes'},
  {'value': '09:00', 'id': '16214', 'key': 'iva_hrs_Thursday_opens'},
  {'value': '12', 'id': '16225', 'key': 'iva_hrs_timeformat'},
  {'value': '', 'id': '16209', 'key': 'iva_hrs_Tuesday_close'},
  {'value': '18:00', 'id': '16207', 'key': 'iva_hrs_Tuesday_closes'},
  {'value': '09:00', 'id': '16208', 'key': 'iva_hrs_Tuesday_opens'},
  {'value': '', 'id': '16212', 'key': 'iva_hrs_Wednesday_close'},
  {'value': '18:00', 'id': '16210', 'key': 'iva_hrs_Wednesday_closes'},
  {'value': '09:00', 'id': '16211', 'key': 'iva_hrs_Wednesday_opens'},
  {'value': 'fullwidth', 'id': '16196', 'key': 'sidebar_options'},
  {'value': 'default', 'id': '16188', 'key': 'slide_template'},
  {'value': 'left', 'id': '16189', 'key': 'sub_styling'},
  {'value': 'a:5:{s:5:"image";s:0:"";s:5:"color";s:0:"";s:6:"repeat";s:6:"repeat";s:8:"position";s:8:"left top";s:11:"attachement";s:6:"scroll";}', 'id': '16293', 'key': 'subheader_img'},
  {'value': 'a:5:{s:5:"image";s:0:"";s:5:"color";s:0:"";s:6:"repeat";s:6:"repeat";s:8:"position";s:8:"left top";s:11:"attachement";s:6:"scroll";}', 'id': '16294', 'key': 'subheader_img'},
  {'value': 'a:5:{s:5:"image";s:0:"";s:5:"color";s:0:"";s:6:"repeat";s:6:"repeat";s:8:"position";s:8:"left top";s:11:"attachement";s:6:"scroll";}', 'id': '16295', 'key': 'subheader_img'},
  {'value': 'a:5:{s:5:"image";s:0:"";s:5:"color";s:0:"";s:6:"repeat";s:6:"repeat";s:8:"position";s:8:"left top";s:11:"attachement";s:6:"scroll";}', 'id': '16296', 'key': 'subheader_img'},
  {'value': 'a:5:{s:5:"image";s:0:"";s:5:"color";s:0:"";s:6:"repeat";s:6:"repeat";s:8:"position";s:8:"left top";s:11:"attachement";s:6:"scroll";}', 'id': '16297', 'key': 'subheader_img'},
  {'value': 'default', 'id': '16190', 'key': 'subheader_teaser_options'}]
"""
