from apscheduler.schedulers.blocking import BlockingScheduler
from fetch_data import cron

# add cron jobs and spin up the scheduler
if __name__ == "__main__":
    sched = BlockingScheduler()

    sched.add_job(cron, "cron", id="midnight", hour=16)
    sched.add_job(cron, "cron", id="noon", hour=1)
    sched.start()
