#!/bin/sh
# usage: sbx.sh <absolute out dir> <python flags...> -- <script> <args...>
OUTD="$1"; shift
PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$OUTD\") (literal \"/dev/null\"))" perl -e 'alarm 600; exec @ARGV' /opt/homebrew/bin/python3.12 "$@"
