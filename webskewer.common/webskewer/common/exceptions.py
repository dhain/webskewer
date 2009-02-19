class Error(Exception):
    pass

class RequestTooLargeError(Error):
    pass

class HeadersTooLargeError(Error):
    pass

class ChunkTooLargeError(Error):
    pass

class BadChunkSizeError(Error):
    pass

class BadRequestError(Error):
    pass

class BadVersionError(Error):
    pass

class BadHeaderError(Error):
    pass

class BadRangeSpecError(Error):
    pass

class RangePastEOFError(Error):
    pass

class UnimplementedError(Error):
    pass
