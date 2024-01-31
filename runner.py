import os
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContainerRunner:
    """Handles logic of running the container"""

    version: str
    """Version of image to run"""

    container_program: str
    """Container runner program to use (e.g. podman, docker)"""

    run_args: list
    """Command to run in container"""

    image_name: str
    """Name of image to run"""

    workdir_path: str
    """Path to workdir in container"""

    postgres_run_path: str
    """Path to postgres run dir to map 1 to 1 in container"""

    host_src_path: str
    """Path to Odoo source on host"""

    host_fileshare_path: str
    """Path to Odoo fileshare on host"""

    guest_fileshare_path: str
    """Path to Odoo fileshare on guest"""

    guest_src_path: str
    """Path to Odoo source on guest"""

    guest_user_src_path: str
    """Path to user modules directory on guest"""

    verbose: bool = False
    """Enable verbose output"""

    extra_runtime_args: list = field(default_factory=list)
    """Extra args to pass to container runner"""

    extra_volumes: list = field(default_factory=list)
    """Extra tuples of (host_path, guest_path) to mount in container"""

    extra_env: list = field(default_factory=list)
    """Extra environment variables to pass to container"""

    host_user_src_path: Optional[str] = None
    """Path to user modules directory on host"""

    @property
    def image_tag(self):
        """Final image tag, {image_name}:{version}"""
        return f"{self.image_name}:{self.version}"

    @property
    def volume_args(self):
        """List of volume (-v) arguments for container runner"""
        volumes = [
            (".", self.workdir_path),
            (self.postgres_run_path, self.postgres_run_path),
            (self.host_fileshare_path, self.guest_fileshare_path),
            *(
                (
                    os.path.join(self.host_src_path, path),
                    os.path.join(self.guest_src_path, path),
                )
                for path in os.listdir(self.host_src_path)
            ),
            *self.extra_volumes,
        ]
        if self.host_user_src_path:
            volumes.append((self.host_user_src_path, self.guest_user_src_path))

        return [f"-v={src}:{dst}" for src, dst in volumes]

    @property
    def env_args(self):
        """List of env (-e) arguments for container runner"""
        return [f"-e {var}={val}" for var, val in self.extra_env]

    @property
    def program(self):
        """List of arguments to pass to subprocess.run"""
        return [
            self.container_program,
            "run",
            "--rm",
            "--net=host",
            "-w",
            self.workdir_path,
            *self.volume_args,
            *self.env_args,
            *self.extra_runtime_args,
            self.image_tag,
            *self.run_args,
        ]

    def image_exists(self):
        return (
            subprocess.run(
                [self.container_program, "image", "exists", self.image_tag]
            ).returncode
            == 0
        )

    def run(self):
        if not self.image_exists():
            print(f'Image "{self.image_tag}" not found on system')
            exit(1)
        subprocess.run(self.program)
