import os
import subprocess


class Instance:

    def __init__(self):
        pass

    def create_keys(self, key_name, home_dir, user, public_key, private_key):
        # create .ssh
        ssh_folder = f"{home_dir}/.ssh"
        if not os.path.isdir(ssh_folder):
            os.mkdir(ssh_folder)
            os.chmod(ssh_folder, 0o700)
            subprocess.call(['chown', f"{user}:", ssh_folder])

        private_key_file = f"{ssh_folder}/{key_name}"
        with open(private_key_file, 'w') as f:
            f.write(private_key)
        os.chmod(private_key_file, 0o600)
        subprocess.call(['chown', f"{user}:", private_key_file])

        public_key_file = f"{ssh_folder}/{key_name}.pub"
        with open(public_key_file, 'w') as f:
            f.write(public_key)
        os.chmod(public_key_file, 0o644)
        subprocess.call(['chown', f"{user}:", public_key_file])