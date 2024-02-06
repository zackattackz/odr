import argparse
import config

from runner import ContainerRunner


def clean_args(args):
    """Return only non-None args"""
    return {k: v for k, v in args.items() if v is not None}


def parse_extra_volumes(extra_volumes):
    """Split extra_volumes on ':'"""
    return [v_str.split(":") for v_str in extra_volumes]


def parse_extra_env(extra_env):
    """Split extra_env on '='"""
    return [v_str.split("=") for v_str in extra_env]


def main():
    parser = argparse.ArgumentParser(prog="odr", description="CLI program for odr")
    parser.add_argument("version", type=str, help="Version string")
    parser.add_argument(
        "-a",
        "--extra-runtime-args",
        nargs="+",
        help="Extra args to pass to container runner",
    )
    parser.add_argument(
        "-c", "--config", dest="config_path", type=str, help="Path to config file"
    )
    parser.add_argument(
        "-p",
        "--container-program",
        type=str,
        help="Container runner program to use (e.g. podman, docker)",
    )
    parser.add_argument(
        "-f",
        "--fileshare",
        dest="host_fileshare_path",
        type=str,
        help="Path to Odoo fileshare on host",
    )
    parser.add_argument(
        "-s",
        "--src",
        dest="host_fileshare_path",
        type=str,
        help="Path to Odoo fileshare on host",
    )
    parser.add_argument(
        "-u",
        "--user",
        dest="host_user_src_path",
        type=str,
        help="Path to user modules directory on host",
    )
    parser.add_argument(
        "-v",
        "--extra-volumes",
        nargs="+",
        help="Extra volumes of form host_path:guest_path to mount in container",
    )
    parser.add_argument(
        "-d", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "run_args", nargs=argparse.REMAINDER, help="Command to run in container"
    )

    args = vars(parser.parse_args())
    args = clean_args(args)
    if "extra_volumes" in args:
        args["extra_volumes"] = parse_extra_volumes(args["extra_volumes"])
    if "extra_env" in args:
        args["extra_env"] = parse_extra_env(args["extra_env"])

    file_path = args.get("config", config.get_default_file_path())
    cfg = config.merge_configs(args, file_path, config.default_cfg)

    runner = ContainerRunner(**cfg)

    if cfg.get("verbose"):
        print("Prepared config:")
        print(cfg)
        print("Running the following command:")
        print(" ".join(runner.program))

    runner.run()


if __name__ == "__main__":
    main()
