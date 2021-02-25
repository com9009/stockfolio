import time


class Information(object):
    def __init__(self, 
                 op, 
                 *args, 
                 refresh_freq=None, 
                 is_auto_refresh=False,
                 scheduler=None
                 ):
        self.op = args
        self.args = args
        self.refresh_freq = refresh_freq
        self.is_auto_refresh = is_auto_refresh
        self.cached_information = None
        self.last_refresh_time = None
        self.parents = []
        self.childs = args

        # set refresh_freq as min refresh_freq of childs
        self.init_refresh_freq()
        
       
    def update_information(self):
        args = self.args
        self.cached_information = self.op(*args)
        self.last_refresh_time = time.time()
        
        # call scheduler. run update after refresh_freq
        if self.is_auto_refresh:
            # TODO : make scheduler and launch job
            pass
    
    def init_refresh_freq(self):
        min_refresh_freq = float('inf')
        for info in self.childs:
            if type(info) == type(self) and info.refresh_freq is not None:
                if info.refresh_freq < min_refresh_freq:
                    min_refresh_freq = info.refresh_freq
        self.refresh_freq = min_refresh_freq

class InformationAPI(Information):
    pass

class InformationUDF(Information):
    pass
