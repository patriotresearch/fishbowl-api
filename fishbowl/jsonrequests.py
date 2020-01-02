import json

from .xmlrequests import BaseRequest


class Request(BaseRequest):
    def __init__(self, key=""):
        super().__init__(key=key)
        self.root = {"FbiJson": {"Ticket": {"Key": key}, "FbiMsgsRq": {}}}

    @property
    def request(self):
        return json.dumps(self.root)

    def add_data(self, name, data):
        self.root["FbiJson"]["FbiMsgsRq"][name] = data

    def add_request_element(self, name):
        self.root["FbiJson"]["FbiMsgsRq"][name] = None

        return self.root["FbiJson"]["FbiMsgsRq"][name]


class Login(Request):
    key_required = False
    base_iaid = "22"

    def __init__(self, username, password, key="", logout=None, task_name=None):
        super().__init__(key=key)
        iaid = self.base_iaid
        ianame = "PythonApp"
        iadescription = "Connection for Python Wrapper"
        if task_name:
            # Attach the task name to the end of the internal app.
            ianame = f"{ianame} ({task_name})"
            iadescription = f"{iadescription} ({task_name} task)"
            # Make a unique internal app id from the hash of the task name.
            # This uses a namespace of only 100,000 so there is a potential
            # chance of collisions. unperceivable.
            iaid = "{}{:>05d}".format(
                iaid, struct.unpack("i", sha1(task_name.encode("utf-8")).digest()[:4])[0] % 100000,
            )

        data = {
            "IAID": iaid,
            "IAName": ianame,
            "IADescription": iadescription,
            "UserName": username,
            "UserPassword": password,
        }

        if logout:
            self.add_data("LogoutRq", "")
        else:
            self.add_data("LoginRq", data)


class SimpleRequest(Request):
    def __init__(self, request_name, value=None, key=""):
        super().__init__(key)
        el = self.add_request_element(request_name)
        if value is not None:
            if isinstance(value, dict):
                el = value
            else:
                el = str(value)
