#!/bin/sh
# Run python 3.14 in the sandbox: no network, writes only inside the build folder.
# usage: sbpy.sh <build folder> <alarm seconds> <python flags, script and arguments...>
BUILD="$1"; N="$2"; shift 2
exec env -u ANTHROPIC_API_KEY -u CEREBRAS_API_KEY -u ANTHROPIC_BASE_URL PYTHONDONTWRITEBYTECODE=1 \
  sandbox-exec -p "(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$BUILD\") (literal \"/dev/null\"))" \
  perl -e 'alarm shift; exec @ARGV' "$N" /usr/local/bin/python3.14 "$@"
