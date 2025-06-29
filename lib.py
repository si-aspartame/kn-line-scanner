# lib.py
from typing import Tuple, Optional
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np
from pypylon import pylon, genicam

# 定数
INITIAL_SHRINK_RATIO = 0.2#最初に全体を何倍に縮小するか(計算軽量化)
SHRINK_STEP_RATIO = 0.9#毎回何倍に縦縮小するか
MAX_STEPS = 100#何回まで縦縮小してQR探すか

def shrink_until_readable(
    gray_img: np.ndarray,
    initial_shrink_ratio: float = INITIAL_SHRINK_RATIO,
    max_steps: int = MAX_STEPS
) -> Tuple[Optional[np.ndarray], Optional[list], float]:
    """
    グレースケール画像を入力として、QRが読めるまで縦方向に圧縮する。

    Parameters:
        gray_img (np.ndarray): 入力グレースケール画像
        initial_shrink_ratio (float): 全体縮小率（例: 0.2で20%に縮小）
        max_steps (int): 最大試行回数

    Returns:
        Tuple:
            - resized_img (np.ndarray): 読み取れた縮小画像（なければNone）
            - points (list): QRのpolygon座標（なければNone）
            - scale (float): 使用したスケール倍率（例: 0.81など）
    """
    if len(gray_img.shape) != 2:
        raise ValueError("gray_imgは2次元のグレースケール画像である必要があります")

    h, w = gray_img.shape
    h_small, w_small = int(h * initial_shrink_ratio), int(w * initial_shrink_ratio)
    img_small = cv2.resize(gray_img, (w_small, h_small), interpolation=cv2.INTER_AREA)

    scale = 1.0

    for step in range(max_steps):
        print(f"step:{step}, scale:{scale}")
        new_h = int(h_small * scale)
        if new_h < 10:
            break

        resized = cv2.resize(img_small, (w_small, new_h), interpolation=cv2.INTER_NEAREST)
        pil_img = Image.fromarray(resized)
        decoded_objs = decode(pil_img)

        if decoded_objs and len(decoded_objs[0].polygon) == 4:
            return resized, decoded_objs[0].polygon, scale

        scale *= SHRINK_STEP_RATIO

    return None, None, scale

def get_correction_factor(img: np.ndarray) -> Optional[float]:
    """
    QRコードの縦横比から補正倍率（縦スケーリング）を算出。

    Parameters:
        img (np.ndarray): グレースケール or カラー画像（OpenCV形式）

    Returns:
        Optional[float]: 補正に必要な縦方向のスケーリング倍率
                         QRが検出できない場合は None
    """
    gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized_img, points, scale = shrink_until_readable(gray)

    if resized_img is None or points is None:
        return None

    # アスペクト比から補正倍率を求める
    sorted_pts_y = sorted(points, key=lambda p: p.y)
    top_y = (sorted_pts_y[0].y + sorted_pts_y[1].y) / 2
    bottom_y = (sorted_pts_y[2].y + sorted_pts_y[3].y) / 2
    height = bottom_y - top_y

    sorted_pts_x = sorted(points, key=lambda p: p.x)
    left_x = (sorted_pts_x[0].x + sorted_pts_x[1].x) / 2
    right_x = (sorted_pts_x[2].x + sorted_pts_x[3].x) / 2
    width = right_x - left_x

    if width == 0:
        return None  # 0除算防止

    aspect = height / width
    correction_factor = 1.0 / aspect  # 縦横比1にするための補正
    correction_factor = round(scale * correction_factor, 5)  # 小数5桁まで丸め
    print(f"correction_factor -> {correction_factor}")
    return correction_factor

def get_linerate_node(camera) -> Optional[genicam.IFloat]:
    """
    ラインレートのノードを取得
    """
    try:
        node = camera.GetNodeMap().GetNode("AcquisitionLineRateAbs")
        if node is None:
            raise RuntimeError("ラインレートノードが見つかりません")
        return node
    except Exception as e:
        print(f"⚠️ ラインレートノード取得失敗: {e}")
        return None

def get_linerate(camera):
    try:
        camera.Open()
        linerate_node = get_linerate_node(camera)
        if linerate_node is None:
            print("⚠️ ラインレートノードが無効です。設定を中断します。")
            return None
        current_linerate = linerate_node.GetValue()
    except:
        current_linerate = None
    finally:
        if camera.IsOpen():
            camera.Close()
    return current_linerate


def set_linerate(camera, target_linerate: float):
    """
    カメラのラインレートを設定し、成功時は設定後のラインレートを返す

    Parameters:
        camera: Pylonカメラオブジェクト
        target_linerate (float): 設定したいラインレート値

    """
    try:
        camera.Open()
        linerate_node = get_linerate_node(camera)
        if linerate_node is None:
            print("⚠️ ラインレートノードが無効です。設定を中断します。")
            return

        current_linerate = linerate_node.GetValue()
        linerate_node.SetValue(target_linerate)
        updated_linerate = linerate_node.GetValue()
        print(f"✅ ラインレートを {current_linerate} -> {updated_linerate} lines/sec に設定しました")

    except Exception as e:
        print(f"⚠️ ラインレート設定エラー: {e}")

    finally:
        if camera.IsOpen():
            camera.Close()

    
