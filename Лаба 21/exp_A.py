import ctypes
from ctypes import wintypes
import sys

OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
]
kernel32.CreateFileW.restype = wintypes.HANDLE

device_path = r"\\.\PhysicalDrive0"
print(f"ЭКСПЕРИМЕНТ А: Открытие {device_path} с правами GENERIC_READ (0x80000000)")

h_device = kernel32.CreateFileW(
    device_path,
    0x80000000,             # ИЗМЕНЕНО: Права доступа GENERIC_READ
    0x00000001 | 0x00000002,
    None,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    None
)

if h_device == INVALID_HANDLE_VALUE:
    print(f"[ОШИБКА] Не удалось получить дескриптор. Код ошибки Win32: {ctypes.get_last_error()}")
    sys.exit(1)

print(f"[УСПЕХ] Дескриптор получен! HANDLE = {hex(h_device)}")
kernel32.CloseHandle(h_device)
