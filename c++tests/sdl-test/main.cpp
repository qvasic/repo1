#include "SDL2/SDL.h"

#include <chrono>
#include <iostream>
#include <iomanip>
#include <thread>
#include <cstring>

std::string
haptics_to_string( unsigned int haptic_effects )
{
    struct HapticEffectName
    {
        const char* name;
        unsigned int mask;
    };

    HapticEffectName effect_names[] = {
        { "SDL_HAPTIC_CONSTANT", SDL_HAPTIC_CONSTANT },
        { "SDL_HAPTIC_SINE", SDL_HAPTIC_SINE },
        { "SDL_HAPTIC_LEFTRIGHT", SDL_HAPTIC_LEFTRIGHT },
        { "SDL_HAPTIC_TRIANGLE", SDL_HAPTIC_TRIANGLE },
        { "SDL_HAPTIC_SAWTOOTHUP", SDL_HAPTIC_SAWTOOTHUP },
        { "SDL_HAPTIC_SAWTOOTHDOWN", SDL_HAPTIC_SAWTOOTHDOWN },
        { "SDL_HAPTIC_RAMP", SDL_HAPTIC_RAMP },
        { "SDL_HAPTIC_SPRING", SDL_HAPTIC_SPRING },
        { "SDL_HAPTIC_DAMPER", SDL_HAPTIC_DAMPER },
        { "SDL_HAPTIC_INERTIA", SDL_HAPTIC_INERTIA },
        { "SDL_HAPTIC_FRICTION", SDL_HAPTIC_FRICTION },
        { "SDL_HAPTIC_CUSTOM", SDL_HAPTIC_CUSTOM },
        { "SDL_HAPTIC_GAIN", SDL_HAPTIC_GAIN },
        { "SDL_HAPTIC_AUTOCENTER", SDL_HAPTIC_AUTOCENTER },
        { "SDL_HAPTIC_STATUS", SDL_HAPTIC_STATUS },
        { "SDL_HAPTIC_PAUSE", SDL_HAPTIC_PAUSE },
    };

    std::string names;

    for ( int i = 0; i < sizeof( effect_names ) / sizeof( effect_names[0] ); ++i )
    {
        if ( effect_names[i].mask & haptic_effects )
        {
            names += std::string( effect_names[i].name ) + " ";
        }
    }

    return names;
}

void
show_haptic_stats( )
{
    auto haptics_count = SDL_NumHaptics( );

    std::cout << "there are " << haptics_count << " haptic device(s) in the system" << std::endl;

    for ( auto i = 0; i < haptics_count; ++i )
    {
        SDL_Haptic* haptic = SDL_HapticOpen( i );

        if ( haptic == nullptr )
        {
            std::cerr << "couldn't open haptic " << i << ": " << SDL_GetError( ) << std::endl;
            continue;
        }

        auto haptic_effects = SDL_HapticQuery( haptic );
        printf( "haptic device opened: %s, effects: 0x%x, which are: %s\n",
                SDL_HapticName( i ), haptic_effects, haptics_to_string( haptic_effects ).c_str( ) );

        SDL_HAPTIC_CONSTANT;

        SDL_HapticClose( haptic );
    }
}

SDL_HapticPeriodic
init_haptic_sine_effect( )
{
    SDL_HapticPeriodic periodic;

    SDL_memset( &periodic, '\0', sizeof( periodic ) ); // 0 is safe default
    periodic.type = SDL_HAPTIC_SINE;
    periodic.direction.type = SDL_HAPTIC_POLAR; // Polar coordinates
    periodic.direction.dir[0] = 18000; // Force comes from south
    periodic.period = 1000; // 1000 ms
    periodic.magnitude = 20000; // 20000/32767 strength
    periodic.length = 5000; // 5 seconds long
    periodic.attack_length = 1000; // Takes 1 second to get max strength
    periodic.fade_length = 1000; // Takes 1 second to fade away

    return periodic;
}

SDL_HapticEffect
init_haptic_friction_effect( )
{
    SDL_HapticEffect effect;
    memset( &effect, '\0', sizeof( effect ) );

    effect.type = SDL_HAPTIC_FRICTION;
    // effect.condition.direction; // not used for friction
    effect.condition.length = 1000;
    effect.condition.delay = 50;

    effect.condition.button = 0;
    effect.condition.interval = 0;

    effect.condition.right_sat[0] = 0xffff;
    effect.condition.right_sat[1] = 0xffff;
    effect.condition.right_sat[2] = 0xffff;

    effect.condition.left_sat[0] = 0xffff;
    effect.condition.left_sat[1] = 0xffff;
    effect.condition.left_sat[2] = 0xffff;

    effect.condition.right_coeff[0] = 0x7fff;
    effect.condition.right_coeff[1] = 0x7fff;
    effect.condition.right_coeff[2] = 0x7fff;

    effect.condition.left_coeff[0] = 0x7fff;
    effect.condition.left_coeff[1] = 0x7fff;
    effect.condition.left_coeff[2] = 0x7fff;

    effect.condition.deadband[0] = 0;
    effect.condition.deadband[1] = 0;
    effect.condition.deadband[2] = 0;

    effect.condition.center[0] = 0;
    effect.condition.center[1] = 0;
    effect.condition.center[2] = 0;

    return effect;
}

