from pypylon import pylon

factory = pylon.TlFactory.GetInstance()
devices = factory.EnumerateDevices()

print(f"🔍 接続カメラ数: {len(devices)}")

if devices:
    cam = pylon.InstantCamera(factory.CreateDevice(devices[0]))
    cam.Open()
    print("📷 接続成功:", cam.GetDeviceInfo().GetModelName())
    cam.Close()
else:
    print("⚠️ カメラが見つかりません…🥲")
