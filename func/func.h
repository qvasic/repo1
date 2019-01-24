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
    explicit func( const T& function_object )
        : contained_function_object(
              new function_object_container< T >( function_object ) )
    {
    }

    func( const func& r )
    {
        if ( r.contained_function_object )
        {
            contained_function_object = r.contained_function_object->make_copy( );
        }
    }

    func( func&& r ) = default;

    func& operator=( const func& r )
    {
        if ( this == &r )
        {
            return *this;
        }

        if ( !r.contained_function_object )
        {
            contained_function_object = nullptr;
        }

        contained_function_object = r.contained_function_object->make_copy( );

        return *this;
    }

    func& operator=( func&& r ) = default;

    template <typename T>
    func& operator=( const T& function_object );

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
        virtual std::unique_ptr< function_object_container_interface >
            make_copy( ) const = 0;
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

        std::unique_ptr< function_object_container_interface >
            make_copy( ) const override
        {
            return std::unique_ptr< function_object_container_interface >(
                        new function_object_container( object ) );
        }

        T object;
    };

private:
    std::unique_ptr< function_object_container_interface > contained_function_object;
};

}

#endif // FUNC_H
