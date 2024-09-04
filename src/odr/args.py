import argparse
import os

from getpass import getuser
from itertools import chain, takewhile


class HelpFormatter(argparse.HelpFormatter):
    """Custom HelpFormatter to add passthrough to help text"""

    def format_help(self):
        original_help = super().format_help()
        try:
            options_idx = original_help.index(f"{os.linesep}options:")
        except ValueError:
            # couldn't find options, so just return unchanged
            return original_help
        return (
            original_help[:options_idx]
            + "  passthrough\t\traw arguments for container command\n"
            + original_help[options_idx:]
        )


def _split_argv(argv):
    """Partition list of strings into two iterables before and after \"--\" """
    argv = iter(argv)
    before = takewhile(lambda s: s != "--", argv)
    return before, argv


def _optional_arg(include, value):
    """Use to conditionally include an arg in final result"""
    if include:
        return value
    else:
        return []


def _try_apply_multiverse(args):
    """Set host_src to proper path based on detection of universe/multiverse setup"""
    # TODO: Warn/Error on improper setup?
    version_file_path = os.path.join(args.host_src, args.aliased_version)
    if os.path.exists(version_file_path):
        args.host_src = version_file_path


PARSER_PROG = "odr"

PARSER_ARGUMENTS = {
    "--src": {
        "short_name": "-s",
        "dest": "host_src",
        "type": str,
        "required": True,
        "help": "path to odoo source on host",
    },
    "--user": {
        "short_name": "-u",
        "dest": "host_user_src",
        "type": str,
        "help": "path to user modules on host",
    },
    "--fileshare": {
        "short_name": "-f",
        "dest": "host_fileshare",
        "type": str,
        "default": "odr_fileshare",
        "help": "named volume or path to fileshare on host (default odr_fileshare)",
    },
    "--guest-src": {
        "type": str,
        "default": "/home/odoo/src:ro",
        "help": "path to odoo source on guest (default /home/odoo/src:ro)",
    },
    "--guest-user-src": {
        "type": str,
        "default": "/home/odoo/src/user",
        "help": "path to user modules on guest (default /home/odoo/src/user)",
    },
    "--guest-fileshare": {
        "type": str,
        "default": "/home/odoo/.local/share/Odoo",
        "help": "path to odoo fileshare on guest (default /home/odoo/.local/share/Odoo)",
    },
    "--container-command": {
        "short_name": "-c",
        "type": str,
        "default": "podman",
        "help": "container program to use, e.g. docker or podman (default podman)",
    },
    "--image": {
        "short_name": "-i",
        "type": str,
        "default": "odr",
        "help": "container image name to use (default odr)",
    },
    "--workdir": {
        "short_name": "-w",
        "type": str,
        "help": "workdir for container",
    },
    "--pg-user": {
        "type": str,
        "default": getuser(),
        "help": "PGUSER env variable (default is current user)",
    },
    "--pg-host": {
        "type": str,
        "default": "0.0.0.0",
        "help": "PGHOST env variable (default 0.0.0.0)",
    },
    "--pg-port": {
        "type": str,
        "default": "5432",
        "help": "PGPORT env variable (default 5432)",
    },
    "--pg-pass": {
        "type": str,
        "required": False,
        "help": "PGPASSWORD env variable",
    },
    "--pg-socket": {
        "type": str,
        "default": "/var/run/postgresql",
        "help": "path to pg socket directory, for mounting into container",
    },
    "--pg-use-socket": {
        "short_name": "-t",
        "action": "store_true",
        "default": False,
        "help": "pass to mount and use --pg-socket in container",
    },
    "--server-port": {
        "type": str,
        "default": "8069",
        "help": "port to open for odoo server (default 8069)",
    },
    "--no-server": {
        "action": "store_true",
        "default": False,
        "help": "pass to close server port",
    },
    "--debug-port": {
        "type": str,
        "default": "5678",
        "help": "port to open for debugpy (default 5678)",
    },
    "--debug": {
        "short_name": "-d",
        "action": "store_true",
        "default": False,
        "help": "pass to open debug port (assumed present if --debug-port is provided)",
    },
    "--no-interactive": {
        "action": "store_true",
        "default": False,
        "help": "pass to not run container interactively",
    },
    "--no-remove": {
        "action": "store_true",
        "default": False,
        "help": "pass to not remove the container after running",
    },
    "--verbose": {
        "action": "store_true",
        "default": False,
        "help": "pass to print extra output",
    },
    "--alias": {
        "short_name": "-a",
        "dest": "aliases",
        "action": "append",
        "default": list(),
        "help": 'map alias to version in form "alias:version", ex. 15:15.0',
    },
    "version": {"type": str, "help": "version/alias of image to run"},
    "command": {
        "default": ["python3"],
        "nargs": argparse.ZERO_OR_MORE,
        "help": "command to run in container (default python3)",
    },
}


