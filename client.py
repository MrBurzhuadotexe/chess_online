import socket

def main():
    server_address = ('127.0.0.1', 8084)  # Server address and port

    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(server_address)
        print("Connected to the server.")

        while True:
            # Send message
            message = input("Enter message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            sock.sendall(message.encode())  # Send message to the server

            # Receive response
            response = sock.recv(1024).decode()  # Receive message from the server
            if not response:
                print("Server closed the connection.")
                break
            print("Received from the other client: ", response)

    except Exception as e:
        print("Connection error: ", e)
    finally:
        sock.close()  # Close socket when done

if __name__ == "__main__":
    main()