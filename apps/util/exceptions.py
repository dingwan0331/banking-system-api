class AuthException(Exception):
    def __init__(self, message):
        self.message   = message
        self.status    = 401
        self.is_custom = True

    def __str__(self):
        return self.message

class BadRequestException(Exception):
    def __init__(self, message):
        self.message   = message
        self.status    = 400
        self.is_custom = True

    def __str__(self):
        return self.message

class PermissionException(Exception):
    def __init__(self, message):
        self.message   = message
        self.status    = 403
        self.is_custom = True

    def __str__(self):
        return self.message