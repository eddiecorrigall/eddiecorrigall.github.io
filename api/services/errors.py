class ServiceError(Exception):
    pass

class NotFoundError(ServiceError):
    pass

class TooManyRequestsError(ServiceError):
    pass
