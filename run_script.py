#!/usr/bin/python3
import json
import datetime
from datetime import timedelta
from datetime import timezone
import sched
import time

from script import RSI_Script
from RSI_Timezone_Helper import RSI_Timezone
# Instance of RSI_Timzone
my_rsi_timezone = RSI_Timezone()

# Flag, for the desired Timezone
SELECTED_TIMEZONE = my_rsi_timezone.get_kelowna_timezone()

# Create new RSI_Script's
my_rsi_bitcoin = RSI_Script(SELECTED_TIMEZONE,"XBTUSD",30)
my_rsi_ethereum = RSI_Script(SELECTED_TIMEZONE,"ETHUSD",30)
my_rsi_ripple = RSI_Script(SELECTED_TIMEZONE,"XRPZ18",100)
my_rsi_cardano = RSI_Script(SELECTED_TIMEZONE,"ADAZ18",1000)
my_rsi_bitcoincash = RSI_Script(SELECTED_TIMEZONE,"BCHZ18",1)
my_rsi_EOS = RSI_Script(SELECTED_TIMEZONE,"EOSZ18",10)
my_rsi_litecoin = RSI_Script(SELECTED_TIMEZONE,"LTCZ18",1)
my_rsi_tron = RSI_Script(SELECTED_TIMEZONE,"TRXZ18",2000)

# A method created to be run by the Python Scheduler below.
def go(wait=60):
    """
    This method provides a handler for the below Python Scheduler to execute. It contains the waiting logic between cycles.
    """

    
    # Get the start time.
    start_time = my_rsi_timezone.get_current_datetime_in_timezone(SELECTED_TIMEZONE)
    print("Start:\t\t"+str(start_time)+"\t("+str(start_time.tzname())+")")

    # Calculate the end time, based on the input wait
    end_time = start_time + timedelta(seconds=wait)
    print("Wait:\t\t"+str(end_time)+"\t("+str(wait)+" seconds)")
    


    # Run the RSI_Script instance. If run succeeds, it automatically stops itself.
    my_rsi_bitcoin.run()
    my_rsi_ethereum.run() 
    my_rsi_ripple.run()
    my_rsi_cardano.run()
    my_rsi_bitcoincash.run()
    my_rsi_EOS.run()
    my_rsi_litecoin.run()
    my_rsi_tron.run()
    
    # Get the time that the RSI_Script completed its work.
    complete_time = my_rsi_timezone.get_current_datetime_in_timezone(SELECTED_TIMEZONE)

    # Calculate the remaining wait from the start and end datetimes (which returns a timedelta)
    remaining_wait_timedelta = end_time - complete_time
    print("Completed: \t"+str(complete_time)+"\tDuration: "+str(remaining_wait_timedelta.seconds)+" sec.")

    # If there is any expeceted time to be waiting, wait it. else, show the overtime.
    if(remaining_wait_timedelta > timedelta(seconds=0)):
        print("Waiting:\t"+str(remaining_wait_timedelta.seconds)+" seconds.")
        time.sleep(remaining_wait_timedelta.seconds)
    else:
        print("Overtime:\t"+str(remaining_wait_timedelta.seconds)+" seconds.")

    # Print a separator to console.
    print("\n----------------------------\n")



# Initalize the Python Scheduler.
print("Initializing the Python Scheduler.")
s = sched.scheduler(time.time, time.sleep)

# Surround the loop with a keyboard interrrupt to fail gracefully
run=True
while run==True:
    try:   

        e = s.enter(0, 1, go(30))
        # print("Queue: "+str(s.queue))

        # Remove the above event from the Schedule queue, so we don't have a massive queue sucking up memory over long periods of time.
        s.cancel(e)
    except KeyboardInterrupt:
        run=False
        my_rsi_bitcoin.stop()
        my_rsi_ethereum.stop()
        my_rsi_ripple.stop()
        my_rsi_cardano.stop()
        my_rsi_bitcoincash.stop()
        my_rsi_EOS.stop()
        my_rsi_litecoin.stop()
        my_rsi_tron.stop()
        #my_rsi_litecoin.stop()
        #my_rsi_ripple.stop()

        print("So long, and thanks for all the fish!.")
    except Exception as e:
        time.sleep(1)
        print ("Hey we caught a general exception")

  
