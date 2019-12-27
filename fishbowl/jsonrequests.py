import json

from .xmlrequests import BaseRequest


class Request(BaseRequest):
    def __init__(self, key=""):
        super().__init__(key=key)
        self.root = {"FbiJson": {"Ticket": {"Key": key}, "FbiMsgsRq": {}}}

    @property
    def request(self):
        import json

        return json.dumps(self.root)

    def add_data(self, data):
        self.root["FbiJson"]["FbiMsgsRq"] = data


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
            ianame = "{} ({})".format(ianame, task_name)
            iadescription = "{} ({} task)".format(iadescription, task_name)
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
            self.add_data({"LogoutRq": ""})
        else:
            self.add_data({"LoginRq": data})


class SimpleJSONRequest(Request):
    def __init__(self, request_name, value=None, key=""):
        super().__init__(key)
        el = self.add_request_element(request_name)
        if value is not None:
            if isinstance(value, dict):
                self.add_elements(el, value)
            else:
                el.text = str(value)
