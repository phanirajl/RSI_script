import json
import datetime
from datetime import timedelta
from datetime import timezone
import sched
import time

from script import RSI_Script
from RSI_Timezone_Helper import RSI_Timezone

# Method for the scheduler to run 
def go(wait=60):
    """
    This method provides a handler for the below Python Scheduler to execute. It contains the waiting logic between cycles.
    """
    # Flag, for the desired Timezone
    SELECTED_TIMEZONE = RSI_Timezone.TIMEZONE_KELOWNA
    
    # Get the start time.
    start_time = RSI_Timezone().get_current_datetime_in_timezone(selected_timezone=SELECTED_TIMEZONE)
    print("Start:\t\t"+str(start_time)+"\t("+str(start_time.tzname())+")")

    # Calculate the end time, based on the input wait
    end_time = start_time + timedelta(seconds=wait)
    print("Wait:\t\t"+str(end_time)+"\t("+str(wait)+" seconds)")
    
    # Create new RSI_Script
    my_rsi = RSI_Script(selected_timezone=SELECTED_TIMEZONE)

    # Run the RSI_Script instance. If run succeeds, it automatically stops itself.
    my_rsi.run()

    # Stop the RSI_Script instance.
    # my_rsi.stop()
    
    # Get the time that the RSI_Script completed its work.
    complete_time = datetime.datetime.now(SELECTED_TIMEZONE)

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
try:
    # Forever and ever and ever and ever....
    while True:
        
        # Get the event created by immediately scheduling a run of the above "go" method.
        # NOTE: The 30 seconds wait here is just an example...you can change it to whatever you want. Ideally 60, so you know your code runs exactly every minute, or however quick it can over 60 seconds.
        e = s.enter(0, 1, go(30))
        # print("Queue: "+str(s.queue))

        # Remove the above event from the Schedule queue, so we don't have a massive queue sucking up memory over long periods of time.
        s.cancel(e)

except KeyboardInterrupt:
    print("So long, and thanks for all the fish!.")
  
