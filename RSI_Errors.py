from colorama import init, deinit, Fore, Back, Style

class RSI_Generic_Error(Exception):
    """
    Base class for exceptions in the RSI_Script.
    
    Attributes:
        message -- Explanation of why the error is being shown.
    """
    def __init__(self, message=None):
      
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "A Generic Error in the RSI Script has been raised, with no explaination."
        else:
            self.message = message
    
    def __str__(self):
        return repr("[X]    "+str(self.__class__.__name__)+": "+self.message)

class HTTP_503_Error(RSI_Generic_Error):
    """
    Error to handle HTTP 503 responses from the Bitmex client. Subclass of RSI_Generic_Error.
    
    Attributes:
        message -- Explanation of why the error is being shown
        http_message -- This is the error details given by the web server.
    """
    # NOTE: "To help improve responsiveness during high-load periods, the BitMEX trading engine will begin load-shedding when requests reach a critical queue depth. When this happens, you will quickly receive a 503 status code with the message "The system is currently overloaded. Please try again later." The request will not have reached the engine, and you should retry after at least 500 milliseconds."

    def __init__(self, message=None, http_message=None):
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "An HTTP 503 has been raised, with no explaination. This may be due to Bitmex's trading engine experiencing an overload and sheading some requests. Recommended retry after 500 milliseconds."
        else:
            self.message = message

        # Set http_message to the one provided, else provide a default one.
        if not http_message:
            self.http_message = "No details from the HTTP 503 response were provided to this error."
        else:
            self.http_message = http_message
    
    def __str__(self):
        return repr("[X]    "+str(self.__class__.__name__)+": "+self.message+"HTTP Message: "+self.http_message)

class HTTP_400_Error(RSI_Generic_Error):
    """
    Error to handle HTTP 400 responses from the Bitmex client. Subclass of RSI_Generic_Error.
    
    Attributes:
        message -- Explanation of why the error is being shown
        http_message -- This is the error details given by the web server.
    """
    # Accoring to the API Explorer, Trad, 400 is used for Parameter Error.

    def __init__(self, message=None, http_message=None):
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "An HTTP 400 has been raised, with no explaination. This may be due to a Parameter Error."
        else:
            self.message = message

        # Set http_message to the one provided, else provide a default one.
        if not http_message:
            self.http_message = "No details from the HTTP 400 response were provided to this error."
        else:
            self.http_message = http_message
    
    def __str__(self):
        return repr("[X]    "+str(self.__class__.__name__)+": "+self.message+"HTTP Message: "+self.http_message)

class HTTP_403_Error(RSI_Generic_Error):
    """
    Error to handle HTTP 403 responses from the Bitmex client. Subclass of RSI_Generic_Error.
    
    Attributes:
        message -- Explanation of why the error is being shown
        http_message -- This is the error details given by the web server.
    """
    # Accoring to the API Explorer, Trad, 403 is used for Access Denied.

    def __init__(self, message=None, http_message=None):
        # Set message to the one provided, else provide a default one.
        if not message:
            self.message = "An HTTP 403 has been raised, with no explaination. This may be due to your Access being Denied."
        else:
            self.message = message

        # Set http_message to the one provided, else provide a default one.
        if not http_message:
            self.http_message = "No details from the HTTP 403 response were provided to this error."
        else:
            self.http_message = http_message
    
    def __str__(self):
        return repr("[X]    "+str(self.__class__.__name__)+": "+self.message+"HTTP Message: "+self.http_message)