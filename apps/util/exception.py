class AuthException(Exception):
    def __init__(self, message):
        self.message = message
        self.status = 401

    def __str__(self):
        return self.message