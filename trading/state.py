import pykka
import information
import uuid

from apscheduler.schedulers.background import BackgroundScheduler


# args : information proxy
class State(pykka.ThreadingActor):
    def __init__(self,
                 cond_func,
                 *args,
                 id: str = None,
                 check_interval: information.RefreshFreq = None,
                 scheduler: BackgroundScheduler = None,
                 auto_check: bool = False
                 ):
        super().__init__()
        self.cond_func = cond_func
        self.args = args
        self.id = f"State-{str(uuid.uuid1())}" if id is not None else id
        self.check_interval = check_interval
        self.scheduler = scheduler
        self.is_auto_check = auto_check

    def check_condition(self):
        informations = list(map(lambda info: info.get_information(), self.args))
        return self.cond_func(*informations)

    def register_auto_check(self):
        if self.is_auto_check:
            self.scheduler.add_job(self.check_condition,
                                   'interval',
                                   id=self.id,
                                   weeks=self.check_interval.weeks,
                                   days=self.check_interval.days,
                                   hours=self.check_interval.hours,
                                   minutes=self.check_interval.minutes,
                                   seconds=self.check_interval.seconds,
                                   )
