import datetime
from datetime import timedelta
from datetime import timezone
import time


class RSI_Timezone(object):

    # Standards fo the Timezones we want to work in.
    TIMEZONE_KELOWNA = timezone(-timedelta(hours=8), name="Kelowna") # GMT-8
    TIMEZONE_TORONTO = timezone(-timedelta(hours=5), name="Toronto") # GMT-5

    def time_zone_test(self):
        # https://www.reddit.com/r/BitMEX/comments/8aimm4/getting_historical_data_through_the_api_python/
        # print("UTC: "+str(datetime.datetime.now(tz=datetime.timezone.utc)))
        # kelowna = datetime.timezone(-timedelta(hours=8), name="Kelowna Timezone!")
        # kelowna_td = kelowna.utcoffset(datetime.datetime.now(tz=datetime.timezone.utc))
        # current_time = datetime.datetime.now(timezone.utc)+kelowna_td
        # current_time = datetime.datetime.combine(current_time.date(), current_time.time(), tzinfo=kelowna)
        # print(str(current_time))
        # I think that works!!!!

        #Cleaning up the above
        datetime_utc = datetime.datetime.now(timezone.utc)
        print("The time in "+str(datetime_utc.tzname())+" is: "+str(datetime_utc))

        #Kelowna
        timezone_kelowna = datetime.timezone(-timedelta(hours=8), name="Kelowna")
        timedelta_kelowna = timezone_kelowna.utcoffset(datetime_utc)
        datetime_kelowna = datetime_utc+timedelta_kelowna
        datetime_kelowna = datetime.datetime.combine(datetime_kelowna.date(), datetime_kelowna.time(), tzinfo=timezone_kelowna)
        print("The time in "+str(datetime_kelowna.tzname())+" is: "+str(datetime_kelowna))
    
    # Method to get the current time in the selected timezone.
    def get_current_datetime_in_timezone(self, selected_timezone):
        datetime_utc = datetime.datetime.now(timezone.utc)
        #print("The time in "+str(datetime_utc.tzname())+" is: "+str(datetime_utc))
        #selected
        timezone_selected = datetime.timezone(-timedelta(hours=8), name=selected_timezone.tzname())
        timedelta_selected = timezone_selected.utcoffset(datetime_utc)
        datetime_selected = datetime_utc+timedelta_selected
        datetime_selected = datetime.datetime.combine(datetime_selected.date(), datetime_selected.time(), tzinfo=timezone_selected)
        print("The time in "+str(datetime_selected.tzname())+" is: "+str(datetime_selected))
        return datetime_selected