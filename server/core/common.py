import json
import logging
import sys

from server.core.models.delayed_tasks import DelayedTask


class LoggingMixin(object):
    """
    Mixin for logging

    Add all class fields _logger and _marker
    """
    _logger = logging.getLogger('core')
    _marker = None
    _LOG_MESSAGE_FORMAT = '%(marker)s:%(method)s:%(message)s'

    def _logging_debug(self, message):
        self._logger.debug(self._logging_message(message))

    def _logging_error(self, message):
        self._logger.error(self._logging_message(message))

    def _logging_info(self, message):
        self._logger.info(self._logging_message(message))

    def _logging_exception(self, message):
        self._logger.exception(self._logging_message(message))

    def _logging_message(self, message):
        return self._LOG_MESSAGE_FORMAT % {'marker': self._marker, 'method': self._fullname_caller(), 'message': message}

    def _fullname_caller(self):
        return self.__module__ + "." + self.__class__.__name__ + "." + sys._getframe(3).f_code.co_name

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DelayedTask):
            return o.values
        return json.JSONEncoder.default(self, o)
