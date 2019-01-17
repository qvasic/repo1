#ifndef CALLABLESIGNAL_H_SA0DF89HAS0DF8H7AS0DF87HASDFSJKDHFSODIF
#define CALLABLESIGNAL_H_SA0DF89HAS0DF8H7AS0DF87HASDFSJKDHFSODIF

class CallableSignal
{
public:
    CallableSignal( );

    void set( );
    void operator( )( );

    void reset( );

    bool is_set( ) const;
    explicit operator bool( ) const;

private:
    bool m_set;
};

#endif // CALLABLESIGNAL_H_SA0DF89HAS0DF8H7AS0DF87HASDFSJKDHFSODIF
