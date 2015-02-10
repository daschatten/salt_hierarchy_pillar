#!/usr/bin/env python

# Import python libs
import os
import logging
import yaml
from copy import deepcopy

# Import salt libs
import salt.utils

# Start loging
log = logging.getLogger(__name__)

# Define defaults
__opts__ = { 
    'hierarchy_pillar.key': '_parent',
    'hierarchy_pillar.data_path': '/srv/salt/pillar',
}

# Argument data does nothing, just needs to be there
def ext_pillar(id, pillar, data):
    # First, build pillar hierarchy starting with host pillar for id
    result = build_pillar(id)

    # Second, combine generated pillar with given pillar variable
    # First built pillar takes precedence
    result = combine_two(result, pillar)

    # Return result
    return result

# Builds a pillar structure starting with given pillar filename or pillar data
def build_pillar(id):
    try:
        pillar_data = load_pillar(id)
    except Exception as e:
        log.critical('build_pillar: load_pillar failed')
        log.critical(e)
        return {}

    parent_id = get_parent(pillar_data)

    if parent_id:
        return combine(pillar_data)
    else:
        return pillar_data

# Returns parent name from given pillar data
def get_parent(pillar_data):
    if __opts__['hierarchy_pillar.key'] in pillar_data:
        log.debug('get_parent: parent exists')
        return pillar_data[__opts__['hierarchy_pillar.key']]
    else:
        log.debug('get_parent: parent does not exist')
        return None

# Loads pillar data from given filename or pillar data
def load_pillar(pillar):
    if type(pillar) is str:
        log.debug('pillar is str!')
        return load_pillar_from_file(pillar)
    else:
        log.debug('pillar is NOT str!')
        return pillar

# Loads pillar data from a file
def load_pillar_from_file(pillar):
    # Get host pillar
    filename = find_file(pillar + '.yaml', __opts__['hierarchy_pillar.data_path'])

    # Open file
    try:
        log.debug('Trying to open file: ' + filename)
        stream = open(filename, 'r')
    except Exception:
        log.critical('Error opening file: ' + filename)
        return {}    

    # Load yaml data from file
    try:
        host_pillar = yaml.load(stream)
        return host_pillar
    except Exception:
        log.critical('YAML data from file "' + filename + '" failed to parse')
        return {}    

# Find file by filename in path hierarchy
def find_file(name, path):
    log.debug('Search file: ' + path + '/' + name)
    for root, dirs, files in os.walk(path):
        if name in files:
            log.critical('Found file: ' + root + '/' + name)
            return os.path.join(root, name)

# Combines pillar data with parents
def combine(pillar_data):
    # Initial load current with given pillar data
    result = pillar_data
    # Loop as long as there is a '_parent' string in current dict
    # This steps up the defined hierarchy 
    while '_parent' in result:
        # Set parent name
        parent_id = result['_parent']
        # Remove '_parent' key to let the parent '_parent' key merge in for next iteration
        del result['_parent']

        try:
            parent_data = load_pillar(parent_id)
            result = combine_two(result, parent_data)
        except Exception:
            return result
    return result

# A is primary and b is secondary
# This means items in a take precedence
def combine_two(a,b):
    if type(a) == type(b):
        return check_types(a,b)
    else:
        return a

# Check type of a and call corresponding function
def check_types(a,b):
    if type(a) is list:
        return combine_list(a,b)
    elif type(a) is dict:
        return combine_dict(a,b)
    else:
        return combine_str(a,b)

# Combines two lists, a takes precedence
def combine_list(a,b):
    if len(a) > 0 and a[0] == '_replace':
        a.pop(0)
    else:
        # a.extend(b) # may generates duplicates
        for item in b:
            if item not in a:
                a.append(item)
    return a    

# TODO: remove control from dict
# Combines two dicts, a takes precedence
# If we find a '_control' key with value '_replace' then existing dict is thrown away
# and new one is used. If not, missing keys are added.
def combine_dict(a,b):
    if not ("_control" in a and a['_control'] == '_replace'):
        for key, value in b.iteritems():
            if not key in a:
                a[key] = value
            else:
                a[key] = combine_two(a[key], b[key])
    return a            

# Combines two strings, it always returns a
def combine_str(a,b):
    return a
