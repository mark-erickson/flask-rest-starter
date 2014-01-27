allowed_methods = (
    'GET',
    'HEAD',
    'POST',
    'DELETE',
    'PUT',
    'PATCH',
    'OPTIONS'
)
bodyless_methods = ('GET', 'HEAD', 'OPTIONS', 'DELETE')

class CorsHeadersMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Methods', ', '.join(allowed_methods)))
            headers.append(('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept'))
            return start_response(status, headers, exc_info)

        return self.app(environ, cors_start_response)

class HTTPMethodOverrideMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
            if method in bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)