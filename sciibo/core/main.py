import curses
import getpass
import time


def mainloop(screen):
    from sciibo.core.state import State

    # Get username from environment
    try:
        env_user = getpass.getuser()
    except KeyError:
        env_user = ''

    # Create a new state
    state = State()
    state.set_name(env_user)
    state.set_scene('Main')

    try:
        while state.running:
            # Handle key and mouse input
            ch = screen.get_key()
            while ch:
                if ch == curses.KEY_MOUSE:
                    result = screen.get_mouse(state.scene)
                    if result:
                        state.scene.on_mouse(*result)
                else:
                    state.scene.on_key(ch)

                # Handle all key presses in queue
                ch = screen.get_key()

            # Register frame tick
            state.scene.on_tick()

            # Update the screen
            screen.update(state.scene)
            time.sleep(1.0 / 24)

    except KeyboardInterrupt:
        state.quit()

    except Exception:
        # Make sure threads are stopped when an exception is encountered
        state.quit()

        # Re-raise exception so screen can be terminated
        # before displaying exception in console
        raise
