import kronos
import datetime

import logging

from django.utils import timezone
from django.core.management.base import BaseCommand
from doctix.models import SMSMessage, Appointment

logger = logging.getLogger(__name__)


@kronos.register('*/30 * * * * *')
class Command(BaseCommand):
    help = 'Closes the specified apptts for voting'

    def add_arguments(self, parser):
        # parser.add_argument('apptts_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("Update message outgoing")
        now = timezone.now()
        in_halfhour = now + datetime.timedelta(minutes=30)
        for appoint in Appointment.objects.filter(appointmentdatetime__gte=now,
                                                  appointmentdatetime__lte=in_halfhour):
            phone = appoint.doctor.phone
            if not phone:
                print("{} n'a pas de numéro de telephone".format(
                    appoint.doctor.full_name))
                return
            data = {
                "direction": SMSMessage.OUTGOING,
                "identity": phone,
                "event_on": appoint.date,
                "text": appoint.description,
                "defaults": {'created_on': now}
            }
            try:
                msg, created = SMSMessage.objects.get_or_create(**data)
            except Exception as e:
                print(e)
                logger.critical("Unable to save SMS into DB: {}".format(e))
                # raise
