class ServerSendModule:
    def __init__(self, clients_list, client_id, server_ip, server_port=6969):
        self.client_id = client_id
        self.server_ip = server_ip
        self.server_port = server_port
        self.clients_list = clients_list

    @staticmethod
    def welcome_message_send(client_id, client_socket, client_address):
        cli_info = f"Client with ip {client_address} and id: {client_id} has connected to the server"

        client_socket.send(bytes(cli_info, 'utf-8'))
