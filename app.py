from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Integer, String
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from waitress import serve

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
            # Aplicando cabeçalhos CORS a todas as respostas
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),  # Permite requisições de qualquer origem
                ('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'),  # Especifica métodos permitidos
                ('Access-Control-Allow-Headers', 'Content-Type, SOAPAction'),  # Especifica cabeçalhos permitidos
            ]
            headers.extend(cors_headers)
            return start_response(status, headers, exc_info)

        if environ['REQUEST_METHOD'] == 'OPTIONS':
            # Tratando requisições OPTIONS de forma adequada
            custom_start_response('204 No Content', [])
            return [b'']

        # Inclui tratamento para a rota /status como antes
        if environ['REQUEST_METHOD'] == 'GET' and environ['PATH_INFO'] == '/status':
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b"Service is up and running"]

        # Chama a aplicação com os cabeçalhos CORS adicionados
        return self.app(environ, custom_start_response)

wsgi_app = WsgiApplication(application)
wsgi_app_with_cors = CorsMiddleware(wsgi_app)

serve(wsgi_app_with_cors, host='0.0.0.0', port=8080)
