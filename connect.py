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
        response = self.wait_for_response()
        if response['code'] == '220':
            self.connected = True

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

    def wait_for_response(self):
        """
        Waits for the next response from the server, returns it
        """
        found_response = False
        s_file = self.server.makefile('rb')
        while not found_response:
            for line in s_file:
                found_response = True
                print line
                s_file.close()
                return self.parse_response(line)

    def parse_response(self, response):
        """
        Returns a dictionary with the 3 digit response code and message
        """
        code = response[:3]
        message = response[3:]
        return {
           'code': code,
           'message': message
        }
