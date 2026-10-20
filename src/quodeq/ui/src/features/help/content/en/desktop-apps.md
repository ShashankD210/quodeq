## Desktop Apps (beta)

The usual way to install quodeq is `pipx install quodeq` on any platform, or `brew install quodeq/tap/quodeq` on macOS. Each release also attaches two desktop builds of the dashboard, for people who would rather not install Python. They are a beta: they open the same dashboard as `quodeq`, but they are not signed, so the first launch takes one extra step.

### What there is

| Key | Value |
| --- | --- |
| Quodeq-&lt;version&gt;-macOS.dmg | The dashboard in a native macOS window, with Python bundled. *Settings*, *Desktop app*, **Show menu bar icon** keeps quodeq in the menu bar to start, stop and watch it while the window is closed. |
| Quodeq-&lt;version&gt;-Windows.zip | The dashboard in a native Windows window (WebView2), with Python bundled. |

Both are on the latest release page of the quodeq repository on GitHub, under *Assets*.

### macOS

Open the `.dmg` and drag Quodeq to Applications. Because the app is unsigned, macOS refuses the first launch. Either right-click the app, choose **Open**, then **Open** again in the dialog, or clear the quarantine flag once in a terminal:

```bash
xattr -cr /Applications/Quodeq.app
```

### Windows

Unzip the archive anywhere and run `Quodeq.exe`. SmartScreen warns about an unrecognized publisher on the first launch: choose **More info**, then **Run anyway**.

### What the apps leave out

The apps contain the dashboard only. The `quodeq` command, and with it headless evaluations, pull request reviews and SARIF export (*Command Line*, *Connect to CI*), comes with the pipx or Homebrew install. Updates work differently too: the daily version check looks at GitHub releases instead of PyPI, and the *Updates* section in **Settings** offers the new download rather than an upgrade command.
