from pypylon import pylon

#MAX_LINE_RATE = 80645
TARGET_LINE_RATE = 5000  # 設定したいラインレート（lines/sec）

def get_current_linerate_value(linerate_node):
    return linerate_node.GetValue()

def get_linerate_node(camera):
    try:
        node = camera.GetNodeMap().GetNode("AcquisitionLineRateAbs")
    except:
        print(f"ラインレートのノード取得中に例外")
    return node

def set_linerate(camera):
    try:
        camera.Open()
        linerate_node = get_linerate_node(camera)
        print(get_current_linerate_value(linerate_node))

        linerate_node.SetValue(TARGET_LINE_RATE)
        print(f"✅ ラインレートを {TARGET_LINE_RATE} lines/sec に設定しました")

    except Exception as e:
        print(f"⚠️ エラー: {e}")
    finally:
        if camera.IsOpen():
            camera.Close()

if __name__ == "__main__":
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    set_linerate(camera)
