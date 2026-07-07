# glab CLI: install and authenticate

## Install per OS

Releases (all platforms, checksums, .deb/.rpm/binaries):
<https://gitlab.com/gitlab-org/cli/-/releases>

### macOS

```bash
brew install glab
```

### Fedora / RHEL

```bash
sudo dnf install glab
```

### Arch Linux

```bash
sudo pacman -S glab
```

### Debian / Ubuntu

There is no official apt repository. Download the `.deb` for your
architecture from the releases page and install it:

```bash
curl -fsSLo /tmp/glab.deb "https://gitlab.com/gitlab-org/cli/-/releases/permalink/latest/downloads/glab_amd64.deb"
sudo dpkg -i /tmp/glab.deb
```

If the permalink asset name fails (asset naming has changed across
releases), open the releases page and copy the current `.deb` URL.
Alternative: `sudo snap install glab` where snap is available.

### Windows

```powershell
winget install glab.glab
```

If winget is unavailable: `scoop install glab`.

### Dev containers

There is no first-party dev container feature for glab. Install the
release binary in the image build (Dockerfile `RUN` or
`postCreateCommand`) using the Linux binary from the releases page, so
the install survives rebuilds.

## Authenticate

- Agents and CI: set `GITLAB_TOKEN` to a personal access token, and
  `GITLAB_HOST` to the instance host for anything that is not
  gitlab.com. This requires no interactive step and takes precedence
  over stored credentials.
- To persist credentials in glab's config instead (useful when several
  hosts are used side by side):

  ```bash
  printf %s "$GITLAB_TOKEN" | glab auth login --hostname HOST --stdin
  ```

- Humans: `glab auth login` walks through browser/OAuth or token entry
  interactively — direct the user to run it in their own terminal; never
  start it from an agent session.
- Self-managed instances with a non-standard API location can pass
  `--api-host` / `--api-protocol` to `glab auth login`.

## Interpret `glab auth status`

- Lists every configured host with a ✓/✗ per check (token validity, API
  reachability). Exit code 0 means at least the checked host is usable;
  pass `--hostname HOST` to check one host specifically.
- Failure output names the cause: no token found for the host, or the
  token was rejected. Set `GITLAB_TOKEN` + `GITLAB_HOST`, or run the
  `--stdin` login above.
