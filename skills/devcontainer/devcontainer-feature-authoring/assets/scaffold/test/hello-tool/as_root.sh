#!/bin/bash
set -e

# shellcheck source=/dev/null
source dev-container-features-test-lib

check "works for root user too" bash -c "hello-tool | grep -q 'hello from hello-tool latest'"

reportResults
