import ubluetooth

ble = ubluetooth.BLE()

ble.active(True)

print(ble.config('mac'))