from pypylon import pylon

def read_node_value(camera, node_name):
    try:
        nodemap = camera.GetNodeMap()
        node = nodemap.GetNode(node_name)
        if node:
            print(f"{node_name}: {node.GetValue()}")
        else:
            print(f"{node_name} は存在しません")
    except Exception as e:
        print(f"❌ {node_name} の取得エラー: {e}")

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

for name in [
    "AcquisitionLineRateAbs",
    "ResultingLineRateAbs",
    "ResultingLinePeriodAbs",
    "ResultingFrameRateAbs",
    "Height"# FrameGrabberPool
]:
    read_node_value(camera, name)

camera.Close()
