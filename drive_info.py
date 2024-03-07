import wmi

def get_physical_drive_type():
    c = wmi.WMI()
    physical_drives = c.Win32_DiskDrive()
    drive_info = []
    for drive in physical_drives:
        drive_info.append({
            'device_id': drive.DeviceID,
            'model': drive.Model,
            'interface_type': drive.InterfaceType,
        })

    return drive_info

if __name__ == "__main__":
    drives = get_physical_drive_type()

    if drives:
        print("Physical Drive Information:")
        for drive in drives:
            print(f"Device ID: {drive['device_id']}, Model: {drive['model']}, Interface Type: {drive['interface_type']}")
    else:
        print("No physical drives found.")
