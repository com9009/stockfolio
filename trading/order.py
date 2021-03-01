import pykka
import information
import uuid

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()


class OrderAPI(object):
    def __init__(self,
                 buy_api,
                 sell_api,
                 ):
        self.buy_api = buy_api
        self.sell_api = sell_api

    def buy(self, stock, value):
        self.buy_api(stock, value)

    def sell(self, stock, value):
        self.sell_api(stock, value)

    def order(self, arg):
        if arg[1] > 0:
            self.buy_api(arg[0], arg[1])
        elif arg[1] < 0:
            self.sell_api(arg[0], arg[1])


""" 
    order_func return : [(stock, value)] 
                        if value > 0 buy, elif value < 0 sell
    args : information
    
    None value in order_api is for test 
"""
class Order(pykka.ThreadingActor):
    def __init__(self,
                 order_func,
                 *args,
                 check_interval: information.RefreshFreq = None,
                 auto_check: bool = False,
                 order_api: OrderAPI = None
                 ):
        super().__init__()
        self.order_func = order_func
        self.args = args
        self.id = super().actor_urn
        self.check_interval = check_interval
        self.is_auto_check = auto_check
        self.order_api = order_api

    def check_order(self):
        futures = list(map(lambda info: info.actor_proxy.get_information(), self.args))
        args = [future.get() for future in futures]
        if self.order_api is not None:
            map(lambda stock_value: self.order_api.order(stock_value), self.order_func(*args))
        else:
            print(args)

    def register_auto_check(self):
        if self.is_auto_check and self.check_interval is not None:
            scheduler.add_job(self.check_order,
                              'interval',
                              id=self.id,
                              weeks=self.check_interval.weeks,
                              days=self.check_interval.days,
                              hours=self.check_interval.hours,
                              minutes=self.check_interval.minutes,
                              seconds=self.check_interval.seconds,
                              )
