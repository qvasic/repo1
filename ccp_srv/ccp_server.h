#ifndef CCP_SERVER_H_SAD0F89HJASD0F89HSADASODUFIHNOISUEHAF0E8F7HSA80EFH7
#define CCP_SERVER_H_SAD0F89HJASD0F89HSADASODUFIHNOISUEHAF0E8F7HSA80EFH7

#include <atomic>
#include <thread>

class CCPServer
{
public:
    struct ccp_type
    {
        double lat;
        double lng;
    };

    void start( );
    void stop( );

    CCPServer( ) = default;

    CCPServer( const CCPServer& ) = delete;
    CCPServer &operator=( const CCPServer& ) = delete;
    CCPServer( CCPServer&& ) = delete;
    CCPServer &operator=( CCPServer&& ) = delete;

    ~CCPServer( );

    void set_ccp( const ccp_type& new_ccp );
    ccp_type get_ccp( ) const;
    void get_ccp( ccp_type& ret_ccp ) const;

private:
    std::atomic< ccp_type > ccp;
    std::atomic< bool > stop_server;
    std::thread server_thread;
    void server_routine( );
};

#endif // CCP_SERVER_H_SAD0F89HJASD0F89HSADASODUFIHNOISUEHAF0E8F7HSA80EFH7
