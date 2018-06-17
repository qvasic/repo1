#include <arpa/inet.h>
#include <netinet/ip.h>
#include <unistd.h>

#include <cstring>
#include <iostream>
#include <thread>
#include <chrono>

#include "common.h"

int connect_and_send_data()
{
    int ret = 0;

    auto tcp_socket = socket( AF_INET, SOCK_STREAM, 0 );
    if( tcp_socket == -1 )
    {
        std::cerr << "couldn't open socket, errno=" << errno << std::endl;
        ret = 1;
    }
    else
    {
        /*sockaddr_in addr = { AF_INET, htons( 10489 ), INADDR_ANY };
        inet_aton( "192.168.1.33", &addr.sin_addr );

        if( bind( tcp_socket, reinterpret_cast<sockaddr*>(&addr), sizeof( addr ) ) == -1 )
        {
            std::cerr << "couldn't bind socket, errno=" << errno << std::endl;
            ret = 1;
        }
        else*/

        {
            sockaddr_in srv_addr = {AF_INET, htons( 10443 ), INADDR_ANY };
            inet_aton( "127.0.0.1", &srv_addr.sin_addr );

            if( connect( tcp_socket, reinterpret_cast<sockaddr*>(&srv_addr), sizeof( srv_addr ) ) == -1 )
            {
                std::cerr << "couldn't connect, errno=" << errno << std::endl;
                ret = 1;
            }
            else
            {
                std::cout << "successfully connected, sending countdown... " << std::endl;
                constexpr int buffer_size = 20;
                char countdown_buffer[buffer_size] = "";
                for( int i=0; i<20; i++ )
                {
                    snprintf( countdown_buffer, buffer_size, "%d\n", i );
                    write( tcp_socket, countdown_buffer, strlen( countdown_buffer ) );
                    std::this_thread::sleep_for( std::chrono::seconds(1) );
                }

            }
        }
        close( tcp_socket );
    }

    return ret;
}

int main( int argc, char *argv[] )
{
    int ret = 0;

    ret = connect_and_send_data( );

    return ret;
}
