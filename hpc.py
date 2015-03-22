#!/usr/bin/env python

import sys
import yaml
import hierarchy_pillar

if len(sys.argv) == 1:
    print "No minion id given."
    exit(0)

id = sys.argv[1]

result = hierarchy_pillar.build_pillar(id)

print yaml.dump(result, default_flow_style=False)
