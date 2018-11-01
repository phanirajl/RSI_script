from colorama import init, deinit, Fore, Back, Style

class RSI_Generic_Error(Exception):
    """
    Base class for exceptions in the RSI_Script.
    
    Attributes:
        message -- Explanation of why the error is being shown
    """
    def __init__(self, message=None):
      
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "A RSI_Generic_Error has been raised, with no explaination."
        else:
            self.message = message
                
        # Does this need to be superclassed now.
        #super(RSI_Generic_Error, self).__init__(self.message)
        #Exception.__init__(self, self.message)

    # def __str__(self):
    #     init(autoreset=True, strip=True)
    #     return repr(Style.BRIGHT+Fore.RED+"[X]    "+str(self.__class__.__name__)+": "+self.message)

    def __str__(self):
        return repr("[X]    "+str(self.__class__.__name__)+": "+self.message)

class HTTP_503_Error(RSI_Generic_Error):
    """
    Error to handle HTTP 503 responses from the Bitmex client. Subclass of RSI_Generic_Error.
    
    Attributes:

        message -- Explanation of why the error is being shown
    """
    # NOTE: "To help improve responsiveness during high-load periods, the BitMEX trading engine will begin load-shedding when requests reach a critical queue depth. When this happens, you will quickly receive a 503 status code with the message "The system is currently overloaded. Please try again later." The request will not have reached the engine, and you should retry after at least 500 milliseconds."

    def __init__(self, message):
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "An HTTP 503 has been raised, with no explaination. This may be due to Bitmex's trading engine experiencing an overload and sheading some requests. Recommended retry after 500 milliseconds."
        else:
            self.message = message