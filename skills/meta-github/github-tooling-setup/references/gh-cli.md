# gh CLI: install and authenticate

## Install per OS

### Debian / Ubuntu (official apt repository)

```bash
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh -y
```

### Fedora / RHEL (dnf5)

```bash
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

### macOS

```bash
brew install gh
```

### Windows

```powershell
winget install --id GitHub.cli
```

If winget is unavailable: `scoop install gh` or `choco install gh`.

### Dev containers

Add the feature `ghcr.io/devcontainers/features/github-cli:1` to
`devcontainer.json` instead of installing inside a running container, so
the install survives rebuilds.

## Authenticate

- Agents and CI: set the `GH_TOKEN` environment variable to a personal
  access token. It requires no interactive step and takes precedence
  over any credentials stored by `gh auth login`.
- Humans: `gh auth login` walks through browser or device-code
  authentication. It is interactive — direct the user to run it in their
  own terminal; never start it from an agent session.

## Interpret `gh auth status`

- Exit code 0: authenticated. The output shows the active account and
  the token's scopes.
- Non-zero exit: not authenticated — no token was found, or the token
  was rejected. Set `GH_TOKEN`, bridge git's stored credential (below),
  or ask the user to run `gh auth login`.

## Bridge git's stored credential

When `gh auth status` fails but `git push` or `git fetch` against a
github.com HTTPS remote succeeds, git's credential helper already holds
a token. It can be borrowed for gh without creating or storing anything
new:

```bash
GH_TOKEN="$(printf 'protocol=https\nhost=github.com\n' | git credential fill | sed -n 's/^password=//p')" gh <command>  # gitleaks:allow
```

- Get the user's explicit consent before the first use, and do not run
  the bridge until they give it. Reusing a credential the user handed
  git for a different tool is theirs to authorize: ask with the agent's
  user-question tool if it has one, otherwise stop and wait for the
  user — never assume approval. One explicit yes covers the rest of the
  session unless the user narrows or withdraws it.
- The command-scoped `GH_TOKEN=… gh` form above holds the token only for
  that one call; never assign it to a persistent shell variable, export
  it, echo it, write it to a file or config, or feed it to `gh auth
  login`. (`sed` takes the whole password, including any `=`, where
  `cut -d= -f2` would truncate it.)
- The bridge grants exactly the credential the user already gave git —
  no new scopes. Scope-gated calls (for example Projects v2 needing
  `project`) may still fail; fall back to a real token setup when they
  do.
- After using the bridge, tell the user git's stored credential was
  reused to authenticate gh; never include the token value.

Done when: the user consented, the gh call succeeded, and the reuse was
disclosed.
