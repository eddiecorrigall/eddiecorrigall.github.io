class DAOError(Exception):
    pass

class TooManyRequestsError(DAOError):
    pass

class NotFoundError(DAOError):
    pass
