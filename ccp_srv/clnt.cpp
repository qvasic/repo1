#include <iostream>
#include <boost/asio.hpp>

int main( int argc, char* argv[] )
{
    if ( argc != 2 )
    {
        std::cerr << "usage: " << argv[0] << " <server addr>" << std::endl;
        return 1;
    }

    boost::asio::io_service io_service;

    using boost::asio::ip::tcp;

    tcp::resolver resolver( io_service );
    tcp::resolver::query query( argv[1], "2222" );
    auto endpoint_iter = resolver.resolve( query );

    tcp::socket socket( io_service );
    boost::asio::connect( socket, endpoint_iter );

    char character;
    auto buffer = boost::asio::buffer( &character, 1 );

    boost::system::error_code error;
    for (;;)
    {
        socket.read_some( buffer, error );
        if ( error == boost::asio::error::eof )
        {
            break;
        }
        else if ( error )
        {
            std::cout << "error reading from server: " << error << ", disconnecting" << std::endl;
            break;
        }
        std::cout << character;
    }

    return 0;
}
