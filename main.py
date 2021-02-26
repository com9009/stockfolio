import time

from trading.information import InformationUDF, InformationConstant, RefreshFreq

day_count = InformationConstant(2)

current_time_refresh_freq = RefreshFreq(seconds=5)
current_time = InformationUDF(lambda: time.time(), refresh_freq=current_time_refresh_freq, is_auto_refresh=True)

def time_add(current_time, day_count):
    print("current_time:", current_time)
    print("day_count: ", day_count)

    output = current_time + day_count
    print("output: ", output)

    return output

root_information = InformationUDF(time_add, current_time, day_count)

while True:
    print(root_information.get_information())
    time.sleep(2)

