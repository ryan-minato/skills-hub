#!/bin/bash
set -e

# Provided by the devcontainer CLI at test runtime.
# shellcheck source=/dev/null
source dev-container-features-test-lib

check "hello-tool on PATH" hello-tool
check "reports default version" bash -c "hello-tool | grep -q 'hello from hello-tool latest'"

reportResults
