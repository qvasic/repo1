#include <iostream>
#include <vector>

template <typename T>
std::ostream &operator<<( std::ostream &os, const std::vector<T> &vec )
{
    for( const auto &i : vec )
        std::cout << i << ' ';
    return os;
}

void process_test_case()
{
    auto N = 0;
    std::cin >> N;

    std::vector< int > time_avail_table( N, 0 );

    auto previous = 0;
    for( auto n=0; n<N; n++ )
    {
        auto end_time = 0;
        std::cin >> end_time;
        //std::cout << end_time << ' ';
        time_avail_table[n] = end_time - previous;
        previous = end_time;
    }

    //std::cout << std::endl << "time avail: " << time_avail_table << std::endl;

    auto in_time = 0;

    for( auto n=0; n<N; n++ )
    {
        auto time_req = 0;
        std::cin >> time_req;
        if( time_req <= time_avail_table[n] )
            in_time++;
    }

    std::cout << in_time << std::endl;
}

int main()
{
    auto T = 0;

    std::cin >> T;

    for( auto t=0; t<T; t++ )
        process_test_case();

    return 0;
}
