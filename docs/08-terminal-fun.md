# 08 - Terminal screensavers, clocks, and weather

This setup keeps the handwritten launchers and configuration in this repository while
third-party binaries remain external. `scripts/install-terminal-fun.sh` installs only
missing files, so it is safe to rerun and will report local files that differ.

## Commands

| Command | Behavior |
|---|---|
| `saver` | Choose one installed effect at random |
| `saver help` | Show all effects and whether each dependency is installed |
| `saver <name>` | Run one explicit effect, for example `saver pipes3d` |
| `saverwall [top] [bottom]` | Start two distinct effects in stacked tmux panes and span all X11 monitors |
| `ztoy` | Add Cava above `tclock` on the right side of the current Zellij tab |
| `ztoy off` | Close those Cava and clock panes in the current tab |
| `zcava` | Toggle a borderless Cava footer in the current Zellij tab |
| `zcava on` / `zcava off` | Explicitly open or close the Cava footer |
| `pclock` / `tclock` | Responsive party clock / classic centered clock |
| `weather [place]` / `wx` | Korean three-day forecast, defaulting to Suwon |
| `wxn [place]` / `wxt [place]` | One-line current conditions / today's forecast |
| `weathr` | Animated weather scene, separate from the forecast commands |

`saverwall` also installs a `Saver Wall` desktop entry and icon, making it searchable
from the GNOME application launcher. Its multi-monitor fullscreen control uses X11
Xinerama/EWMH; it is not a Wayland-native implementation.

## Runtime dependencies

Ubuntu 24.04 packages used by the current machine:

```bash
sudo apt install alacritty bb caca-utils cava cbonsai cmatrix curl hollywood jq \
  nyancat python3-xlib sl tmux tty-clock xsel
```

Zellij is required for `ztoy` and `zcava`. The random saver launcher simply skips any
effect whose executable is absent, so the entire optional list does not need to be installed.
`/usr/games` is added by the launcher for Ubuntu's `bb`, `cbonsai`, and `sl` packages.

### Cava footer

`zcava` uses a small tiled command pane rather than a WASM plugin. It splits the leftmost
pane downward, shrinks Cava to 5 rows, and restores the previous layout when toggled off.
It never covers terminal content. `ZCAVA_HEIGHT` overrides the default height.

The dedicated `files/config/cava/zcava.conf` disables automatic sensitivity changes,
sets sensitivity to 35%, limits the height to 70%, uses a muted blue, and lowers the
frame rate to 30. This makes it less visually distracting than the normal Cava view.

No Zellij key is bound to this command. Run `zcava` manually when the footer is wanted.

### X11 clipboard workaround

Alacritty 0.17 can fail to claim the XCB clipboard selection when Zellij sends an OSC52
copy and print `Failed to set new owner of XCB selection` into the launching terminal.
`scripts/install-zellij-clipboard.py` configures Zellij to pipe copied text directly to
`xsel --clipboard --input` instead. It preserves any existing active `copy_command`.

The manually installed tools on the captured x86_64 machine are:

| Tool | Pinned version | Installed executable SHA-256 | Upstream |
|---|---:|---|---|
| terminal-toys | 0.7.0 | `a8bc4cfa08b00c5e854600c844827cd8967db5c6635f176e1150d307ed756de1` | [release](https://github.com/Seebass22/terminal-toys/releases/tag/v0.7.0) |
| astroterm | 1.2.0 | `57a542bd37d01337a5dfd8582015a76c9949c0a514e4b9335e0c1aa44445b3df` | [release](https://github.com/da-luce/astroterm/releases/tag/v1.2.0) |
| genact | 1.5.1 | `5208ba2fac015585e535bbf12c3d5743bb11f16194fe19b79a1213975a312c12` | [release](https://github.com/svenstaro/genact/releases/tag/v1.5.1) |
| peaclock | 0.4.3 | `634491598c18761c6d71b23698c7685a65e739be0725326ba62a033c355ffff3` | [tag](https://github.com/octobanana/peaclock/tree/0.4.3) |
| weathr | 1.4.0 | `7b9761f2b97183e4ac546bbcda45719d63a05a95aed84d996580b6975ba26213` | [release](https://github.com/Veirt/weathr/releases/tag/v1.4.0) |

`tty-clock` 2.3-4 is available from Ubuntu and the current locally extracted binary has
SHA-256 `ad84f434776da4ceced0a5d5f84b79bcca4a8d5d6ad216c80520b65cee0c87a8`.
`pipes.sh` 1.3.0 comes from [pipeseroni/pipes.sh](https://github.com/pipeseroni/pipes.sh).

## Artifacts

- Launchers: `files/bin/{saver,saverwall,ztoy,zcava,weather,pclock,tclock,wx,wxn,wxt}`
- Zellij clipboard installer: `scripts/install-zellij-clipboard.py`
- Shell modules: `files/shell/{saver.zsh,tools-cheatsheet.zsh}`
- Clock and animation settings: `files/config/{cava,peaclock,weathr}/`
- App launcher: `files/applications/saverwall.desktop.in`, `files/icons/saverwall.svg`

The `tools` shell function is the compact command index. It is loaded by the modular
`~/.zsh/my-zshrc/*.zsh` loop in `files/shell/zshrc.sample`.
