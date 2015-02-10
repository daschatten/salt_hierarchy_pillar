# Salt hierarchy Pillar

This external pillar module for salt merges hierarchical pillar data.

## Installation

1. Clone the repo to your salt external module location in the pillar subdirectory. For the correct location look in your master config for 'extension_modules' or set it to e.g.: extension_modules: /srv/salt/extra. In this case clone the repo to /srv/salt/extra/pillar.

2. Set a symlink to make the module usable because salt ignores subdirectories. E.g. ln -s /srv/salt/extra/pillar/hierarchy_pillar/hierarchy_pillar.py /srv/salt/extra/pillar/

3. Activate pillar in master config:
```
ext_pillar:
    - hierarchy_pillar:
```
or change defaults:
```
ext_pillar:
    - hierarchy_pillar:
        'hierarchy_pillar.key': '_parent'
        'hierarchy_pillar.data_path': '/srv/salt/pillar'
```

## Usage

1. Disable usage of pillar data from pillar/top.sls, e.g.:
```
base:
    '*':
        - hostmap
```

And create an empty pillar/hostmap.sls

2. Put your pillar data in yaml files under /srv/salt/pillar or your configured path (See installation 3.). The pillar files can exist in any number of subdirectories, hierarchy_pillar will find it. The first pillar which is loaded is the pillar file with name <minion_id>.yaml. In it the parent pillar file has to be referenced in keyword '_parent'. Example:

/srv/salt/pillar/hosts/myhost.yaml:
```
_parent: myzone
hostname: myhost
```

/srv/salt/pillar/zones/myzone.yaml:
```
zonename: myzone
```

Output:

```
hostname: myhost
zonename: myzone
```
