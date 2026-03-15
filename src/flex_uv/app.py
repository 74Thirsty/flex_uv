#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Pretty,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

# ── colours ────────────────────────────────────────────────────────────────────
_UNC_BLUE  = (0x7B, 0xAF, 0xD4)   # Carolina / UNC blue
_HOYAS_DARK = (0x04, 0x1E, 0x42)  # Georgetown dark navy


def _gradient(text: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> Text:
    """Return a Rich Text object with per-line colour gradient from *start* to *end*."""
    lines = text.split("\n")
    non_blank = [l for l in lines if l.strip()]
    steps = max(len(non_blank) - 1, 1)
    rich = Text()
    seen = 0
    for line in lines:
        if line.strip():
            t = seen / steps
            r = int(start[0] + (end[0] - start[0]) * t)
            g = int(start[1] + (end[1] - start[1]) * t)
            b = int(start[2] + (end[2] - start[2]) * t)
            rich.append(line + "\n", style=f"rgb({r},{g},{b})")
            seen += 1
        else:
            rich.append(line + "\n")
    return rich


# ── splash ─────────────────────────────────────────────────────────────────────
SPLASH_CSS = """
SplashScreen {
    align: center middle;
    background: $background;
}

#splash-banner {
    width: auto;
    text-align: center;
    text-style: bold;
    padding: 2 4;
}
"""

_BANNER_TEXT = """\
███████╗██╗     ███████╗██╗  ██╗██╗   ██╗██╗   ██╗
██╔════╝██║     ██╔════╝╚██╗██╔╝██║   ██║██║   ██║
█████╗  ██║     █████╗   ╚███╔╝ ██║   ██║██║   ██║
██╔══╝  ██║     ██╔══╝   ██╔██╗ ██║   ██║╚██╗ ██╔╝
██║     ███████╗███████╗██╔╝ ██╗╚██████╔╝ ╚████╔╝
╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═══╝

FlexUV — The Interactive UV Command Center

Copyright (c) 2026 Chris Hirschauer
All Rights Reserved"""


class SplashScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static(_gradient(_BANNER_TEXT, _HOYAS_DARK, _UNC_BLUE), id="splash-banner")

    async def on_mount(self) -> None:
        await asyncio.sleep(3)
        self.app.pop_screen()


# ── main app CSS ───────────────────────────────────────────────────────────────
APP_CSS = """
Screen {
    layout: vertical;
}

#body {
    height: 1fr;
}

.panel {
    border: round $accent;
    padding: 1;
    margin: 0 1 1 1;
}

.title {
    text-style: bold;
    margin-bottom: 1;
}

.row {
    height: auto;
    margin-bottom: 1;
}

Input, Select, TextArea {
    margin-bottom: 1;
}

Button {
    margin-right: 1;
    margin-bottom: 1;
}

#log {
    height: 1fr;
    border: round $primary;
}

#command_output {
    height: 1fr;
    border: round $success;
}

.status-ok {
    color: $success;
    text-style: bold;
}

.status-bad {
    color: $error;
    text-style: bold;
}
"""


# ── helpers ────────────────────────────────────────────────────────────────────
@dataclass
class CommandResult:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def combined(self) -> str:
        parts = [f"$ {' '.join(self.cmd)}"]
        if self.stdout.strip():
            parts.append(self.stdout.rstrip())
        if self.stderr.strip():
            parts.append("[stderr]\n" + self.stderr.rstrip())
        parts.append(f"\n(exit code: {self.returncode})")
        return "\n\n".join(parts)


class ConfirmScreen(ModalScreen[bool]):
    def __init__(self, title: str, body: str) -> None:
        super().__init__()
        self.title = title
        self.body = body

    def compose(self) -> ComposeResult:
        with Container(classes="panel"):
            yield Static(self.title, classes="title")
            yield Markdown(self.body)
            with Horizontal(classes="row"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="success")

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#confirm")
    def confirm(self) -> None:
        self.dismiss(True)


# ── app ────────────────────────────────────────────────────────────────────────
class UVManager(App):
    TITLE = "UV Manager"
    SUB_TITLE = "Safe, guided terminal management for uv"
    CSS = APP_CSS + SPLASH_CSS

    cwd = reactive(Path.cwd())
    uv_path = reactive("")

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="body"):
            with TabPane("Dashboard", id="dashboard"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Environment", classes="title")
                        yield Static(id="env_summary")
                        yield Button("Refresh", id="refresh_dashboard")
                        yield Button("Install uv", id="install_uv", variant="primary")
                        yield Button("Open Current Folder", id="open_folder")
                    with Vertical(classes="panel"):
                        yield Static("Current Project", classes="title")
                        yield Static(id="project_summary")
                        yield Button("Detect Project", id="detect_project")
                        yield Button("Initialize New Project", id="wizard_init", variant="success")
            with TabPane("Project", id="project"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Project Setup", classes="title")
                        yield Input(str(Path.cwd()), placeholder="Project root", id="project_root")
                        yield Input("my_app", placeholder="Package name", id="project_name")
                        yield Input("A uv-managed Python project", placeholder="Description", id="project_desc")
                        yield Input("3.12", placeholder="Python version", id="project_python")
                        with Horizontal(classes="row"):
                            yield Button("uv init", id="run_init", variant="success")
                            yield Button("uv sync", id="run_sync")
                            yield Button("uv lock", id="run_lock")
                            yield Button("uv tree", id="run_tree")
                    with Vertical(classes="panel"):
                        yield Static("Dependencies", classes="title")
                        yield Input(placeholder="Add dependency, e.g. textual", id="dependency_name")
                        with Horizontal(classes="row"):
                            yield Button("Add", id="dep_add", variant="success")
                            yield Button("Remove", id="dep_remove", variant="warning")
                        yield Input(placeholder="Command to run, e.g. python -m main", id="run_command")
                        yield Button("Run In Project", id="project_run")
            with TabPane("Python", id="python"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Managed Python", classes="title")
                        yield Input("3.12", placeholder="Version like 3.12 or pypy@3.10", id="python_version")
                        with Horizontal(classes="row"):
                            yield Button("Install", id="python_install", variant="success")
                            yield Button("List", id="python_list")
                            yield Button("Find", id="python_find")
                            yield Button("Pin In Project", id="python_pin")
                    with Vertical(classes="panel"):
                        yield Static("Virtual Environments", classes="title")
                        yield Input(".venv", placeholder="Environment path", id="venv_path")
                        with Horizontal(classes="row"):
                            yield Button("Create venv", id="venv_create", variant="success")
                            yield Button("Show activation help", id="venv_help")
                        yield Static(id="venv_help_text")
            with TabPane("Tools", id="tools"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Install Tools", classes="title")
                        yield Input(placeholder="Tool package, e.g. ruff", id="tool_name")
                        with Horizontal(classes="row"):
                            yield Button("Install Tool", id="tool_install", variant="success")
                            yield Button("Uninstall Tool", id="tool_uninstall", variant="warning")
                            yield Button("List Tools", id="tool_list")
                    with Vertical(classes="panel"):
                        yield Static("Run One-Off Tool", classes="title")
                        yield Input(placeholder="Tool command, e.g. ruff check .", id="tool_run_cmd")
                        yield Button("Run via uvx", id="tool_run", variant="primary")
            with TabPane("Pip Mode", id="pip"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Legacy Pip Commands", classes="title")
                        yield Input(placeholder="Package, e.g. requests", id="pip_package")
                        with Horizontal(classes="row"):
                            yield Button("uv pip install", id="pip_install", variant="success")
                            yield Button("uv pip uninstall", id="pip_uninstall", variant="warning")
                        with Horizontal(classes="row"):
                            yield Button("uv pip list", id="pip_list")
                            yield Button("uv pip freeze", id="pip_freeze")
                            yield Button("uv pip tree", id="pip_tree")
            with TabPane("Command Center", id="commands"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Static("Preset Actions", classes="title")
                        yield ListView(
                            ListItem(Label("uv version")),
                            ListItem(Label("uv self update")),
                            ListItem(Label("uv cache dir")),
                            ListItem(Label("uv cache clean")),
                            ListItem(Label("uv tool list")),
                            ListItem(Label("uv python list")),
                            id="preset_list",
                        )
                        yield Button("Run Selected Preset", id="run_preset", variant="primary")
                    with Vertical(classes="panel"):
                        yield Static("Custom Command", classes="title")
                        yield Input(placeholder="Example: uv add rich", id="custom_command")
                        yield Button("Run Custom uv Command", id="run_custom", variant="error")
                        yield Markdown(
                            "Use this only when the guided buttons do not cover your task. "
                            "This app intentionally funnels common workflows into safer actions."
                        )
            with TabPane("Logs", id="logs"):
                with Vertical(classes="panel"):
                    yield Static("Command Output", classes="title")
                    yield TextArea("", id="command_output", read_only=True)
                    yield Button("Clear Output", id="clear_output")
        yield Footer()

    async def on_mount(self) -> None:
        await self.push_screen(SplashScreen())
        self._refresh_everything()

    def _refresh_everything(self) -> None:
        self.uv_path = shutil.which("uv") or ""
        self._update_env_summary()
        self._update_project_summary()
        self._update_venv_help()

    def _project_root(self) -> Path:
        raw = self.query_one("#project_root", Input).value.strip() or str(Path.cwd())
        return Path(raw).expanduser().resolve()

    def _update_env_summary(self) -> None:
        python_path = shutil.which("python") or "not found"
        uv_state = self.uv_path if self.uv_path else "not installed or not on PATH"
        summary = (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Current folder: {Path.cwd()}\n"
            f"Python: {python_path}\n"
            f"uv: {uv_state}\n"
            f"Project marker files here: {', '.join(self._markers_in(Path.cwd())) or 'none'}"
        )
        self.query_one("#env_summary", Static).update(summary)

    def _markers_in(self, root: Path) -> list[str]:
        names = ["pyproject.toml", "uv.lock", ".venv", ".python-version"]
        return [name for name in names if (root / name).exists()]

    def _update_project_summary(self) -> None:
        root = self._project_root() if self.query("#project_root").first() else Path.cwd()
        markers = self._markers_in(root)
        status = "Looks like a uv project" if (root / "pyproject.toml").exists() else "Not initialized yet"
        summary = f"Root: {root}\nStatus: {status}\nMarkers: {', '.join(markers) or 'none'}"
        self.query_one("#project_summary", Static).update(summary)

    def _update_venv_help(self) -> None:
        if os.name == "nt":
            text = "Activate with: .venv\\Scripts\\activate"
        else:
            text = "Activate with: source .venv/bin/activate"
        self.query_one("#venv_help_text", Static).update(text)

    def _append_output(self, text: str) -> None:
        output = self.query_one("#command_output", TextArea)
        current = output.text
        output.load_text((current + "\n\n" + text).strip())

    def _require_uv(self) -> bool:
        if self.uv_path:
            return True
        self._append_output("uv was not found on PATH. Install it first from the Dashboard tab.")
        self.notify("uv not found", severity="error")
        return False

    @work(thread=True)
    def run_command(self, cmd: list[str], cwd: Path | None = None) -> None:
        result = self._execute(cmd, cwd=cwd)
        self.call_from_thread(self._append_output, result.combined)
        if result.ok:
            self.call_from_thread(self.notify, "Command completed", severity="information")
        else:
            self.call_from_thread(self.notify, "Command failed", severity="error")
        self.call_from_thread(self._refresh_everything)

    def _execute(self, cmd: list[str], cwd: Path | None = None) -> CommandResult:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            env=os.environ.copy(),
        )
        return CommandResult(cmd=cmd, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)

    def _safe_uv(self, *parts: str) -> list[str]:
        return [self.uv_path or "uv", *parts]

    def _run_uv(self, *parts: str, cwd: Path | None = None) -> None:
        if not self._require_uv():
            return
        self.run_command(self._safe_uv(*parts), cwd=cwd)

    @on(Button.Pressed, "#refresh_dashboard")
    def refresh_dashboard(self) -> None:
        self._refresh_everything()
        self.notify("Refreshed")

    @on(Button.Pressed, "#detect_project")
    def detect_project(self) -> None:
        self._update_project_summary()
        self.notify("Project status updated")

    @on(Button.Pressed, "#open_folder")
    def open_folder(self) -> None:
        path = str(self._project_root())
        if platform.system() == "Darwin":
            self.run_command(["open", path])
        elif os.name == "nt":
            self.run_command(["explorer", path])
        else:
            self.run_command(["xdg-open", path])

    @on(Button.Pressed, "#install_uv")
    def install_uv(self) -> None:
        if self.uv_path:
            self.notify("uv already appears to be installed")
            return
        system = platform.system()
        if system in {"Linux", "Darwin"}:
            self._append_output("Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        elif os.name == "nt":
            self._append_output(
                'Install uv with: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
            )
        else:
            self._append_output("Unknown platform. See the uv installation docs.")

    @on(Button.Pressed, "#wizard_init")
    def wizard_init(self) -> None:
        self.query_one("#project_name", Input).focus()
        self.notify("Fill in the fields on the Project tab, then click uv init")

    @on(Button.Pressed, "#run_init")
    def run_init(self) -> None:
        root = self._project_root()
        name = self.query_one("#project_name", Input).value.strip() or "my_app"
        desc = self.query_one("#project_desc", Input).value.strip()
        py = self.query_one("#project_python", Input).value.strip()
        root.mkdir(parents=True, exist_ok=True)
        cmd = self._safe_uv("init", "--package", "--name", name)
        if desc:
            cmd.extend(["--description", desc])
        if py:
            cmd.extend(["--python", py])
        cmd.append(str(root))
        self.run_command(cmd)

    @on(Button.Pressed, "#run_sync")
    def run_sync(self) -> None:
        self._run_uv("sync", cwd=self._project_root())

    @on(Button.Pressed, "#run_lock")
    def run_lock(self) -> None:
        self._run_uv("lock", cwd=self._project_root())

    @on(Button.Pressed, "#run_tree")
    def run_tree(self) -> None:
        self._run_uv("tree", cwd=self._project_root())

    @on(Button.Pressed, "#dep_add")
    def dep_add(self) -> None:
        pkg = self.query_one("#dependency_name", Input).value.strip()
        if not pkg:
            self.notify("Enter a dependency name", severity="warning")
            return
        self._run_uv("add", pkg, cwd=self._project_root())

    @on(Button.Pressed, "#dep_remove")
    def dep_remove(self) -> None:
        pkg = self.query_one("#dependency_name", Input).value.strip()
        if not pkg:
            self.notify("Enter a dependency name", severity="warning")
            return
        self._run_uv("remove", pkg, cwd=self._project_root())

    @on(Button.Pressed, "#project_run")
    def project_run(self) -> None:
        raw = self.query_one("#run_command", Input).value.strip()
        if not raw:
            self.notify("Enter a command to run", severity="warning")
            return
        self._run_uv("run", *raw.split(), cwd=self._project_root())

    @on(Button.Pressed, "#python_install")
    def python_install(self) -> None:
        version = self.query_one("#python_version", Input).value.strip() or "3.12"
        self._run_uv("python", "install", version)

    @on(Button.Pressed, "#python_list")
    def python_list(self) -> None:
        self._run_uv("python", "list")

    @on(Button.Pressed, "#python_find")
    def python_find(self) -> None:
        version = self.query_one("#python_version", Input).value.strip()
        parts = ["python", "find"] + ([version] if version else [])
        self._run_uv(*parts)

    @on(Button.Pressed, "#python_pin")
    def python_pin(self) -> None:
        version = self.query_one("#python_version", Input).value.strip() or "3.12"
        self._run_uv("python", "pin", version, cwd=self._project_root())

    @on(Button.Pressed, "#venv_create")
    def venv_create(self) -> None:
        path = self.query_one("#venv_path", Input).value.strip() or ".venv"
        self._run_uv("venv", path, cwd=self._project_root())

    @on(Button.Pressed, "#venv_help")
    def venv_help(self) -> None:
        self._update_venv_help()
        self.notify("Activation help updated")

    @on(Button.Pressed, "#tool_install")
    def tool_install(self) -> None:
        tool = self.query_one("#tool_name", Input).value.strip()
        if not tool:
            self.notify("Enter a tool name", severity="warning")
            return
        self._run_uv("tool", "install", tool)

    @on(Button.Pressed, "#tool_uninstall")
    def tool_uninstall(self) -> None:
        tool = self.query_one("#tool_name", Input).value.strip()
        if not tool:
            self.notify("Enter a tool name", severity="warning")
            return
        self._run_uv("tool", "uninstall", tool)

    @on(Button.Pressed, "#tool_list")
    def tool_list(self) -> None:
        self._run_uv("tool", "list")

    @on(Button.Pressed, "#tool_run")
    def tool_run(self) -> None:
        raw = self.query_one("#tool_run_cmd", Input).value.strip()
        if not raw:
            self.notify("Enter a tool command", severity="warning")
            return
        first, *rest = raw.split()
        self._run_uv("tool", "run", first, *rest)

    @on(Button.Pressed, "#pip_install")
    def pip_install(self) -> None:
        pkg = self.query_one("#pip_package", Input).value.strip()
        if not pkg:
            self.notify("Enter a package name", severity="warning")
            return
        self._run_uv("pip", "install", pkg, cwd=self._project_root())

    @on(Button.Pressed, "#pip_uninstall")
    def pip_uninstall(self) -> None:
        pkg = self.query_one("#pip_package", Input).value.strip()
        if not pkg:
            self.notify("Enter a package name", severity="warning")
            return
        self._run_uv("pip", "uninstall", pkg, cwd=self._project_root())

    @on(Button.Pressed, "#pip_list")
    def pip_list(self) -> None:
        self._run_uv("pip", "list", cwd=self._project_root())

    @on(Button.Pressed, "#pip_freeze")
    def pip_freeze(self) -> None:
        self._run_uv("pip", "freeze", cwd=self._project_root())

    @on(Button.Pressed, "#pip_tree")
    def pip_tree(self) -> None:
        self._run_uv("pip", "tree", cwd=self._project_root())

    @on(Button.Pressed, "#run_preset")
    def run_preset(self) -> None:
        list_view = self.query_one("#preset_list", ListView)
        if list_view.index is None:
            self.notify("Choose a preset first", severity="warning")
            return
        presets = [
            ["version"],
            ["self", "update"],
            ["cache", "dir"],
            ["cache", "clean"],
            ["tool", "list"],
            ["python", "list"],
        ]
        self._run_uv(*presets[list_view.index])

    @on(Button.Pressed, "#run_custom")
    def run_custom(self) -> None:
        raw = self.query_one("#custom_command", Input).value.strip()
        if not raw:
            self.notify("Enter a uv command", severity="warning")
            return
        parts = raw.split()
        if parts[0] == "uv":
            parts = parts[1:]
        self._run_uv(*parts, cwd=self._project_root())

    @on(Button.Pressed, "#clear_output")
    def clear_output(self) -> None:
        self.query_one("#command_output", TextArea).load_text("")


def main() -> None:
    UVManager().run()


if __name__ == "__main__":
    main()
