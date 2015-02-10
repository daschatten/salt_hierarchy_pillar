# Salt hierarchy Pillar

This external pillar module for salt merges hierarchical pillar data.

## Installation

1. Clone the repo to your salt external module location in the pillar subdirectory. For the correct location look in your master config for extension_modules' or set it to e.g.
    ```
    extension_modules: /srv/salt/extra
    ```
In this case clone the repo to /srv/salt/extra/pillar.

2. Set a symlink to make the module usable because salt ignores subdirectories. E.g. 
    ```
    ln -s /srv/salt/extra/pillar/salt_hierarchy_pillar/hierarchy_pillar.py /srv/salt/extra/pillar/
    ```

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

    Output from command "salt 'myhost' pillar.items":

    ```
    hostname: myhost
    zonename: myzone
    ```

## Merge details

### Merge order

1. Pillar hierarchy for given minion_id is built bottom (host data) up (e.g. zone data) according to given '_parent' keys (or whatever is defined manually). Values in lower levels always takes precedence.

2. Pillar data from earlier running pillar modules is merged in (Pillar hierarchy from 1 takes precedence).

### Merge strategy

A (e.g. host data) is merged with B (e.g. zone data).

* If data type is not the same, e.g. String <-> List then A takes precedence
    ```
     A
    === 
    key: value

     B
    === 
    key: 
        one: 1
        two: 2
    
    Result:
    =======
    key: value
    ```
* If data type is list then values in B not present in A are appended to A
    ```
     A
    ===
    key:
        - one 
        - two

     B    
    === 
    key:
        - two
        - three

    Result:
    =======
    key:
        - one
        - two
        - three  
    ```
* If data type is dict then values from B not present in A are appended to A
    ```
     A
    ===
    key:
        one: 1
        two: 2

     B
    ===
    key:
        one: 4
        two: 2
        three: 3

    Result:
    =======
    key:
        one: 1
        two: 2
        three: 3
    ```
* If data type is str then A takes precedence
    ```
     A
    ===
    key: one

     B
    ===
    key: two

    Result:
    =======
    key: one
    ```

### Control merge strategy

Merge strategy can be controlled in some ways:

A (e.g. host data) is merged with B (e.g. zone data).

* List:
    If first element in a list is '_replace' then the list from B will replace list in A
* Dict:
   If dict contains a key `_control` with value `_replace` then dict from B replaces dict in A
