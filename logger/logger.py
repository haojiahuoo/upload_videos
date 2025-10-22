import os
import time
import threading
from functools import partial
from typing import Union, Optional, Tuple, Callable

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

_thread_local = threading.local()

def _ensure_device_id(device: Union[str, object]) -> str:
    if device is None:
        raise ValueError("设备ID不能为None")
    if isinstance(device, str):
        return device
    if hasattr(device, "serial"):
        serial = getattr(device, "serial")
        if serial:
            return str(serial)
    raise ValueError(f"无法从设备对象中获取序列号: {device}")

def set_default_device(device: Union[str, object, None]) -> None:
    if device is None:
        _thread_local.default_device = None
        return
    try:
        _thread_local.default_device = _ensure_device_id(device)
    except ValueError as e:
        raise RuntimeError(f"设置默认设备失败: {e}")

def get_current_device_id() -> Optional[str]:
    return getattr(_thread_local, "default_device", None)

def _resolve_device_id(device: Union[str, object, None]) -> Optional[str]:
    if device is not None:
        try:
            return _ensure_device_id(device)
        except Exception:
            # 如果这里抛异常，打印警告，返回字符串形式
            try:
                return str(device)
            except Exception:
                return None
    return get_current_device_id()

def _log(
    message: str,
    level: str,
    device: Union[str, object, None],
    print_console: bool
) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    device_id = _resolve_device_id(device)
    device_tag = f"[{device_id}]" if device_id else ""
    log_line = f"{timestamp} [{level.upper()}]{device_tag} {message}"
    if print_console:
        print(log_line)
    try:
        log_file = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"⚠️ 日志写入失败: {e} | 原日志: {log_line}")

def log(
    message: str,
    device: Union[str, object, None] = None,
    level: str = "INFO",
    print_console: bool = True
) -> None:
    _log(message, level, device, print_console)

def log_error(
    message: str,
    device: Union[str, object, None] = None,
    print_console: bool = True
) -> None:
    _log(message, "ERROR", device, print_console)

def log_debug(
    message: str,
    device: Union[str, object, None] = None,
    print_console: bool = True
) -> None:
    _log(message, "DEBUG", device, print_console)

def bind_logger(device: Union[str, object]) -> Tuple[Callable, Callable, Callable]:
    device_id = _ensure_device_id(device)
    return (
        partial(log, device=device_id),
        partial(log_error, device=device_id),
        partial(log_debug, device=device_id)
    )
