import ctypes
from ctypes import wintypes
import sys

OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
kernel32.CreateFileW.restype = wintypes.HANDLE

kernel32.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
kernel32.ReadFile.restype = wintypes.BOOL

device_path = r"\\.\PhysicalDrive0"

h_device = kernel32.CreateFileW(
    device_path, 
    0,                      # ВОЗВРАЩЕНО: Права доступа 0
    0x00000001 | 0x00000002,
    None, 
    OPEN_EXISTING, 
    FILE_ATTRIBUTE_NORMAL, 
    None
)

if h_device != INVALID_HANDLE_VALUE:
    print(f"ЭКСПЕРИМЕНТ Б: Дескриптор получен с правами 0. HANDLE = {hex(h_device)}")
    
    # Попытка прочитать загрузочный сектор MBR
    print("Попытка прямого чтения 512 байт через ReadFile...")
    raw_sector = ctypes.create_string_buffer(512)
    read_bytes = wintypes.DWORD(0)
    res = kernel32.ReadFile(h_device, raw_sector, 512, ctypes.byref(read_bytes), None)
    
    print(f"Результат ReadFile: {bool(res)}")
    print(f"Код ошибки Win32: {ctypes.get_last_error()}")
    
    kernel32.CloseHandle(h_device)
else:
    print(f"Ошибка открытия: {ctypes.get_last_error()}")
