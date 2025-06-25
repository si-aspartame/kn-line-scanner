from pypylon import pylon

def list_all_node_names(camera, output_path="node_properties.txt"):
    nodemap = camera.GetNodeMap()
    nodes = nodemap.GetNodes()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("📋 ノード名一覧とプロパティ情報（最初の33件）\n\n")

        for i, node in enumerate(nodes[:33]):
            try:
                internal_node = node.GetNode()
                name = internal_node.GetName()
                f.write(f"--[{i}] {internal_node.Name}--\n")
                for p_name in internal_node.PropertyNames:
                    try:
                        property_value = internal_node.GetProperty(p_name)
                        f.write(f"{p_name} -> {property_value}\n")
                    except Exception as e_prop:
                        f.write(f"{p_name} -> 取得失敗: {e_prop}\n")
                f.write("\n")
            except Exception as e:
                f.write(f"⚠️ スキップ [{i}]: {e}\n")

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
list_all_node_names(camera)
camera.Close()
