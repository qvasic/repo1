#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <functional>
#include <map>
#include <sstream>

#include <cassert>

namespace vdem
{

class undead_lock_guard
{
public:
    template <typename M>
    undead_lock_guard( M& mutex )
        : m_unlock_routine( [&mutex](){mutex.unlock( );} )
        , m_locked_mutex_ptr( &mutex )
    {
        {
            std::lock_guard< std::mutex > guard( m_common_data_mutex );

            if ( is_deadlocked( std::this_thread::get_id( ), &mutex ) )
            {
                std::cerr << "\n\nDEADLOCK DETECTED\n\n"
                          << std::this_thread::get_id( ) << " tried to lock " << &mutex << "\n"
                          << dump_state( ) << "\n" << std::endl;
                abort( );
            }

            m_waiting_threads[ std::this_thread::get_id( ) ] = &mutex;
        }
        mutex.lock( );
        {
            std::lock_guard< std::mutex > guard( m_common_data_mutex );
            m_waiting_threads.erase( std::this_thread::get_id( ) );
            m_locked_mutexes[ &mutex ] = std::this_thread::get_id( );
        }
    }

    undead_lock_guard( const undead_lock_guard& ) = delete;
    undead_lock_guard& operator=( const undead_lock_guard& ) = delete;

    undead_lock_guard( undead_lock_guard&& r ) = delete;
    undead_lock_guard& operator=( undead_lock_guard&& ) = delete;

    ~undead_lock_guard( )
    {
        m_unlock_routine( );

        std::lock_guard< std::mutex > guard( m_common_data_mutex );
        m_locked_mutexes.erase( m_locked_mutex_ptr );
    }

private:
    static std::string dump_state( );
    static bool is_deadlocked( std::thread::id locking_thread_id, void* mutex_to_lock );

private:
    std::function< void() > m_unlock_routine;
    void* m_locked_mutex_ptr;

    static std::mutex m_common_data_mutex;
    static std::map< void* , std::thread::id > m_locked_mutexes;
    static std::map< std::thread::id, void* > m_waiting_threads;
};

std::mutex undead_lock_guard::m_common_data_mutex;
std::map< void* , std::thread::id > undead_lock_guard::m_locked_mutexes;
std::map< std::thread::id, void* > undead_lock_guard::m_waiting_threads;

std::string
undead_lock_guard::dump_state( )
{
    std::ostringstream oss;

    for ( const auto& lock : m_locked_mutexes )
    {
        oss << lock.first << " was locked by " << lock.second << "\n";
    }
    for ( const auto& wait : m_waiting_threads )
    {
        oss << wait.first << " was waiting for " << wait.second << "\n";
    }

    return oss.str( );
}

bool
undead_lock_guard::is_deadlocked( std::thread::id locking_thread_id, void* mutex_to_lock )
{
    for ( ;; )
    {
        auto locked_mutex_iter = m_locked_mutexes.find( mutex_to_lock );
        if ( locked_mutex_iter != m_locked_mutexes.end( )
             && locked_mutex_iter->second == locking_thread_id )
        {
            return true;
        }

        auto waiting_thread = m_waiting_threads.find( m_locked_mutexes[ mutex_to_lock ] );
        if ( waiting_thread == m_waiting_threads.end( ) )
        {
            return false;
        }

        mutex_to_lock = waiting_thread->second;

        // if this fails - data is corrupt or inconsistent
        assert( m_locked_mutexes.find( mutex_to_lock ) != m_locked_mutexes.end( ) );
    }
}

} // namespace vdem

int main( )
{
    std::mutex m1;
    std::recursive_mutex m2;
    std::mutex m3;

    std::thread t1( [&m1, &m2]()
    {
        vdem::undead_lock_guard lock1( m1 );
        std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );
        vdem::undead_lock_guard lock2( m2 );
        std::this_thread::sleep_for( std::chrono::milliseconds( 2000 ) );
    } );

    std::thread t2( [&m1,&m3]()
    {
        vdem::undead_lock_guard lock3( m3 );
        std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );
        vdem::undead_lock_guard lock1( m1 );
        std::this_thread::sleep_for( std::chrono::milliseconds( 2000 ) );
    } );


    {
        std::cout << "hell" << std::flush;
        vdem::undead_lock_guard lock2( m2 );
        std::this_thread::sleep_for( std::chrono::milliseconds( 100 ) );
        vdem::undead_lock_guard lock3( m3 );
        std::cout << "o" << std::endl;
    }

    t1.join( );
    t2.join( );
}