void
play_haptic_effects( int number )
{
    SDL_Haptic* haptic = SDL_HapticOpen( number );

    if ( haptic == nullptr )
    {
        std::cerr << "couldn't open haptic " << number << ": " << SDL_GetError( ) << std::endl;
        return;
    }
    std::cout << "haptic device opened" << std::endl;


    /*if ( SDL_HapticStopAll( haptic ) < 0 )
    {
        std::cerr << "couldn't stop all: " << SDL_GetError( ) << std::endl;
    }*/

    /*int effects_count = SDL_HapticNumEffects( haptic );
    std::cout << "haptic num of effects: " << effects_count << std::endl;
    std::cout << "haptic num of effects running: "
              << SDL_HapticNumEffectsPlaying( haptic ) << std::endl;

    std::this_thread::sleep_for( std::chrono::seconds( 5 ) );*/
    /*for ( int i = 0; i < effects_count; ++i )
    {
        if ( SDL_HapticRunEffect( haptic, i, 1 ) < 0 )
        {
            std::cout << "couldn't play effect #" << i << ": " << SDL_GetError( ) << std::endl;
        }
    }*/

    /*if ( SDL_HapticRunEffect( haptic, 100, 1 ) < 0 )
    {
        std::cout << "couldn't play effect: " << SDL_GetError( ) << std::endl;
    }
    else
    {
        std::this_thread::sleep_for( std::chrono::seconds( 3 ) );
    }*/

    /*SDL_HapticEffect effect = init_haptic_friction_effect( );
    // effect.type = SDL_HAPTIC_SINE;
    // effect.periodic = init_haptic_sine_effect( );

    auto effect_id = 0;
    if ( SDL_HapticUpdateEffect( haptic, effect_id, &effect ) < 0 )
    {
        std::cerr << "couldn't update effect: " << SDL_GetError( ) << std::endl;
    }
    else
    {
        SDL_HapticRunEffect( haptic, effect_id, 1 );
        std::this_thread::sleep_for( std::chrono::seconds( 3 ) );
        SDL_HapticDestroyEffect( haptic, effect_id );
    }*/

    /*if ( SDL_HapticSetAutocenter( haptic, 10 ) < 0 )
    {
        std::cerr << "couldn't set auto center: " << SDL_GetError( ) << std::endl;
    }

    if ( SDL_HapticSetGain( haptic, 100 ) < 0 )
    {
        std::cerr << "couldn't set gain: " << SDL_GetError( ) << std::endl;
    }*/

    std::this_thread::sleep_for( std::chrono::seconds( 10 ) );

    SDL_HapticClose( haptic );
    std::cout << "haptic device closed" << std::endl;
}

void
show_joystick_stats( )
{
    int joystick_count = SDL_NumJoysticks( );

    if ( SDL_NumJoysticks( ) < 1 )
    {
        std::cerr << "no joystick present in the system to show" << std::endl;
        return;
    }

    std::cout << "there are " << joystick_count << " joystick(s) present: " << std::endl;
    for ( int i = 0; i < joystick_count; ++i )
    {
        std::cout << i+1 << " " << SDL_JoystickNameForIndex( i ) << std::endl;
    }
}

void
show_joystick_axes( int number )
{
    SDL_Joystick* joystick = SDL_JoystickOpen( number );

    if ( joystick == nullptr )
    {
        std::cerr << "couldn't open joystick" << std::endl;
        return;
    }

    int axes_count = SDL_JoystickNumAxes( joystick );
    std::cout << "opened joystick " << SDL_JoystickName( joystick )
              << ", it has " << axes_count << " axes" << std::endl;

    bool exit_event = false;
    for ( ; !exit_event; )
    {
        SDL_Event event;
        while ( SDL_PollEvent( &event ) )
        {
            if ( event.type == SDL_JOYBUTTONDOWN )
            {
                exit_event = true;
            }
        }

        std::cout << "\raxes: " << std::setprecision( 2 );
        for ( int i=0; i < axes_count; ++i )
        {
            std::cout << SDL_JoystickGetAxis( joystick, i ) / double( 0xefff ) << ' ';
        }
        std::cout << "      ";

        std::this_thread::sleep_for( std::chrono::milliseconds( 50 ) );
    }

    SDL_JoystickClose( joystick );
}

int
main( int, char** )
{
    if ( SDL_Init( SDL_INIT_EVERYTHING ) < 0 )
    {
        std::cout << "COULDN'T INIT SDL: " << SDL_GetError( ) << std::endl;
        return -1;
    }

    show_haptic_stats( );
    show_joystick_stats( );


    SDL_Haptic* haptic = SDL_HapticOpen( 0 );
    SDL_HapticNumEffects( haptic );
    show_joystick_axes( 1 );
    SDL_HapticClose( haptic );

    play_haptic_effects( 0 );
    //play_haptic_effects( 0 );

    SDL_Quit( );
}
