# ⚡ FlexUV

![Sheen Banner](https://raw.githubusercontent.com/74Thirsty/74Thirsty/main/assets/flexuv.svg)


<div align="center">
  <a href="https://postimg.cc/cgy6w8tr">
    <img src="https://i.postimg.cc/pTy8Nf2Y/Chat-GPT-Image-Mar-15-2026-02-20-47-AM-removebg-preview.png"/>
  </a>
</div>
<!-- Badges -->
<div align="center">
  <a href="https://github.com/74Thirsty/flex_uv">
    <img src="https://img.shields.io/badge/App-Flex%20UV-7BAFD4?style=for-the-badge&labelColor=0B1D2A&color=7BAFD4">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Language-100%25%20Python-6FA8D6?style=for-the-badge&logo=python&logoColor=ffffff&labelColor=0B1D2A&color=6FA8D6">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/Package%20Manager-uv-63A1D8?style=for-the-badge&labelColor=0B1D2A&color=63A1D8">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Interface-TUI-5799DA?style=for-the-badge&labelColor=0B1D2A&color=5799DA">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Author-Christopher%20Hirschauer-4B92DC?style=for-the-badge&labelColor=0B1D2A&color=4B92DC">
  </a>
</div>

---

## The Interactive Command Center for `uv`

> Stop memorizing `uv` commands.
> Manage Python environments visually — **without leaving your terminal.**

FlexUV is a **terminal UI (TUI)** built with **Textual** that turns the `uv` Python ecosystem into a **visual command center**.

Instead of typing dozens of commands, you get a **guided interface for managing projects, environments, dependencies, and tools**.

Think:

> **LazyGit — but for Python environments.**

---

# 🚀 Demo

```
███████╗██╗     ███████╗██╗  ██╗██╗   ██╗██╗   ██╗
██╔════╝██║     ██╔════╝╚██╗██╔╝██║   ██║██║   ██║
█████╗  ██║     █████╗   ╚███╔╝ ██║   ██║██║   ██║
██╔══╝  ██║     ██╔══╝   ██╔██╗ ██║   ██║╚██╗ ██╔╝
██║     ███████╗███████╗██╔╝ ██╗╚██████╔╝ ╚████╔╝
╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝

FlexUV — The Interactive UV Command Center
```

---

# ✨ Features

### 🧭 Dashboard

See the state of your environment instantly.

* OS + Python detection
* `uv` installation check
* project detection
* environment markers

---

### 📦 Project Management

Run core `uv` workflows from a guided interface.

```
uv init
uv sync
uv lock
uv tree
```

Create new projects and configure:

* package name
* description
* Python version

---

### 📚 Dependency Management

Add or remove dependencies quickly.

```
uv add fastapi
uv remove requests
```

Run commands directly inside your project environment.

---

### 🐍 Python Version Manager

Manage Python versions with `uv`.

```
uv python install 3.12
uv python list
uv python find
uv python pin
```

---

### 🧰 Tool Manager

Install global developer tools.

```
uv tool install ruff
uv tool uninstall black
uv tool list
```

Run tools with `uv tool run`.

---

### 🔁 Pip Compatibility Mode

Still need pip workflows?

FlexUV exposes:

```
uv pip install
uv pip uninstall
uv pip list
uv pip freeze
uv pip tree
```

---

### ⚡ Command Center

Quick-access presets:

```
uv version
uv self update
uv cache dir
uv cache clean
uv tool list
uv python list
```

Or run **custom uv commands**.

---

### 📜 Command Logging

Every command executed is logged.

```
$ uv add textual

Installed successfully

(exit code: 0)
```

No hidden magic — you always see what happens.

---

# 🖥 Interface

FlexUV organizes everything into tabs:

```
Dashboard
Project
Python
Tools
Pip Mode
Command Center
Logs
```

It’s designed to feel like a **modern terminal application**.

---

# 📦 Installation

First install **uv**:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then run FlexUV:

```
python app.py
```

---

# 🧠 Why FlexUV Exists

`uv` is incredibly powerful.

But command-heavy tools have a discoverability problem.

FlexUV solves this by providing:

* visual workflows
* command guidance
* environment awareness
* command logs
* safer actions

All **without leaving the terminal**.

---

# 🛠 Built With

* Python
* Textual
* Rich
* uv

---

# 🗺 Roadmap

Planned improvements:

* dependency graph visualization
* environment health checks
* plugin system
* task runner integration
* project templates
* package security scanning

---

# ⭐ Contributing

Contributions welcome!

If you have ideas, open an issue or PR.

---

# 🔥 If You Like This Project

Give it a ⭐ on GitHub.

It helps the project grow and reach more developers.


