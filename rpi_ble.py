import time
from bluepy.btle import Peripheral, UUID, DefaultDelegate, Scanner
from bluepy.btle import Characteristic
import threading
# --- REPLACE THESE WITH YOUR ACTUAL VALUES ---
# TARGET_DEVICE_NAME = "Your BLE Device Name"  # The name of your BLE peripheral in nRF Connect
SERVICE_UUID = UUID(0x180D)      # Replace with your service UUID
CHARACTERISTIC_UUID = UUID(0x2A37) # Replace with the UUID of the characteristic that sends notifications/indications

def notification_loop(peripheral, characteristic):
    while True:
        time.sleep(0.2)
        print('', end='', flush=True)
        try:
            if peripheral.waitForNotifications(1.0):
                continue
        except Exception as e:
            print(f"error:{e}")
            pass



def interactive_cccd(peripheral, characteristic):
    state = True
    while True:
        user_input = input("Enter 'n' to enable notifications, 'd' to disable, or 'q' to quit: ")
        if user_input.lower() == 'n':
            if not state:
                try:
                    cccd_handle = characteristic.getHandle() + 1
                    peripheral.writeCharacteristic(cccd_handle, b'\x01\x00', withResponse=True)
                    state=True
                    print("Notifications enabled.")
                except Exception as e:
                    print(f"Error enabling notifications: {e}")
        elif user_input.lower() == 'd':
            if state:
                try:
                    cccd_handle = characteristic.getHandle() + 1
                    peripheral.writeCharacteristic(cccd_handle, b'\x00\x00', withResponse=True)
                    state=False
                    print("Notifications or Indication disabled.")
                except Exception as e:
                    print(f"Error disabling notifications: {e}")
        #elif user_input.lower() == 'i':
        #    if not (2 & state):
         #       try:
          #          cccd_handle = characteristic.getHandle() + 1
           #         peripheral.writeCharacteristic(cccd_handle, b'\x02\x00', withResponse=True)
            #        state=2
             #       print("Indication enabled.")
              #  except Exception as e:
               #     print(f"Error enabling indications: {e}")
        elif user_input.lower() == 'q':
            break  # Exit the loop
        else:
            print("Invalid input.")



class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        start='\033[96m'
        ENDC = '\033[0m'
        print(f"{start}Received notification: {data.hex()} (handle: {cHandle}){ENDC}")



def connect_and_subscribe(device_addr):
    print(f"Connecting to {device_addr}...")
    try:
        p = Peripheral(device_addr, 'random')  # No timeout here, let it handle connection issues
        p.withDelegate(MyDelegate())

        print("Discovering services...")
        services = p.getServices()
        for service in services:
            print(f"service: {service}")
            if service.uuid == SERVICE_UUID:
                print(f"Found service: {service.uuid}")
                characteristics = service.getCharacteristics(forUUID=CHARACTERISTIC_UUID)
                if characteristics:
                    characteristic = characteristics[0]  # Assuming one characteristic with this UUID
                    print(f"Found characteristic: {characteristic.uuid}, handle: {characteristic.getHandle()}")


                    print(f"properties:{characteristic.properties}")
                    print(f"all propertis in CHAR....:{Characteristic.props}")
                    support_notify=characteristic.properties & Characteristic.props["NOTIFY"]
                    support_indicate=characteristic.properties & Characteristic.props["INDICATE"]
                    support_write=characteristic.properties & Characteristic.props["WRITE"]
                    support_write_no_resp=characteristic.properties & Characteristic.props["WRITE_NO_RESP"]


                    if support_notify or support_indicate or support_write or support_write_no_resp: # check notify, indicate, write, write without response property
                        if characteristic.supportsRead():
                            print(f"initial value:{characteristic.read().hex()}")

                        cccd_handle = characteristic.getHandle() + 1
                        print(f"CCCD handle: {cccd_handle}")

                        # Enable notifications/indications
                        if support_indicate: # check indicate property
                            #p.writeCharacteristic(cccd_handle, b"\x02\x00", withResponse=True)
                            pass

                        elif support_notify: # check notify property
                            p.writeCharacteristic(cccd_handle, b"\x01\x00", withResponse=True)

                        notification_thread = threading.Thread(target=notification_loop, args=(p, characteristic), daemon=True) # daemon thread will close when the main thread exits
                        notification_thread.start()

                        interactive_thread = threading.Thread(target=interactive_cccd, args=(p, characteristic))
                        interactive_thread.start()


            # Main thread waits for the interactive thread to finish (when the user enters 'q')
                        interactive_thread.join()



                    else:
                        print(f"characteristic {CHARACTERISTIC_UUID} doesn't support notify, indicate, write or write without response property")



                else:
                    print(f"Characteristic {CHARACTERISTIC_UUID} not found in service {service.uuid}")

                return p  # Return the peripheral object to keep the connection alive


        print(f"Service {SERVICE_UUID} not found.")
        return None

    except Exception as e:
        print(f"Connection error: {e}")
        return None


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)

def connect_get_addr():
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(5.0)
    n = 0
    addr = []
    mm = {}
    for dev in devices:
        print("%d: Device %s (%s), RSSI=%d dB" % (n, dev.addr, dev.addrType, dev.rssi))
        if dev.getValueText(9):
            mm[dev.getValueText(9)]=n
        addr.append(dev.addr)
        n += 1
        for (adtype, desc, value) in dev.getScanData():
            print(" %s = %s" % (desc, value))
    print(mm)
    number = input('Enter your device number: ')
    print('Device', number)
    num = int(number)
    return addr[num]

if __name__ == "__main__":

    try:
        addr = connect_get_addr()
        if True:
            peripheral = connect_and_subscribe(addr)
            if peripheral:
                try:
                    while True:
                        time.sleep(1)
                        # Add any other periodic tasks here if needed

                except KeyboardInterrupt:
                    print("\nExiting...")

                finally:
                    peripheral.disconnect()
                    print("Disconnected.")

    except Exception as e:
        print(f"Error: {e}")
