from datetime import *
from dateutil.relativedelta import *
import calendar

NOW = datetime.now()
TODAY = date.today()
print(f"{NOW}")

FREQ = relativedelta(minutes=+30)

print(f"{NOW + FREQ}")


from dateutil.relativedelta import *
def check_awr_completeness(dates: list):
    # awr_frequency = "00:30:00"
    # duration_obj = datetime.strptime("00:30:00", '%H:%M:%S')

    first_date = dates[0]
    last_date = dates[-1]
    iterator_date = first_date

    while iterator_date <= last_date:
        print(f"date: {iterator_date} - {type(iterator_date)}")
        iterator_date += relativedelta(minutes=+30)

        list_index = 0
        for counter in range(list_index, len(dates)):
            print(f"{dates[counter]}")
            # c = a - b
            print('Difference: ', counter - iterator_date)