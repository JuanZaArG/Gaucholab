"""Background execution helpers using ThreadPoolExecutor."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Optional

from PySide6.QtCore import QObject, Signal

ExecutorCallable = Callable[..., Any]
UICallback = Optional[Callable[[Any], None]]


class _Dispatcher(QObject):
    completed = Signal(object, object)


_dispatcher = _Dispatcher()
_executor = ThreadPoolExecutor(max_workers=8)


def _handle_completed(callback: Callable[[Any], None], result: Any) -> None:
    if callback:
        callback(result)


_dispatcher.completed.connect(_handle_completed)


def run_in_executor(func: ExecutorCallable, *args, ui_callback: UICallback = None) -> Future:
    """Run func(*args) in the shared executor and optionally deliver result on UI thread."""

    def _done(future: Future) -> None:
        if ui_callback is None:
            return
        try:
            result = future.result()
        except Exception as exc:  # pragma: no cover - surface errors in UI
            result = exc
        _dispatcher.completed.emit(ui_callback, result)

    future = _executor.submit(func, *args)
    future.add_done_callback(_done)
    return future
