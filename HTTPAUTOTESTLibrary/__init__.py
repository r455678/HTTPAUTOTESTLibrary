from .HTTPAUTOTESTLibrary import httpautotest
from .version import VERSION

_version_ = VERSION
class HTTPAUTOTESTLibrary(httpautotest):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'