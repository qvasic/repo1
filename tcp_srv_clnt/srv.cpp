#include <arpa/inet.h>
#include <netinet/ip.h>
#include <unistd.h>
#include <iostream>

#include "common.h"

int main()
{
    int ret = 0;
    int default_port = 10443;

    auto tcp_socket = socket( AF_INET, SOCK_STREAM, 0 );
    if( tcp_socket == -1 )
    {
        std::cerr << "couldn't open socket, errno=" << errno << std::endl;
        ret = 1;
    }
    else
    {
        sockaddr_in addr = { AF_INET, htons( default_port ), INADDR_ANY };
        //inet_aton( "127.0.0.1", &addr.sin_addr );

        if( bind( tcp_socket, reinterpret_cast<sockaddr*>(&addr), sizeof( addr ) ) == -1 )
        {
            std::cerr << "couldn't bind socket, errno=" << errno << std::endl;
            ret = 1;
        }
        else
        {
            if( listen( tcp_socket, 0 ) == -1 )
            {
                std::cerr << "could'n set socket to listen, errno=" << errno << std::endl;
                ret = 1;
            }
            else
            {
                std::cout << "socket successfully opened, bound to port " << ntohs( addr.sin_port )
                          << " and set to listen" << std::endl;

                while( ret == 0 )
                {
                    sockaddr_in peer;
                    socklen_t addr_len = sizeof( peer );

                    std::cout << "accepting incoming connections" << std::endl;

                    auto connected_socket = accept( tcp_socket, reinterpret_cast<sockaddr*>(&peer),
                                                    &addr_len );
                    if( connected_socket == -1 )
                    {
                        std::cerr << "couldn't accept connection, errno=" << errno << std::endl;
                        ret = 1;
                    }
                    else
                    {
                        std::cout << "connected with " << peer.sin_addr << '/' << ntohs( peer.sin_port ) << std::endl;
                        char c;
                        while( read( connected_socket, &c, 1 ) )
                        {
                            std::cout << c;
                        }
                        close( connected_socket );
                        std::cout << "connection closed" << std::endl;
                    }
                }
            }

        }
        close( tcp_socket );
    }

    return ret;
}
