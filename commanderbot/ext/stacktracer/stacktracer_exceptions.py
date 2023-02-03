from commanderbot.lib import ResponsiveException


class StacktracerException(ResponsiveException):
    pass


class LoggingNotConfigured(StacktracerException):
    def __init__(self):
        super().__init__("Global error logging is not configured")


class GuildLoggingNotConfigured(StacktracerException):
    def __init__(self):
        super().__init__("No error logging is configured for this guild")


class TestEventErrors(Exception):
    def __init__(self):
        super().__init__("Testing the error logging configuration for events")


class TestCommandErrors(Exception):
    def __init__(self):
        super().__init__("Testing the error logging configuration for commands")


class TestAppCommandErrors(Exception):
    def __init__(self):
        super().__init__("Testing the error logging configuration for app commands")
