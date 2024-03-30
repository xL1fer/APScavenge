from apscheduler.schedulers.background import BackgroundScheduler

def sample_task():
    print("Working...")

def init_tasks():
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(sample_task, 'interval', seconds=5)
    scheduler.start()

    #print("Tasks initialized.")