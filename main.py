import time
from pathos.multiprocessing import ProcessingPool as Pool

from apscheduler.schedulers.background import BackgroundScheduler
from trading.information import InformationUDF, InformationConstant, RefreshFreq


if __name__ == '__main__':
    day_count = InformationConstant(2)

    current_time_refresh_freq = RefreshFreq(seconds=5)
    current_time = InformationUDF(lambda: time.time(),
                                  refresh_freq=current_time_refresh_freq, 
                                  is_auto_refresh=True
                                  )

    def time_add(current_time, day_count):
        print("current_time:", current_time)
        print("day_count: ", day_count)

        output = current_time + day_count
        print("output: ", output)

        return output

    root_information = InformationUDF(time_add, current_time, day_count)

    while True:
        print(root_information.actor_proxy.get_information().get())
        time.sleep(2)
