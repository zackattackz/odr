import json
import os
from inspect import signature
from runner import ContainerRunner

default_cfg = {
    "aliases": {"16": "16.0", "17": "17.0"},
    "container_program": "podman",
    "extra_env": [["PGUSER", "$USER"]],
    "image_name": "odr",
    "workdir_path": "/root/workdir",
    "postgres_run_path": "/var/run/postgresql",
    "guest_fileshare_path": "/root/.local/share/Odoo",
    "guest_src_path": "/root/src/",
    "guest_user_src_path": "/root/src/user",
}


def get_default_file_path():
    """Get default config file path"""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        res = os.path.join(xdg_config_home, "odr.json")
    else:
        res = os.path.join(
            os.path.expanduser("~"), ".config", "odr.json"
        )
    return res


def merge_dicts(dict_one, dict_two):
    """Set items from dict_two into dict_one. Merges lists. Returns new dict"""
    res = {**dict_one}
    for k, v in dict_two.items():
        if k in res and isinstance(res[k], list):
            res[k] = [*res[k], *v]
        else:
            res[k] = v
    return res


def load_config_file(file_path):
    """Parse contents of config file as a dict, return empty dict if file doesn't exist"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def with_aliased_version(cfg):
    """Set version to its alias if it exists"""
    res = {**cfg}
    if "aliases" in res and "version" in res:
        res["version"] = res["aliases"].get(res["version"], res["version"])
    return res


def with_host_paths(cfg):
    """Expand host paths to absolute paths"""
    host_path_keys = {"host_fileshare_path", "host_src_path", "host_user_src_path"}
    expanded_host_path_items = {
        k: os.path.abspath(os.path.expandvars(cfg[k]))
        for k in host_path_keys
        if k in cfg
    }
    return {**cfg, **expanded_host_path_items}


def with_host_src_path(cfg):
    """Set host_src_path to proper path based on detection of universe/multiverse setup"""
    res = {**cfg}
    version_file_path = os.path.join(res["host_src_path"], res["version"])
    if os.path.exists(version_file_path):
        res["host_src_path"] = version_file_path
    return res


def with_expanded_extra_volumes(cfg):
    """Expand extra_volumes to absolute paths"""
    res = {**cfg}
    if "extra_volumes" in res:
        res["extra_volumes"] = [
            [os.path.abspath(os.path.expandvars(src)), dst]
            for src, dst in res["extra_volumes"]
        ]
    return res


def with_expanded_extra_env(cfg):
    """Expand values in extra_env"""
    res = {**cfg}
    if "extra_env" in res:
        res["extra_env"] = [
            [var, os.path.expandvars(val)] for var, val in res["extra_env"]
        ]
    return res


def filter_container_runner_params(cfg):
    """Return only ContainerRunner parameters"""
    runner_params = set(signature(ContainerRunner).parameters.keys())
    return {k: v for k, v in cfg.items() if k in runner_params}

def prepare_config(cfg):
    """Apply all config preparation functions"""
    cfg = with_aliased_version(cfg)
    cfg = with_host_paths(cfg)
    cfg = with_host_src_path(cfg)
    cfg = with_expanded_extra_volumes(cfg)
    cfg = with_expanded_extra_env(cfg)
    cfg = filter_container_runner_params(cfg)
    return cfg

def merge_configs(args_dict, file_path, default_cfg):
    """Perpare config from args, config file and defaults. Preferences are in that order"""
    file_cfg = load_config_file(file_path)
    cfg = merge_dicts(default_cfg, file_cfg)
    cfg = merge_dicts(cfg, args_dict)
    if cfg.get("verbose"):
        print("Unprepared config:")
        print(cfg)
    cfg = prepare_config(cfg)
    return cfg
