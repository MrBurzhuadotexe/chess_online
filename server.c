#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define PORT 8080
#define BUF_SIZE 1024

int white_player, black_player; // Sockets for the two clients
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER; // Mutex for synchronization
int turn = 0; // Variable to keep track of whose turn it is (0 for client1, 1 for client2)

void *handle_client(void *socket_desc);

int main() {
    int server_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    int opt = 1; // Option for setsockopt

    // Create socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Set socket options to allow reuse of the address
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR
            , &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Set address information
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Bind the socket to the address and port number
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Start listening for connections
    if (listen(server_fd, 2) < 0) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d\n", PORT);

    // Accept two connections
    white_player = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
    if (white_player < 0) {
        perror("accept");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    printf("First client connected.\n");

    black_player = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
    if (black_player < 0) {
        perror("accept");
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    printf("Second client connected.\n");

    // Create threads to handle communication for each client
    pthread_t thread1, thread2;
    pthread_create(&thread1, NULL, handle_client, (void *)&white_player);
    pthread_create(&thread2, NULL, handle_client, (void *)&black_player);

    // Wait for both threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    close(server_fd);
    return 0;
}

void *handle_client(void *socket_desc) {
    int client_socket = *(int *)socket_desc;
    char buffer[BUF_SIZE];
    int bytes_read;

    while (1) {
        pthread_mutex_lock(&mutex);

        // Check whose turn it is
        if ((client_socket == white_player && turn == 0) ||
            (client_socket == black_player && turn == 1)) {
            // Read message from the client
            memset(buffer, 0, BUF_SIZE);
            bytes_read = read(client_socket, buffer, BUF_SIZE);
            if (bytes_read <= 0) {
                // Client has disconnected
                printf("Client disconnected.\n");
                break;
            }
            printf("Client %d: %s\n", (client_socket == white_player) ? 1 : 2, buffer);

            // Send the message to the other client
            int other_socket = (client_socket == white_player) ? black_player : white_player;
            send(other_socket, buffer, bytes_read, 0);

            // Switch turn
            turn = !turn; // Toggle between 0 and 1
        }

        pthread_mutex_unlock(&mutex);
        usleep(100000); // Sleep for a short time to avoid busy waiting
    }

    close(client_socket);
    pthread_exit(NULL);
}
