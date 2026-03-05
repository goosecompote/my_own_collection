#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_own_module

short_description: Create or update a text file on remote host

version_added: "1.0.0"

description:
  - Creates a text file on the remote host at the specified path.
  - Writes the specified content into the file.
  - Reports changed when file content is created or updated.

options:
  path:
    description:
      - Destination file path on the remote host.
    required: true
    type: str
  content:
    description:
      - Text content to write into the file.
    required: true
    type: str
  mode:
    description:
      - File permissions (octal string), for example C(0644).
      - If omitted, permissions are not changed.
    required: false
    type: str

author:
  - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
- name: Create file with content
  my_namespace.my_collection.my_own_module:
    path: /tmp/hello.txt
    content: "hello world\n"

- name: Create file with content and permissions
  my_namespace.my_collection.my_own_module:
    path: /tmp/hello.txt
    content: "hello world\n"
    mode: "0644"
'''

RETURN = r'''
path:
  description: Path to the file.
  type: str
  returned: always
changed:
  description: Whether the file was modified.
  type: bool
  returned: always
content_written:
  description: The content that was requested to be written.
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os
import tempfile


def _read_file(path):
    with open(path, 'rb') as f:
        return f.read()


def _atomic_write(path, data_bytes):
    directory = os.path.dirname(path) or '.'
    fd, tmp_path = tempfile.mkstemp(prefix='.ansible_my_own_module_', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(data_bytes)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True),
        mode=dict(type='str', required=False, default=None),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    path = module.params['path']
    content = module.params['content']
    mode = module.params['mode']

    if not os.path.isabs(path):
        module.fail_json(msg='path must be an absolute path', path=path)

    content_bytes = content.encode('utf-8')

    exists = os.path.exists(path)
    current_bytes = b''
    if exists and os.path.isfile(path):
        try:
            current_bytes = _read_file(path)
        except Exception as e:
            module.fail_json(msg='failed to read existing file: {0}'.format(e), path=path)
    elif exists and not os.path.isfile(path):
        module.fail_json(msg='path exists and is not a regular file', path=path)

    changed = (not exists) or (current_bytes != content_bytes)

    result = dict(
        changed=changed,
        path=path,
        content_written=content,
    )

    if module.check_mode:
        module.exit_json(**result)

    if changed:
        try:
            parent = os.path.dirname(path)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)

            _atomic_write(path, content_bytes)

            if mode is not None:
                try:
                    os.chmod(path, int(mode, 8))
                except Exception as e:
                    module.fail_json(msg='failed to chmod file: {0}'.format(e), path=path, **result)

        except Exception as e:
            module.fail_json(msg='failed to write file: {0}'.format(e), path=path, **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
