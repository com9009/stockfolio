import logging
import time
import uuid

import pykka
from apscheduler.schedulers.background import BackgroundScheduler
from pathos.multiprocessing import ProcessingPool as Pool
from pykka import ActorDeadError, ActorRef, ActorRegistry, messages

scheduler = BackgroundScheduler()
scheduler.start()

logger = logging.getLogger('pykka')

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


class Information(pykka.ThreadingActor):
    """
    Scheduler is not serializable.
    So, use gloval scheduler.
    """

    def __init__(self,
                 op,
                 *args,
                 id: str = None,
                 refresh_freq: RefreshFreq = None,
                 is_auto_refresh: bool = False,
                 ):
        super().__init__()
        self.op = op
        self.args = args
        self.id = "Information-" + str(super().actor_urn)
        self.refresh_freq = refresh_freq
        self.is_auto_refresh = is_auto_refresh
        self.cached_information = None
        self.last_refresh_time = 0
        self.parents = []
        self.childs = args[:-3]
        
        self._update_childs_parent()
        self._start()
        self.actor_proxy = self.actor_ref.proxy()
        

    def _start(self):
        assert self.actor_ref is not None, (
            'Actor.__init__() have not been called. '
            'Did you forget to call super() in your override?'
        )
        ActorRegistry.register(self.actor_ref)
        logger.debug('Starting {}'.format(self))
        self._start_actor_loop()
        return self.actor_ref

    def _update_childs_parent(self):
        for child in self.childs:
            child.parents.append(self)

    def _update_information(self):
        futures = [child.actor_proxy.get_information() for child in self.childs]
        args = [future.get() for future in futures]
        self.cached_information = self.op(*args)
        self.last_refresh_time = time.time()

    def get_information(self):
        if self.refresh_freq is None or self.last_refresh_time - time.time() > self.refresh_freq.get_refresh_freq_int():
            self._update_information()
        return self.cached_information

    def _register_auto_refresh(self):
        # call scheduler. run update after refresh_freq
        if self.is_auto_refresh:
            scheduler.add_job(self.actor_proxy.get_information,
                              'interval',
                              id=self.id,
                              weeks=self.refresh_freq.weeks,
                              days=self.refresh_freq.days,
                              hours=self.refresh_freq.hours,
                              minutes=self.refresh_freq.minutes,
                              seconds=self.refresh_freq.seconds,
                              )

    def _init_refresh_freq(self):
        min_refresh_freq = self.refresh_freq
        for info in self.childs:
            if type(info) == type(self) and info.refresh_freq is not None:
                if min_refresh_freq == None or info.refresh_freq.get_refresh_freq_int() < min_refresh_freq.get_refresh_freq_int():
                    min_refresh_freq = info.refresh_freq
        self.refresh_freq = min_refresh_freq


class InformationUDF(Information):
    def __init__(self,
                 op,
                 *args,
                 id: str = None,
                 refresh_freq: RefreshFreq = None,
                 is_auto_refresh: bool = False,
                 ):
        super(InformationUDF, self).__init__(
            op, *args, id, refresh_freq, is_auto_refresh)

        # set refresh_freq as min refresh_freq of childs
        self._init_refresh_freq()
        if self.is_auto_refresh:
            self._register_auto_refresh()


class InformationAPI(Information):
    def __init__(self,
                 api,
                 *args,
                 id: str = None,
                 refresh_freq: RefreshFreq = None,
                 is_auto_refresh: bool = False,
                 ):
        op = None  # TODO: get api op
        super(InformationAPI, self).__init__(
            op, *args, id, refresh_freq, is_auto_refresh)

        # set refresh_freq as min refresh_freq of childs
        self._init_refresh_freq()
        if self.is_auto_refresh:
            self._register_auto_refresh()


class InformationConstant(Information):
    def __init__(self,
                 constant,
                 *args,
                 id: str = None,
                 refresh_freq: RefreshFreq = None,
                 is_auto_refresh: bool = False,
                 ):
        super(InformationConstant, self).__init__(
            lambda: constant, id, refresh_freq, is_auto_refresh)

