import os
import sys

from args import parse_argv


def get_rc_filename():
    """
    Get default config file path

    In order of precedence: $ODR_CONFIG > $XDG_CONFIG_HOME/odrrc > ~/.config/odrrc > ~/.odrrc
    """
    from_env = os.environ.get("ODR_CONFIG")
    if from_env:
        return from_env
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        res = os.path.join(xdg_config_home, "odrrc")
    else:
        res = os.path.join(os.path.expanduser("~"), ".config", "odrrc")
    if os.path.exists(res):
        return res
    res = os.path.join(os.path.expanduser("~"), ".odrrc")
    if not os.path.exists(res):
        return None
    return res


def get_exec_args(args):
    """Format args into an list to pass to execvp"""
    return [
        args.container_command,
        "run",
        *args.passthrough,
        *args.volume_args,
        *args.port_args,
        *args.env_args,
        args.workdir_arg,
        args.remove_arg,
        args.interactive_arg,
        args.image_tag,
        *args.command,
    ]


def main(argv):
    rc_filename = get_rc_filename()
    args = parse_argv(argv, rc_filename)
    exec_args = get_exec_args(args)
    if args.verbose:
        print(" ".join(exec_args))
    os.execvp(args.container_command, exec_args)


if __name__ == "__main__":
    main(sys.argv[1:])
