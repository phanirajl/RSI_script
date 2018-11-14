import datetime
from datetime import timedelta
from datetime import timezone
import time


class RSI_Timezone(object):
    """
    This class is a WORK IN PROGRESS.
    This class is meant to abstract the timezone concerns away from the regular RSI code
    """

    # Timezones
    TIMEZONE_KELOWNA = timezone(-timedelta(hours=8), name="Kelowna")
    TIMEZONE_TORONTO = timezone(-timedelta(hours=5), name="Toronto")

    # Timedeltas
    #NOTE: These strange values were measured in both timezones, and deemed to be correct. Just putting them here, and not asking questions.
    TIMEDELTA_KELOWNA = -timedelta(hours=12)
    TIMEDELTA_TORONTO = -timedelta(hours=8)
    

    def __init__(self):
        pass
        # # Create a dictionary for the Timezones we want to work in.
        # self.TIMEZONE_DICT = dict([
        #     ("Kelowna", timezone(-timedelta(hours=8), name="Kelowna")),
        #     ("Toronto", timezone(-timedelta(hours=5), name="Toronto"))
        # ])
        # print(self.TIMEZONE_DICT)
        # print(str(type(self.TIMEZONE_DICT)))
        # print(str(self.TIMEZONE_DICT.keys()))

    # Quick ,get Kelowna timezone
    def get_kelowna_timezone(self):
        return self.TIMEZONE_KELOWNA

    # Quick, get Toronot timezone.
    def get_toronto_timezone(self):
        return self.TIMEZONE_TORONTO

    # Method to get the current time in the selected timezone.
    def get_current_datetime_in_timezone(self, selected_timezone):
        """
        This method provides the current datetime based in the input timezone.
        Please note that the 'selected_timezone' argument must be an RSI_Timezone
        constant. //!@#fix incorrect

        Attributes:
            selected_timezone_key -- This is the key from the dictionary of timezones that you want the current datetime in. Needs to be a key in the dict.
        """
   
        # Get the UTC datetime first. Alwyas start at UTC, and localize your way back from there.
        datetime_utc = datetime.datetime.now(timezone.utc)
        #print("The time in "+str(datetime_utc.tzname())+" is: "+str(datetime_utc))
        
        # Get the Timedelta, as the offset of the 'selected_timezone' param from UTC
        timedelta_selected = selected_timezone.utcoffset(datetime_utc)

        # Calculate the datetime of the selected timezone using: utc - selected timedelta
        datetime_selected = datetime_utc+timedelta_selected
        
        # Utilize 'combine' in order to add the selected's timezone infor to the new datetime.
        datetime_selected = datetime.datetime.combine(datetime_selected.date(), datetime_selected.time(), tzinfo=selected_timezone)

        #print("The time in "+str(selected_timezone.tzname(datetime_selected))+" is: "+str(datetime_selected))
        return datetime_selected


#--------------------WIP---------------------

     # WIP, Method to fetch one of the timezones from the dict
    def get_timezone(self, selected_timezone):
        
        # Attmept to get the value from the dict
        returned_timezone = self.TIMEZONE_DICT.get(selected_timezone)
        if returned_timezone is None: print("Didn't work again..........")
        # Validation failing, figure out in future. going crazy atm
        # # Validate the result, and return of possible.
        # if returned_timezone is None:
        #     raise TypeError("parameter 'selected_timezone' must be a key of the RSI_Timezone TIMEZONE_DICT dictionary. \""+str(selected_timezone)+"\" doens't exist.")
        # else:
        #     return returned_timezone

        return returned_timezone

    # WIP, Just a test method. Will delete later.
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
    
    # WIP, Just a test method. Will delete later.
    def time_zone_test2(self):
        test = self.get_timezone("Kelowna")
        print(str(type(test)))
        #print(type(str(self.get_timezone("Toronto"))))