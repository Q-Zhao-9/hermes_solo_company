# Class 2: One-click Hermes installation

This student package installs the **AI Solo Company edition of Hermes** and prepares students for the first website exercise.

## Windows 10/11

1. Download this folder (or the ZIP supplied by your teacher).
2. Double-click **`Install-Hermes-Windows.cmd`**.
3. Approve the Administrator prompt.
4. The installer enables WSL and installs **Ubuntu 24.04**.
5. If Windows asks for a restart, restart and double-click the same file again.
6. On Ubuntu's first launch, create a Linux username and password. The password remains invisible while typing; that is normal.
7. Complete the Hermes setup wizard.

Afterward, open **Ubuntu 24.04** from the Windows Start menu and run:

```bash
hermes doctor
hermes
```

> Windows needs virtualization enabled. Most modern computers already have it enabled. Managed school computers may require an administrator.

## macOS

1. Download this folder (or the ZIP supplied by your teacher).
2. Double-click **`Install-Hermes-Mac.command`**.
3. If macOS blocks it, Control-click the file, choose **Open**, and confirm.
4. If Apple Command Line Tools are requested, install them and then run the installer again.
5. Complete the Hermes setup wizard.

Afterward, open Terminal and run:

```bash
hermes doctor
hermes
```

macOS does **not** need WSL or Ubuntu; Hermes runs directly on macOS.

## First class website prompt

Start Hermes and paste:

```text
Create a simple, modern one-page website for my solo company. Ask me for the company name, target customer, services, colors, and contact details before creating it. Save the website in a new folder named my-first-website and show me how to preview it locally.
```

## Teacher: one-line installation

macOS or an existing Ubuntu/WSL terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Easiio-Inc/hermes_solo_company/main/scripts/class2/install-hermes.sh | bash
```

## What the installer changes

- Windows only: installs/enables WSL and the `Ubuntu-24.04` distribution.
- Clones `https://github.com/Easiio-Inc/hermes_solo_company.git` to `~/.hermes/hermes-agent`.
- Runs the repository's standard Hermes installer.
- Creates the `hermes` command in `~/.local/bin`.
- Starts the official interactive Hermes setup wizard; API keys are not embedded in these scripts.

The scripts are safe to rerun. Existing Hermes configuration under `~/.hermes` is preserved by the standard installer.

## Troubleshooting

- **Windows says restart required:** restart Windows and run `Install-Hermes-Windows.cmd` again.
- **Ubuntu asks for a password:** enter the Linux password created during the first Ubuntu launch, not necessarily the Windows password.
- **`hermes` is not found:** close and reopen Ubuntu/Terminal, then run `~/.local/bin/hermes doctor`.
- **Repository cannot be downloaded:** verify internet access and open <https://github.com/Easiio-Inc/hermes_solo_company> in a browser.
- **Setup was skipped or interrupted:** run `hermes setup`.
