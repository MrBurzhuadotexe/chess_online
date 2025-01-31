#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pthread.h>

#define PORT 8080         // Ustala port serwera
#define BUF_SIZE 1024     // Ustala rozmiar bufora

int white_player, black_player; // Sockets dla dwóch klientów
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER; // Mutex do synchronizacji
int turn = 0; // Zmienna do śledzenia, czyja kolej (0 dla klienta1, 1 dla klienta2)

void *handle_client(void *socket_desc); // Deklaracja funkcji do obsługi klienta

int main() {
    int server_fd; // Deskryptor gniazda serwera
    struct sockaddr_in address; // Struktura adresu
    int addrlen = sizeof(address);
    int opt = 1; // Opcja dla setsockopt

    // Tworzenie deskryptora gniazda
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed"); // Błąd przy tworzeniu gniazda
        exit(EXIT_FAILURE);
    }

    // Ustawienie opcji gniazda, aby zezwolić na ponowne użycie adresu
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt"); // Błąd przy ustawieniu opcji gniazda
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Ustawienie informacji o adresie
    address.sin_family = AF_INET; // Rodzina adresów (IPv4)
    address.sin_addr.s_addr = INADDR_ANY; // Akceptacja połączeń na dowolnym adresie
    address.sin_port = htons(PORT); // Ustawienie portu

    // Powiązanie gniazda z adresem i numerem portu
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed"); // Błąd przy wiązaniu gniazda
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Rozpoczęcie nasłuchiwania połączeń
    if (listen(server_fd, 2) < 0) {
        perror("listen"); // Błąd przy nasłuchiwaniu
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d\n", PORT);

    // Akceptacja dwóch połączeń
    white_player = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
    if (white_player < 0) {
        perror("accept"); // Błąd przy akceptacji połączenia
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    printf("White player connected.\n");
    send(white_player, "w", 1, 0); // Wysyłanie informacji o kolorze

    black_player = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
    if (black_player < 0) {
        perror("accept"); // Błąd przy akceptacji połączenia
        close(server_fd);
        exit(EXIT_FAILURE);
    }
    printf("Black player connected.\n");
    send(black_player, "b", 1, 0); // Wysyłanie informacji o kolorze

    // Tworzenie wątków do obsługi komunikacji z każdym klientem
    pthread_t thread1, thread2;
    pthread_create(&thread1, NULL, handle_client, (void *)&white_player);
    pthread_create(&thread2, NULL, handle_client, (void *)&black_player);

    // Czekanie na zakończenie obu wątków
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    close(server_fd); // Zamknięcie gniazda serwera
    return 0;
}

void *handle_client(void *socket_desc) {
    int client_socket = *(int *)socket_desc; // Deskryptor gniazda klienta
    char buffer[BUF_SIZE]; // Bufor do przechowywania wiadomości
    int bytes_read; // Liczba przeczytanych bajtów

    while (1) {
        pthread_mutex_lock(&mutex); // Zablokowanie mutexu
        // Sprawdzenie, czyja jest kolej
        if ((client_socket == white_player && turn == 0) ||
            (client_socket == black_player && turn == 1)) {
            // Odczytanie wiadomości od klienta
            memset(buffer, 0, BUF_SIZE); // Czyszczenie bufora
            bytes_read = read(client_socket, buffer, BUF_SIZE); // Odczyt danych z gniazda
            if (bytes_read <= 0) {
                // Klient się rozłączył
                printf("Client disconnected.\n");
                close(white_player); // Zamknięcie połączenia z białym graczem
                close(black_player); // Zamknięcie połączenia z czarnym graczem
                pthread_mutex_unlock(&mutex); // Odblokowanie mutexu
                exit(EXIT_SUCCESS); // Zakończenie programu
            }
            printf("Klient %d: %s\n", (client_socket == white_player) ? 1 : 2, buffer); // Wyświetlenie wiadomości od klienta

            // Wysłanie wiadomości do drugiego klienta
            int other_socket = (client_socket == white_player) ? black_player : white_player; // Określenie, kto jest drugim klientem
            send(other_socket, buffer, bytes_read, 0); // Wysłanie wiadomości

            // Zmiana kolejności
            turn = !turn; // Przełączenie między 0 i 1
        }

        pthread_mutex_unlock(&mutex); // Odblokowanie mutexu
        usleep(100000); // Uśpienie na krótki czas, aby uniknąć zajmowania zbyt wielu zasobów
    }

}
