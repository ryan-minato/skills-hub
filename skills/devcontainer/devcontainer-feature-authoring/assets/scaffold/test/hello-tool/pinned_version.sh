#!/bin/bash
set -e

# shellcheck source=/dev/null
source dev-container-features-test-lib

check "pinned version reported" bash -c "hello-tool | grep -q 'hi from hello-tool 1.0'"

reportResults
