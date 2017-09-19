from httpautotest import httpautotest
from version import VERSION

_version_ = VERSION


class RequestsKeywords(httpautotest):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
