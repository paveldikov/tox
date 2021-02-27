"""Main entry point for tox."""
import logging
import os
import sys
import time
from typing import Optional, Sequence

from tox.config.cli.parse import get_options
from tox.config.main import Config
from tox.provision import provision
from tox.report import HandledError, ToxHandler
from tox.session.state import State


def run(args: Optional[Sequence[str]] = None) -> None:
    try:
        with ToxHandler.patch_thread():
            result = main(sys.argv[1:] if args is None else args)
    except Exception as exception:
        if isinstance(exception, HandledError):
            logging.error("%s| %s", type(exception).__name__, str(exception))
            result = -2
        else:
            raise
    except KeyboardInterrupt:
        result = -2
    finally:
        if "_TOX_SHOW_THREAD" in os.environ:  # pragma: no cover
            import threading  # pragma: no cover

            for thread in threading.enumerate():  # pragma: no cover
                print(thread)  # pragma: no cover
    raise SystemExit(result)


def main(args: Sequence[str]) -> int:
    state = setup_state(args)
    result = provision(state)
    if result is not False:
        return result
    command = state.options.command
    handler = state.cmd_handlers[command]
    result = handler(state)
    return result


def setup_state(args: Sequence[str]) -> State:
    """Setup the state object of this run."""
    start = time.monotonic()
    # parse CLI arguments
    parsed, handlers, pos_args, log_handler = get_options(*args)
    parsed.start = start
    # parse configuration file
    config = Config.make(parsed, pos_args)
    # build tox environment config objects
    state = State(config, (parsed, handlers), args, log_handler)
    return state
