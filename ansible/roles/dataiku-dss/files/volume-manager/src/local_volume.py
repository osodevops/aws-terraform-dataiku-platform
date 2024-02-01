import sys

import grp
import logging
import os
import pwd
import subprocess

from config import Config
from exceptions import VolumeException

logger = logging.getLogger(__name__)


class LocalVolume:
    blank_fs: bool
    fs_type: str = "xfs"
    config: Config

    def __init__(self, volume_data, config: Config):
        self.blank_fs = volume_data['blank_filesystem']
        self.config = config

    def blank(self):
        return self.blank_fs

    def mount(self, mount_point="", configure_fstab=False):
        if not mount_point:
            mount_point = self.config.volume_mount_point
        if os.path.ismount(mount_point):
            logging.info('Volume is already mounted')
            return
        try:
            _ = subprocess.run(
                f"mount -t {self.fs_type} {self.config.volume_device_name} {mount_point}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            raise VolumeException(f"Error: Could not mount the device", err)

        if configure_fstab:
            with open('/etc/fstab', 'a') as f:
                f.write(f"\n{self.config.volume_device_name} {self.config.volume_mount_point} {self.fs_type} defaults,noatime 0 0")

    def set_mount_ownership(self, mount_point=False, user="dataiku", group="dataiku"):
        if not mount_point:
            mount_point = self.config.volume_mount_point

        os.chmod(mount_point, 0o750)
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(mount_point, uid, gid)

    def unmount(self, mount_point=""):
        if not mount_point:
            mount_point = self.config.volume_mount_point
        try:
            _ = subprocess.run(
                f"umount {mount_point}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            logger.critical(f"Error: Could not unmount the device: {err.output}")
            sys.exit(1)

    def _create_fs(self):
        try:
            _ = subprocess.run(
                f"mkfs -t {self.fs_type} {self.config.volume_device_name}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            logger.critical(f"Error: Could not create filesystem on the device: {err.output}")
            sys.exit(1)

    def _populate_filesystem(self):
        try:
            _ = subprocess.run(
                f"rsync -avc {self.config.volume_mount_point}/ /mnt", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            logger.critical(f"Error: Could not copy default files to device: {err.output}")
            sys.exit(1)

    def _resize_xfs(self):
        try:
            _ = subprocess.run(
                f"xfs_growfs {self.config.volume_device_name}", shell=True,
                check=True, capture_output=True)
        except subprocess.CalledProcessError as err:
            logger.critical(f"Error: Could not unmount the device: {err.output}")
            sys.exit(1)

    def initialise_filesystem(self):
        if self.blank_fs:
            self._create_fs()
            self.mount('/mnt')
            self._populate_filesystem()
            self.unmount('/mnt')
        else:
            if self.fs_type == 'xfs':
                self.mount('/mnt')
                self._resize_xfs()
                self.unmount('/mnt')
