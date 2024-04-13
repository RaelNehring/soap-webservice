from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Integer, String
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from wsgiref.simple_server import make_server

class CalculatorService(ServiceBase):
    @rpc(Integer, Integer, String, _returns=float)
    def calculate(ctx, value1, value2, operation):
        if operation == '+':
            return value1 + value2
        elif operation == '-':
            return value1 - value2
        elif operation == '*':
            return value1 * value2
        elif operation == '/':
            if value2 == 0:
                return 0.0  # Retorno 0.0 para evitar divisão por zero
            return value1 / value2
        else:
            raise ValueError("Operação não suportada")

application = Application([CalculatorService], 'soap.calculator',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

class CorsMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'))
            headers.append(('Access-Control-Allow-Headers', 'Content-Type,SOAPAction'))
            return start_response(status, headers, exc_info)

        if environ['REQUEST_METHOD'] == 'OPTIONS':
            custom_start_response('200 OK', [])
            return []

        return self.app(environ, custom_start_response)

wsgi_app = WsgiApplication(application)
wsgi_app_with_cors = CorsMiddleware(wsgi_app)

server = make_server('0.0.0.0', 8000, wsgi_app_with_cors)
server.serve_forever()
