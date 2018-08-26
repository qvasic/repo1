#include <iostream>
#include <list>
#include <boost/asio.hpp>

#include "ccp_server.h"

void CCPServer::set_ccp( const ccp_type& new_ccp )
{
    ccp.store( new_ccp );
}

CCPServer::ccp_type CCPServer::get_ccp( ) const
{
    return ccp.load( );
}

void CCPServer::get_ccp( ccp_type &ret_ccp ) const
{
    ret_ccp = ccp.load( );
}

void CCPServer::server_routine( )
{
    std::cout << __func__ << " started" << std::endl;

    using tcp = boost::asio::ip::tcp;

    boost::asio::io_service io_service;
    std::list< tcp::socket > connected_clients;
    tcp::acceptor acceptor( io_service, tcp::endpoint( tcp::v4( ), 2222 ) );

    tcp::socket new_client( io_service );
    tcp::endpoint new_client_endpoint;

    std::function< void ( const boost::system::error_code& ) > new_client_handler =
            [ &new_client, &connected_clients, &acceptor,
              &new_client_endpoint, &new_client_handler ]
            ( const boost::system::error_code& error )
    {
        if( !error )
        {
            std::cout << "new client connected: " << new_client.remote_endpoint( ) << std::endl;
            connected_clients.push_back( std::move( new_client ) );
        }
        else
        {
            std::cout << "could not connect new client: " << error << std::endl;
        }
        acceptor.async_accept( new_client, new_client_endpoint, new_client_handler );
    };

    acceptor.async_accept( new_client, new_client_endpoint, new_client_handler );

    while ( !stop_server )
    {
        io_service.poll( );

        ccp_type ccp_copy = ccp.load( );
        std::string data = std::to_string( ccp_copy.lat ) + " "
                          + std::to_string( ccp_copy.lng ) + "\n";
        auto buffer = boost::asio::buffer( data );

        for ( auto client_iter = connected_clients.begin( );
              client_iter != connected_clients.end( ); )
        {
            boost::system::error_code error;
            client_iter->write_some( buffer, error );
            if( error )
            {
                std::cout << "sending to client " << client_iter->remote_endpoint( )
                          << " resulted in error " << error << ", disconnecting" << std::endl;
                client_iter = connected_clients.erase( client_iter );
            }
            else
            {
                ++client_iter;
            }
        }

        std::this_thread::sleep_for( std::chrono::seconds( 1 ) );
    }
    std::cout << __func__ << " stopped" << std::endl;
}

void CCPServer::start( )
{
    stop_server = false;
    server_thread = std::thread( [this](){ this->server_routine( ); } );
}

void CCPServer::stop( )
{
    stop_server = true;
    if ( server_thread.joinable( ) )
        server_thread.join( );
}

CCPServer::~CCPServer( )
{
    stop( );
}
