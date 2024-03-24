from wmi import WMI
def get_physical_drives_windows():
    c = WMI()
    physical_drives = c.Win32_DiskDrive()
    drive_info = []
    for drive in physical_drives:
        drive_info.append({
            'Name': drive.Name,
            'model': drive.Model,
            'interface_type': drive.InterfaceType,
        })
    return drive_info

print(get_physical_drives_windows())