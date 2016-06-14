import socket

class Connection(object):

    # Default FTP port is 21
    PORT = 21

    def __init__(self):
        """
        Constructor sets connected to false
        """
        self.connected = False

    def f_connect(self, host):
        """
        Connects to server given a host
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(host)
        self.server.connect((self.host, self.PORT))
        response = self.get_response()
        if not response['error']:
            self.connected = True
        return response['code']

    def f_close(self):
        """
        Closes connection to server
        """
        self.server.close()
        self.connected = False

    def send_request(self, request):
        """
        Sends request to server
        """
        request = request.strip()
        self.server.send(request + '\r\n')

    def get_response(self):
        """
        Receives response from server, prints and returns the parsed result
        """
        response = self.server.recv(4096)
        print response
        return self.parse_response(response)

    def parse_response(self, response):
        """
        Returns a dictionary with the 3 digit response code and message
        """
        code = response[:3]
        message = response[3:]
        error = False
        if code[0] == '4' or code[0] == '5':
            error = True
        return {
           'code': code,
           'message': message,
           'error': error
        }