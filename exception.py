from werkzeug.exceptions import HTTPException
from flask import make_response,json



class NotfoundError(HTTPException):
    def __init__(self, status_code,msg):
        self.response = make_response(msg, status_code)


class OtherError(HTTPException):
    def __init__(self, status_code,e_msg, e_code):
        message = {"error_code": e_code,"error_message": e_msg}
        self.response = make_response(json.dumps(message), status_code)

class Succesmsg(HTTPException):
    def __init__(self, status_code,msg):
        self.response = make_response(msg, status_code)