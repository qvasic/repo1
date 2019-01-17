#ifndef FUNC_H
#define FUNC_H

#include <memory>

namespace q
{

class bad_func_call
{
};

template <typename R, typename A>
class func
{
public:
    func( ) = default;

    template <typename T>
    explicit func( T&& function_object )
        : contained_function_object(
              new function_object_container< T >( std::forward<T>( function_object ) ) )
    {
    }

    func( const func& r );
    func( func&& r ) = default;

    func& operator=( const func& r );
    func& operator=( func&& r ) = default;

    template <typename T>
    func& operator=( T&& function_object );

    ~func( ) = default;

    R operator( )( const A& arg )
    {
        if ( !contained_function_object )
        {
            throw bad_func_call( );
        }

        return contained_function_object->operator( )( arg );
    }

    explicit operator bool( ) const
    {
        return static_cast< bool >( contained_function_object );
    }

private:
    struct function_object_container_interface
    {
        virtual R operator( )( A arg ) = 0;
        virtual ~function_object_container_interface( ) = default;
    };

    template <typename T>
    struct function_object_container : public function_object_container_interface
    {
        function_object_container( const T& t )
            : object( t )
        {}

        ~function_object_container( ) = default;

        R operator( )( A arg ) override
        {
            return object( arg );
        }

        T object;
    };

private:
    std::unique_ptr< function_object_container_interface > contained_function_object;
};

}

#endif // FUNC_H
