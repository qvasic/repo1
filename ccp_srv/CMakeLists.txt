cmake_minimum_required( VERSION 2.8 )
project( ccp_srv )

if( WIN32 )
    set( BOOST_VER "1_59" )
    set( BOOST_DIR "d:\\boost\\boost_${BOOST_VER}_0" )

    include_directories( ${BOOST_DIR} )
    link_directories( "${BOOST_DIR}\\stage\\lib\\" )
    set( LINK_LIBS "libboost_system-vc140-mt-gd-${BOOST_VER}.lib" )
else( )
    set( CMAKE_CXX_FLAGS "--std=c++11" )
    link_directories( "/usr/lib/x86_64-linux-gnu/" )
    set( LINK_LIBS "boost_system boost_thread" )
endif( )

add_executable( srv_file srv_file.cpp ccp_server.cpp ccp_server.h )
target_link_libraries( srv_file ${BOOST_LIBS} )

add_executable( clnt clnt.cpp )
target_link_libraries( clnt ${LINK_LIBS} )
