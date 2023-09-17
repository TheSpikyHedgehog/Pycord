import socket
import threading


try:
    HOST = input("IP Address > ")
    PORT = int(input("Port > "))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    clients = []
    usernames = []
    print("Server is running.")

except Exception:
    print("Server failed to run!")


def broadcast(message):
    for client in clients:
        client.send(message)


def handle_cmds(clients, usernames):
    while True:
        cmd = input("[Server CMD Prompt]>> \n")
        cmd_result = cmd.split(' ')
        if cmd_result[0] == "/kick":
            try:
                client = clients[usernames.index(cmd_result[1])]
                client.close()

            except Exception as exc:
                print(f"[Error] User '{cmd_result[1]}' does not exist")

        if cmd_result[0] == "/broadcast":
            try:
                message = ""
                for i in range(1, len(cmd_result)):
                    message += " " + cmd_result[i]
                message += "\n"

                broadcast(message.encode("utf-8"))
            except Exception as exc:
                print(f"Couldn't broadcast message. Error: {exc}")

        if cmd == "/listall":
            for username in usernames:
                client = clients[usernames.index(username)]
                print(f"Username: {username}  ||   Socket: {client}")
        if cmd == "/help":
            print("---------- Pycord Server-Side Help ----------")
            print(" ------  Commands  ------ \n")
            print("/listall  - Lists all users online.")
            print("/kick <username>  - Removes a user from the chat. Note: The <username> argument does NOT take any spaces")
            print("/help  - Displays help information. ")
            print("/broadcast <message>  - Sends a message to all users. Note: It's usually good to add a '[Server]' tag in front of your message.")
            print("\n")

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            username = usernames[clients.index(client)]
            print(f"{message}")
            broadcast(message)
        except:
            index = clients.index(client)
            username = usernames[index]
            message = f"-- {username} left the chat. -- \n \n".encode("utf-8")
            print(f"{username} left the chat.")
            clients.remove(client)
            client.close()
            broadcast(message)
            usernames.remove(username)
            break


def receive():
    while True:
        thread = threading.Thread(target=handle_cmds, args=(clients, usernames))
        thread.start()
        try:
            client, address = server.accept()
            print(client, address)
            print(f"Client {str(address)} connected to the chat!")
            client.send("NICK".encode("utf-8"))
            username = client.recv(1024).decode("utf-8")
            usernames.append(username)
            clients.append(client)
            print(f"Username of the client address {str(address)} is {username}")
            print(f"{username} joined the chat!")
            joined = f"-- {username} joined the chat! -- \n \n "
            broadcast(joined.encode("utf-8"))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except:
            print(f"Client {address} lost connection.")


if __name__ == "__main__":
    receive()
