from pypylon import pylon, genicam

# セットしたい各ノードの目標値
TARGET_PARAMS = {
    "GainAuto": "Off",
    "GainRaw": 256,
    "BlackLevelRaw": 50,
    "GammaEnable": False,
    "GammaSelector": "User",  # 例: "User" or "sRGB"
    "Gamma": 1.0
}
def set_camera_parameters_forcefully(camera, param_dict):
    nodemap = camera.GetNodeMap()
    print("💥 SetValue 実行中...")

    for param, value in param_dict.items():
        try:
            node = nodemap.GetNode(param)
            current_value = node.GetValue()
            print(f"{param} の 現在の値:{current_value}")
            if value != current_value:
                node.SetValue(value)
                print(f"✅ {param} を {current_value} -> {value} に強制設定完了")
        except Exception as e:
            print(f"⚠️ {param} の設定失敗: {e}")
    print("設定完了！")

if __name__ == "__main__":
    cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    cam.Open()
    set_camera_parameters_forcefully(cam, TARGET_PARAMS)
    cam.Close()