def get_parser(prog=PARSER_PROG):
    parser = argparse.ArgumentParser(
        prog=prog,
        fromfile_prefix_chars="@",
        formatter_class=HelpFormatter,
        usage="%(prog)s [options] version [command] [-- passthrough]",
    )
    for arg_name, kwargs in PARSER_ARGUMENTS.items():
        short_name = kwargs.pop("short_name", None)
        names = [short_name, arg_name] if short_name else [arg_name]
        parser.add_argument(*names, **kwargs)
    return parser


def parse_argv(argv, rc_filename=None):
    """Parse and post-process argv, including args from rc_filename"""
    parser = get_parser()
    # split odr args from passthrough args
    odr_argv, passthrough = _split_argv(argv)
    if rc_filename:
        # add in the file arg to read from
        odr_argv = chain(iter([f"@{rc_filename}"]), odr_argv)
    args = parser.parse_args(odr_argv)
    # post-process odr args
    args.passthrough = passthrough
    args.aliases = dict(s.split(":") for s in args.aliases)
    args.aliased_version = args.aliases.get(args.version, args.version)
    args.image_tag = f"{args.image}:{args.aliased_version}"
    args.workdir_arg = _optional_arg(args.workdir, [f"-w={args.workdir}"])
    args.remove_arg = _optional_arg(not args.no_remove, ["--rm"])
    args.interactive_arg = _optional_arg(not args.no_interactive, ["-it"])
    _try_apply_multiverse(args)
    # port args
    args.server_port_args = _optional_arg(
        not args.no_server, ["-p", f"{args.server_port}:{args.server_port}"]
    )
    args.debug_port_args = _optional_arg(
        args.debug or args.debug_port != "5678",
        ["-p", f"{args.debug_port}:{args.debug_port}"],
    )
    args.port_args = args.server_port_args + args.debug_port_args
    # volume args
    args.src_volume_args = ["-v", f"{args.host_src}:{args.guest_src}"]
    args.fileshare_volume_args = [
        "-v",
        f"{args.host_fileshare}:{args.guest_fileshare}",
    ]
    args.user_volume_args = _optional_arg(
        args.host_user_src, ["-v", f"{args.host_user_src}:{args.guest_user_src}"]
    )
    args.pg_socket_volume_args = _optional_arg(
        args.pg_use_socket, ["-v", f"{args.pg_socket}:{args.pg_socket}"]
    )
    args.volume_args = (
        args.src_volume_args
        + args.fileshare_volume_args
        + args.user_volume_args
        + args.pg_socket_volume_args
    )
    # env args
    args.pg_user_args = ["-e", f"PGUSER={args.pg_user}"]
    args.pg_host_args = ["-e", f"PGHOST={args.pg_host}"]
    args.pg_port_args = ["-e", f"PGPORT={args.pg_port}"]
    args.pg_pass_args = _optional_arg(
        args.pg_pass, ["-e", f"PGPASSWORD={args.pg_pass}"]
    )
    args.env_args = list(args.pg_user_args)
    if not args.pg_use_socket:
        args.env_args += args.pg_host_args + args.pg_port_args + args.pg_pass_args
    # all of the optional options for `container_command run`
    args.run_option_args = [
        *args.passthrough,
        *args.volume_args,
        *args.port_args,
        *args.env_args,
        *args.workdir_arg,
        *args.remove_arg,
        *args.interactive_arg,
    ]
    return args
