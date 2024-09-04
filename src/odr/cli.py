import os
import sys

from .args import parse_argv


RC_FILENAME_ENV_VAR_NAME = "ODR_CONFIG"
RC_DEFAULT_FILENAME = "odrrc"


def get_rc_filename():
    """
    Get default config file path

    In order of precedence: $ODR_CONFIG > $XDG_CONFIG_HOME/odrrc > ~/.config/odrrc > ~/.odrrc
    """
    from_env = os.environ.get(RC_FILENAME_ENV_VAR_NAME)
    if from_env:
        return from_env
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        res = os.path.join(xdg_config_home, RC_DEFAULT_FILENAME)
    else:
        res = os.path.join(os.path.expanduser("~"), ".config", RC_DEFAULT_FILENAME)
    if os.path.exists(res):
        return res
    res = os.path.join(os.path.expanduser("~"), f".{RC_DEFAULT_FILENAME}")
    if not os.path.exists(res):
        return None
    return res


def get_exec_args(args):
    """Format args into an list to pass to execvp"""
    return [
        args.container_command,
        "run",
        *args.run_option_args,
        args.image_tag,
        *args.command,
    ]


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]
    rc_filename = get_rc_filename()
    args = parse_argv(argv, rc_filename)
    exec_args = get_exec_args(args)
    if args.verbose:
        print(" ".join(exec_args))
    os.execvp(args.container_command, exec_args)
