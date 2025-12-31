# fitnessWay

Simple guide to help teammates (especially on Windows with VS Code) share their SSH keys and connect to the repository.

## 1. Prepare Windows workstation
- Install [Git for Windows](https://git-scm.com/download/win) and keep the default option that enables "Git from the command line".
- Install [Visual Studio Code](https://code.visualstudio.com/) and sign in so settings sync across machines.
- Optional: install the official GitHub VS Code extension for an integrated Pull Request experience.

## 2. Generate SSH keys and send the public key
1. Open **PowerShell** (Win + X → Windows PowerShell).
2. Run:
   ```powershell
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
   Press Enter to accept the default file location `C:\Users\<you>\.ssh\id_ed25519` and choose a passphrase you will remember.
3. Display the public key:
   ```powershell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
   ```
4. Copy the entire line (it starts with `ssh-ed25519`) and send it to the repo maintainer so it can be added to GitHub, **or** paste it yourself under **GitHub → Settings → SSH and GPG keys → New SSH key**.

## 3. Verify access to GitHub over SSH
```powershell
ssh -T git@github.com
```
Type `yes` if prompted to trust GitHub. You should see a "successfully authenticated" message.

## 4. Clone and open the repo in VS Code
1. Open VS Code → `Ctrl+Shift+P` → **Git: Clone**.
2. Paste the repo URL: `git@github.com:yasseen116/fitnessWay.git`.
3. Choose a folder (e.g., `C:\dev\fitnessWay`). When the clone completes, click **Open** to load the workspace.
4. When prompted, trust the authors so VS Code enables workspace features.

## 5. Working with Git in VS Code
- Make sure you are on the latest `main`: `Ctrl+Shift+P` → **Git: Pull**.
- Create feature branches via the status bar branch menu (e.g., `feature/login-ui`).
- Stage and commit changes in the Source Control sidebar, then push using the cloud icon.
- Open pull requests through the GitHub extension or directly on github.com.

## 6. Common troubleshooting tips
- If cloning fails, re-run `ssh -T git@github.com` to confirm the key is registered.
- Ensure any corporate proxy allows SSH on port 22 or use GitHub's HTTPS fallback.
- Keep Git, VS Code, and extensions updated for the best experience.
