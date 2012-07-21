#!/usr/bin/env python

import logging
import re
import os
import shutil

logger = logging.getLogger(__name__)

BOOT_FILE_PREFIXES = (u'initrd', u'System.map', u'vmlinuz', )

def discover_in_dir(directory, file_prefix):
    version_pattern = u'(?P<version>[\\w.-]+catalin[\\w.-]*)'
    kernel_file_pattern = u'{0}-{1}'.format(file_prefix, version_pattern)

    for dir_entry in os.listdir(directory):
        match = re.match(kernel_file_pattern, dir_entry)
        if match is not None:
            version = match.group(u'version')
            yield version

def discover_kernel_versions():
    for file_prefix in BOOT_FILE_PREFIXES:
        for version in discover_in_dir(u'/boot', file_prefix):
            yield version

    for version in discover_in_dir(u'/lib/modules', u''):
        yield version

def remove_file_report_errors(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        logger.warning(u'Cannot remove %s: %s', file_path, e)

def remove_kernel(version):
    for file_prefix in BOOT_FILE_PREFIXES:
        file_path = u'{0}-{1}'.format(file_prefix, version)
        remove_file_report_errors(os.path.join(u'/boot', file_path))

    modules_path = os.path.join(u'/lib/modules', version)
    shutil.rmtree(u'/lib/modules/{0}'.format(candidate), ignore_errors=True)

if __name__ == u'__main__':
    logging.basicConfig(level=logging.DEBUG)

    versions = list(sorted(set(discover_kernel_versions())))
    logger.debug(u'Found kernel versions %s', u', '.join(versions))

    running_version = os.uname()[2]
    removal_candidates = versions[:]
    if running_version in removal_candidates:
        removal_candidates.remove(running_version)
    logger.debug(u'Candidates for removal %s', u', '.join(removal_candidates))

    removed = []
    for candidate in removal_candidates:
        known_input = False
        while not known_input:
            input = raw_input(u'Remove {0}? [y/n] '.format(candidate))
            if input == u'y':
                logger.info(u'Removing kernel %s', candidate)
                remove_kernel(candidate)
                removed.append(candidate)

            if input in (u'y', u'n'):
                known_input = True
    
    logger.info(u'Removed kernels, update your bootloader:\n%s', u'\n'.join(removed))
