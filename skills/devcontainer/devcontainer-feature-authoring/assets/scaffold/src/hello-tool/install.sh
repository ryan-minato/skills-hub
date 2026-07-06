#!/usr/bin/env bash
# Example installer. Structure to keep when replacing with a real tool:
# strict mode, root check, options via env vars, idempotent install,
# user-facing work done for _REMOTE_USER (not root).
set -euo pipefail

# Options arrive as UPPERCASED env vars (non-alphanumerics -> _).
VERSION="${VERSION:-latest}"
GREETING="${GREETING:-hello}"

# Feature installers run as root during the image build.
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must run as root (it runs during the image build)." >&2
    exit 1
fi

TARGET=/usr/local/bin/hello-tool

# Idempotent: re-installation overwrites cleanly instead of failing.
cat > "$TARGET" <<EOF
#!/bin/sh
echo "${GREETING} from hello-tool ${VERSION}"
EOF
chmod 0755 "$TARGET"

# Pattern for user-facing artifacts (rc entries, per-user state): act as
# _REMOTE_USER and write into _REMOTE_USER_HOME, then chown. Example:
#   install -d -o "${_REMOTE_USER}" "${_REMOTE_USER_HOME}/.config/hello-tool"

echo "hello-tool installed: $("$TARGET")"
