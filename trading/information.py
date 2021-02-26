import time
import uuid
from multiprocessing import Pool

from apscheduler.schedulers.background import BackgroundScheduler

pool = Pool(10)

class RefreshFreq(object):
    def __init__(self, weeks=-1, days=0, hours=0, minutes=0, seconds=0):
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def get_refresh_freq_dict(self):
        return {
            'weeks': self.weeks,
            'days': self.days,
            'hours': self.hours,
            'minutes': self.minutes,
            'seconds': self.seconds
        }

    def get_refresh_freq_int(self):
        return self.weeks*60*60*24*7 + self.days*60*60*24 + self.hours*60*60 + self.minutes*60 + self.seconds


class Information(object):
    def __init__(self,
                 op,
                 *args,
                 id: str = None,
                 refresh_freq: RefreshFreq = None,
                 is_auto_refresh: bool = False,
                 scheduler: BackgroundScheduler = None
                 ):
        self.op = op
        self.args = args
        self.id = f"Information-{str(uuid.uuid1())}" if id is not None else id
        self.refresh_freq = refresh_freq
        self.is_auto_refresh = is_auto_refresh
        self.cached_information = None
        self.last_refresh_time = 0
        self.parents = []
        self.childs = args
        self.scheduler = scheduler
        global pool
        self.pool = pool

    def get_information(self):
        if self.refresh_freq is None:
            return self.cached_information
        elif self.last_refresh_time - time.time() > self.refresh_freq.get_refresh_freq_int():
            self.update_information()
            return self.cached_information

    def update_information(self):
        args = self.pool.map(lambda information:information.get_information(), self.args)
        self.cached_information = self.op(*args)
        self.last_refresh_time = time.time()

    def register_auto_refresh(self):
        # call scheduler. run update after refresh_freq
        if self.is_auto_refresh:
            self.scheduler.add_job(self.update_information,
                                   'interval',
                                   id=self.id,
                                   weeks=self.refresh_freq.weeks,
                                   days=self.refresh_freq.days,
                                   hours=self.refresh_freq.hours,
                                   minutes=self.refresh_freq.minutes,
                                   seconds=self.refresh_freq.seconds,
                                   )

    def init_refresh_freq(self):
        min_refresh_freq = None
        for info in self.childs:
            if type(info) == type(self) and info.refresh_freq is not None:
                if min_refresh_freq == None: min_refresh_freq = info.refresh_freq
                if info.refresh_freq.get_refresh_freq_int() < min_refresh_freq.get_refresh_freq_int():
                    min_refresh_freq = info.refresh_freq
        self.refresh_freq = min_refresh_freq


class InformationUDF(Information):
    def __init__(self,
                op,
                *args,
                id: str = None,
                refresh_freq: RefreshFreq = None,
                is_auto_refresh: bool = False,
                scheduler: BackgroundScheduler = None
                ):
        super(InformationUDF, self).__init__(op, *args, id, refresh_freq, is_auto_refresh, scheduler)

        # set refresh_freq as min refresh_freq of childs
        self.init_refresh_freq()
        if self.is_auto_refresh:
            if self.scheduler is None:
                self.scheduler = BackgroundScheduler()
            self.register_auto_refresh()


class InformationAPI(Information):
    def __init__(self,
                api,
                *args,
                id: str = None,
                refresh_freq: RefreshFreq = None,
                is_auto_refresh: bool = False,
                scheduler: BackgroundScheduler = None
                ):
        op = None # TODO: get api op 
        super(InformationAPI, self).__init__(op, *args, id, refresh_freq, is_auto_refresh, scheduler)

        # set refresh_freq as min refresh_freq of childs
        self.init_refresh_freq()
        if self.is_auto_refresh:
            if self.scheduler is None:
                self.scheduler = BackgroundScheduler()
            self.register_auto_refresh()



class InformationConstant(Information):
    def __init__(self, constant):
        self.cached_information = constant
    
    def get_information(self):
        return self.cached_information
    
    def update_information(self):
        pass
    
