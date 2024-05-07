from apscheduler.schedulers.background import BackgroundScheduler

from .models import Seizure

from apserver.emailparser import emailparser

def email_parser_task():
    seizure = Seizure.objects.filter(user_data="").first()
    if seizure is not None:
        seizure.user_data = emailparser.parse_email(seizure.email)
        seizure.save()

def init_tasks():
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(email_parser_task, 'interval', minutes=3)
    scheduler.start()

    #print("Tasks initialized.")