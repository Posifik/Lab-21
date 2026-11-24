import ctypes
from ctypes import wintypes
import sys

# --- КОНСТАНТЫ WINDOWS API ---
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

# 32-битный управляющий код IOCTL_DISK_GET_DRIVE_GEOMETRY
IOCTL_DISK_GET_DRIVE_GEOMETRY = 0x00070000

MEDIA_TYPES = {
    0: "Unknown (Неизвестный тип)",
    11: "RemovableMedia (Съемный носитель / Флешка)",
    12: "FixedMedia (Фиксированный жесткий диск / SSD)"
}

class DISK_GEOMETRY(ctypes.Structure):
    _fields_ = [
        ("Cylinders", ctypes.c_int64),
        ("MediaType", ctypes.c_int),
        ("TracksPerCylinder", wintypes.DWORD),
        ("SectorsPerTrack", wintypes.DWORD),
        ("BytesPerSector", wintypes.DWORD),
    ]

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
]
kernel32.CreateFileW.restype = wintypes.HANDLE

kernel32.DeviceIoControl.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p
]
kernel32.DeviceIoControl.restype = wintypes.BOOL

# ИСПРАВЛЕНО: Правильный префикс пространства имен устройств Windows (\\.\)
device_path = r"\\.\PhysicalDrive0"
print(f"[RING 3] Попытка открыть символическую ссылку устройства: {device_path}")

h_device = kernel32.CreateFileW(
    device_path,
    0,                      # Права доступа: 0 
    0x00000001 | 0x00000002,
    None,
    OPEN_EXISTING,
    FILE_ATTRIBUTE_NORMAL,
    None
)

if h_device == INVALID_HANDLE_VALUE:
    print(f"[ОШИБКА ЯДРА] Не удалось открыть устройство. Код ошибки Win32: {ctypes.get_last_error()}")
    sys.exit(1)

print(f"[УСПЕХ] Дескриптор драйвера получен! HANDLE = {hex(h_device)}")

geometry = DISK_GEOMETRY()
bytes_returned = wintypes.DWORD(0)

print(f"[I/O MANAGER] Отправляем пакет IRP с кодом IOCTL {hex(IOCTL_DISK_GET_DRIVE_GEOMETRY)}...")

success = kernel32.DeviceIoControl(
    h_device,
    IOCTL_DISK_GET_DRIVE_GEOMETRY,
    None, 0,
    ctypes.byref(geometry),
    ctypes.sizeof(geometry),
    ctypes.byref(bytes_returned),
    None
)

if not success:
    print(f"[ОШИБКА ДРАЙВЕРА] Сбой DeviceIoControl. Код ошибки Win32: {ctypes.get_last_error()}")
    kernel32.CloseHandle(h_device)
    sys.exit(1)

print(f"[УСПЕХ] Драйвер вернул {bytes_returned.value} байт аппаратной конфигурации:\n")
print(f"  Тип носителя (MediaType):     {MEDIA_TYPES.get(geometry.MediaType, geometry.MediaType)}")
print(f"  Количество цилиндров:         {geometry.Cylinders}")
print(f"  Дорожек на цилиндр:           {geometry.TracksPerCylinder}")
print(f"  Секторов на дорожку:          {geometry.SectorsPerTrack}")
print(f"  Размер физического сектора:   {geometry.BytesPerSector} байт")

total_bytes = (geometry.Cylinders * geometry.TracksPerCylinder * geometry.SectorsPerTrack * geometry.BytesPerSector)
print(f"  Расчетный объем устройства:   {total_bytes / (1024**3):.2f} ГБ")

kernel32.CloseHandle(h_device)
print("\n[СИСТЕМА] Дескриптор устройства закрыт.")
