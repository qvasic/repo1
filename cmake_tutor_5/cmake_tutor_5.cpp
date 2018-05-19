#include <iostream>

extern double sqrt_table[];

int main()
{
    using std::cout; using std::endl;
    cout << "hello" << endl;

    int i = 0;
    double *p = sqrt_table;
    std::cout << "sqrt(" << i << ")=" << *p << std::endl;
    i++, p++;
    while( *p != 0 )
    {
        std::cout << "sqrt(" << i << ")=" << *p << std::endl;
        i++, p++;
    }

    return 0;
}
