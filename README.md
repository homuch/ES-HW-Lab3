# Embedded Systems Lab 3: BLE Communication using Python

This repository contains the solution to **Lab 3: BLE Communication**. The project demonstrates BLE communication between a **Python BLE program (BLE Central)** running on a **Linux host (Raspberry Pi 3)** and a **BLE test app** running on an Android phone.

---

## Problem Statement

Create a Python BLE program on a Linux host (Raspberry Pi 3) that acts as a **BLE Central** to communicate with a test app (e.g., **BLE Tool**). Your task is to interact with the app by setting the **Client Characteristic Configuration Descriptor (CCCD)** value to `0x0002` (Notifications enabled). 

**Note:**  
Due to the limitations of the **"BLE Tool"** app, the CCCD value might not change visibly in the app’s UI. To validate your solution, you can use **server logs from the BLE Tool** app or a similar app, such as **BLE Scanner by Bluepixel**. iPhone users can find alternative apps with similar functionality.


