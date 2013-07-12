#!/usr/bin/env python3

import os
import os.path
import stat

keys = {}

keys['openshift'] = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLNV5pgT7qrMcbs3J71nLFhVDGkGhE4PZnNYRuJZ0gfOB2yWqjBhTPBnDXUDzDrSsRXiFJ+Vz+UcK0sVB7qp7bwicr4WfxshSTuWd9rqS0bxpiFuVqjHq1dPhLu8k0PsryPPr0CL/UpZ8zgfUPOy5aORZeTx0hlnKtIr8fjIfeO6ZWf9k+aYtFJlcrST1QYwtJ5DowZeL4LE/u1B8F6kETIrzwaUQoUMpzjNecsdNb80wqdBCYrMmN7aPC2IwnahNzOgEltLGShpz5+Fku+TTnKj5WuPXAofQndKNSp4/eV3+r4bcoUWzn8v2Q7rUnvdqoRUdJR6U6cEDjPH2avbGH OpenShift-Key'

keys['moz'] = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCpTQp1MWkgCvXYwRZrPxOuYT/zsgpzXDhE8+jySWMC8Y3g8GAqsp1JphcdWr6/DQiWTIzzdqgbDK3gD619PuYF5/cjwVduFYuqGlCRTZ9zCls2yySJUDQGQI0KQxaQgpXzGh8+BCFWwPfjVKzCq/gPW4Q+yK09M4c8fCjQg5353W8wQB3tBh6xFVM3Hs37kb2AQAQiWOg6ByeGJNnVF/sO7LUBn1aoPKH8G0QADvQLqHQkGPcUZIfodRAW/XawJD/93P9hqOzRV/HCcAJTLvqIUDY1NVl0N7W/oZRxcH+k2OEuYoRnXUeYnYoQvVOMb2vEV5OYhyO8y/h5jRrIol0L Mozilla key'

def key_file_path(ssh_dir, key_prefix, public):
    file_name = '{}_rsa{}'.format(key_prefix, '.pub' if public else '')
    return os.path.join(ssh_dir, file_name)

def write_pub_key(ssh_dir, key_prefix, key):
    with open(key_file_path(ssh_dir, key_prefix, True), 'w', encoding='ascii') as f:
        f.write(key + '\n')

def change_priv_key_mode(ssh_dir, key_prefix):
    os.chmod(key_file_path(ssh_dir, key_prefix, False), stat.S_IRUSR | stat.S_IWUSR)

if __name__ == '__main__':
    ssh_dir = os.path.expanduser('~/.ssh')
    os.makedirs(ssh_dir, mode=0o700, exist_ok=True)

    with open(os.path.join(ssh_dir, 'config'), 'w', encoding='utf-8') as config:
        config.write('# generated automatically, DO NOT EDIT\n')
        config.write('\n')

        for key_type, host, user in zip(('openshift', 'moz'),
                                        ('rhcloud.com', 'mozilla.org'),
                                        ('', 'iacobcatalin@gmail.com'),
                                    ):

            change_priv_key_mode(ssh_dir, key_type)

            write_pub_key(ssh_dir, key_type, keys[key_type])

            config.write('Host *.{}\n'.format(host))
            config.write('IdentityFile {}\n'.format(key_file_path(ssh_dir, key_type, False)))
            if user:
                config.write('User {}\n'.format(user))
            config.write('\n')
