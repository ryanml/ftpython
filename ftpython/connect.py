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
        # Return false if an invalid hostname has been given
        try:
            self.host = socket.gethostbyname(host)
        except socket.gaierror:
            return False
        # Connect to given host on port
        self.server.connect((self.host, self.PORT))
        # Set socket timeout to 15 seconds
        self.server.settimeout(15)
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

    def get_response(self, *no_print):
        """
        Receives response from server, prints and returns the parsed result
        """
        try:
            response = self.server.recv(4096)
            if not no_print:
                print response
            return self.parse_response(response)
        except socket.timeout:
            print "Timeout error, connection closed"
            self.f_close()

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

    def create_pasv_con(self):
        """
        Given a response from an issued PASV command, creates a connection
        to the specified host and port.
        """
        # Issue PASV command
        self.send_request('PASV')
        response = self.get_response()
        # Return False if there is no response
        if not response:
            return False
        # Get the host and port parameters from the response
        params = response['message'].split('(')[1].split(')')[0].split(',')
        file_port = (int(params[4]) * 256) + int(params[5])
        # Set up socket connection and connect it
        file_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_con.connect((self.host, file_port))
        # Return connection
        return file_con
