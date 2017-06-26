from apscheduler.schedulers.blocking import BlockingScheduler
from worker import cron

# add cron jobs and spin up the scheduler
if __name__ == "__main__":
    sched = BlockingScheduler()

    sched.add_job(cron, "cron", id="noon", hour=16)
    sched.add_job(cron, "cron", id="nine_pm", hour=1)
    sched.start()
