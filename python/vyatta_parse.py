#!/usr/bin/env python

import re


# Order matters here
line_re = re.compile("(?:{})".format("|".join([
    r'^([\w\-]+) \{$',                  # section header
    r'^([\w\-]+) ([\w\-\"\./@:]+) \{$', # section header with parameter
    r'^([\w\-]+) "?([^"]+)?"?$',        # key with optionally quoted parameter
    r'^([\w\-]+)$',                     # single key with no parameter
])))


# Parse a line and transform keys/values as needed
def parse_line(line):
    m = line_re.match(line).groups()
    single_header, header, hparam, key, value, single = m
    if single_header:
        key, value = single_header, {}
    elif header:
        key, value = " ".join([header, hparam]), {}
    elif single:
        key, value = single, None

    return key, value


# Keys can be repeated, if they are convert them to a list, otherwise just
# add them to the dict
def insert_value(parent, key, value):
    item = parent.get(key)
    if item:
        if hasattr(item, "append"):
            item.append(value)
        else:
            parent[key] = [item, value]
    else:
        parent[key] = value


def parse(filename):
    # List of all current scopes, grows downward, top scope is our main config
    # object. Only top scope should remain at end of program
    scopes = [{}]

    for line in open(filename):
        line = line.strip()

        # Discard junk
        if not line or line.startswith("/*"):
            continue

        # Close a scope
        if line == "}":
            scopes.pop()
            continue

        key, value = parse_line(line)
        insert_value(scopes[-1], key, value)

        # Start a new scope
        if line.endswith("{"):
            scopes.append(value)

    return scopes[0]


if __name__ == "__main__":
    import sys, json
    json.dump(parse("config.boot"), sys.stdout)
