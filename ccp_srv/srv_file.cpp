#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <boost/asio.hpp>

#include "ccp_server.h"

int main( )
{
    CCPServer ccp_server;

    std::cout << "starting server, type \"exit\" and press ENTER to stop it "
                 "and exit" << std::endl;

    ccp_server.start( );

    for (;;)
    {
        std::string command;
        std::cin >> command;
        if ( command == "exit" )
        {
            break;
        }
    }

    std::cout << "stopping server and exiting" << std::endl;
    ccp_server.stop( );

    /*int i=0;

    using boost::asio::ip::tcp;

    boost::asio::io_service io_service;

    tcp::acceptor acceptor( io_service, tcp::endpoint( tcp::v4( ), 2222 ) );
    for (;;)
    {
        tcp::socket socket( io_service );

        std::cout << "waiting for a client to connect..." << std::endl;

        acceptor.accept( socket );

        std::cout << "new connection from " << socket.remote_endpoint( )
                  << ", sending stuff over" << std::endl;

        boost::system::error_code error;
        while( !error )
        {
            std::string num = std::to_string( i ) + " ";
            socket.write_some( boost::asio::buffer( num ), error );
            ++i;
            std::this_thread::sleep_for( std::chrono::seconds( 1 ) );
        }

        std::cout << "connection is closed, error=" << error << std::endl;

    }*/

    return 0;
}
