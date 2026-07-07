# Canonical check recipes for this repository.
# Agents and humans should run checks through these recipes (not ad-hoc
# commands) so results stay consistent across environments.

# List available recipes
default:
    @just --list

# One-time environment setup (run after cloning / container creation)
setup:
    pre-commit install
    git config commit.template .gitmessage

# Validate skill layout and harness consistency
validate:
    python3 scripts/validate_skills.py

# Lint specific skill directories (spec + quality checks)
check-skill +PATHS:
    python3 scripts/check_skill.py {{PATHS}}

# Regenerate marketplace.json skills[] from the catalogs on disk
gen-marketplace:
    python3 scripts/gen_marketplace.py

# Lint and check formatting of repository scripts
lint:
    ruff check scripts/
    ruff format --check scripts/

# Run every check (validator, lint, pre-commit hooks)
check: validate lint
    pre-commit run --all-files
