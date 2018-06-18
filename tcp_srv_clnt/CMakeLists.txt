cmake_minimum_required( VERSION 2.6 )
project( tcp_srv_clnt )

configure_file( clnt.py clnt.py COPYONLY )
configure_file( srv.py srv.py COPYONLY )

set( CMAKE_CXX_FLAGS "--std=c++11" )
add_executable( srv srv.cpp common.h )
add_executable( clnt clnt.cpp common.h )
