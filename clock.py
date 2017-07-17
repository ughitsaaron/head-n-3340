from apscheduler.schedulers.blocking import BlockingScheduler
import os


def run_cron():
    os.system("python worker.py")


# add cron jobs and spin up the scheduler
if __name__ == "__main__":
    sched = BlockingScheduler()

    sched.add_job(run_cron, "cron", id="noon", hour=16)
    sched.add_job(run_cron, "cron", id="nine_pm", hour=1)
    sched.start()
