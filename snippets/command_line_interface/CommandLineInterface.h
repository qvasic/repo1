#pragma once

#include <string>
#include <mutex>
#include <vector>

/*

  Simple command line interface.
  It is portable and thread-safe - relying only on C++11.

  It has a status line, every status line update will be printed on the same line, so it is
  suitable for showing progress status, distance to next maneuver, etc. Things that change often
  and you do not want to flood user with messages about every small change. Use set_status( ... )
  to update status line.

  If you really want to make user aware of something - use print_message( ... ). It will print
  a message on a separate line. It is suitable for more important events - calculation completion,
  passage of a turn, errors and warnings.

  Both set_status( ... ) and print_message( ... ) are thread-safe, you can call them
  from any thread.

  When you want to receive input from user - use wait_for_next_command( ). Unlike previous methods,
  this one is not thread-safe - call it only from one thread - UI thread. Once you called it,
  it will wait until user presses ENTER. Until then status line may be updated and messages printed.
  But once user pressed ENTER, status updates and new messages will not printed until whole input
  operation is done - there is no protable way to print something and allow user input at
  the same time.
  So, user presses ENTER, output is blocked, prompt is printed, and the sysem waits for user
  to enter a command and press ENTER one more time. Entered command is returned from
  wait_for_next_command( ), and unprinted messages and status updates are finally printed.

*/

namespace vdem
{

class CommandLineInterface
{
public:
    CommandLineInterface( const std::string& prompt = "> ", int status_length = 80 );

    CommandLineInterface( const CommandLineInterface& ) = delete;
    CommandLineInterface& operator=( const CommandLineInterface& ) = delete;

    CommandLineInterface( CommandLineInterface&& ) = default;
    CommandLineInterface& operator=( CommandLineInterface&& ) = default;

    ~CommandLineInterface( );

    void set_status( const std::string& status );
    void print_message( const std::string& message );
    std::string wait_for_next_command( );

private:
    void clear_status_line( );
    void update_status_on_screen( const std::string& status );
    void print_unprinted_messages_and_clear( );

private:
    int m_status_length;
    std::string m_blank_line;
    std::string m_prompt;

    std::mutex m_io_mutex;

    std::mutex m_data_mutex;
    std::string m_last_status;
    std::vector< std::string > m_unprinted_messages;
};

} // namespace vdem
