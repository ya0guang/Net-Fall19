#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUF_SIZE 255

int main(int argc, char** argv){

    // usage msg
    if(argc < 2){
        fprintf(stderr, "Usage: %s <server> \n", argv[0]);
        exit(1);
    }

    // prepare parameters for getaddrinfo()

    // for converted from the result->ai_addr, which is a struct sockaddr
    struct sockaddr_in *smtpaddr;
    memset(&smtpaddr, 0, sizeof(struct sockaddr_in));

    struct addrinfo hints;
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = 0;
    hints.ai_family = 0;

    struct addrinfo *result; // store the result of getaddrinfo()
    int getAddr; // store the return value of getaddrinfo()
    
    getAddr = getaddrinfo(argv[1], "smtp", &hints, &result);
    if (getAddr != 0){
        fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(getAddr));
        exit(1);
    }

    // cast to convert sockaddr to sockaddr_in
    smtpaddr = (struct sockaddr_in*) result->ai_addr;

    // print IP address and prot number
    printf("IP address is:%s\nPort number is:%d\n", inet_ntoa(smtpaddr->sin_addr), 
        ntohs(smtpaddr->sin_port));

    // create a socket file discriptor
    int socketsmtp;
    socketsmtp = socket(result->ai_family, result->ai_socktype, result->ai_protocol);

    // bulid connection
    int conn; // to store return value of connect()
    conn = connect(socketsmtp, (struct sockaddr*) smtpaddr, sizeof(struct sockaddr_in));
    if (conn < 0){
        perror("Connect error\n");
        exit(1);
    }

    // read from the socket and print the message
    char buf[BUF_SIZE] = {0};
    int printSize;

    printSize = read(socketsmtp, buf, BUF_SIZE - 1);
    printf("%s", buf);

    // close the socket
    close(socketsmtp);
    
    return 0;

}
