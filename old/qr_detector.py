import cv2
import numpy as np
import glob
import os
from pyzbar.pyzbar import decode
from PIL import Image

# 定数
SHRINK_RATIO = 0.2            # 全体の初期縮小率
OUTPUT_DIR = "./qr_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compute_aspect(points):
    """QRコードのbounding boxから縦横比を計算する"""
    sorted_pts = sorted(points, key=lambda p: p.y)
    top_y = (sorted_pts[0].y + sorted_pts[1].y) / 2
    bottom_y = (sorted_pts[2].y + sorted_pts[3].y) / 2
    height = bottom_y - top_y

    sorted_pts_x = sorted(points, key=lambda p: p.x)
    left_x = (sorted_pts_x[0].x + sorted_pts_x[1].x) / 2
    right_x = (sorted_pts_x[2].x + sorted_pts_x[3].x) / 2
    width = right_x - left_x

    if width == 0:
        return float('inf')

    return height / width

# 対象画像一覧
image_paths = sorted(glob.glob('./qr_sample/*.png'))

for img_path in image_paths:
    filename = os.path.splitext(os.path.basename(img_path))[0]
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f'❌ 読み込み失敗: {img_path}')
        continue

    h, w = img.shape
    h_small, w_small = int(h * SHRINK_RATIO), int(w * SHRINK_RATIO)
    img_small = cv2.resize(img, (w_small, h_small), interpolation=cv2.INTER_AREA)

    decoded = False
    aspect = None
    scale = 1.0

    # --- QR読み取り ---
    transformed = img_small.copy()
    for i in range(100):  # 最大20回だけ試す
        new_h = int(h_small * scale)
        transformed = cv2.resize(img_small, (w_small, new_h), interpolation=cv2.INTER_NEAREST)
        decoded_objs = decode(Image.fromarray(transformed))
        if decoded_objs:
            points = decoded_objs[0].polygon
            aspect = compute_aspect(points)
            decoded = True
            break
        scale *= 0.9

    if not decoded:
        print(f"❌ {filename}: QR読み取り失敗")
        continue

    # --- 元画像からaspectに基づいて再生成＆保存 ---
    final_h = int(h * (1 / aspect))  # aspectが大きいほど縮める（縦に伸びてたということ）
    output_img = cv2.resize(img, (w, final_h), interpolation=cv2.INTER_AREA)
    output_path = os.path.join(OUTPUT_DIR, f"{filename}_adjusted.png")
    cv2.imwrite(output_path, output_img)

    print(f"\n📂 {filename} ✅ QR読み取り成功 & 画像保存 → {output_path}")
    print(f"📐 検出縦横比: {aspect:.3f} → 補正率: {1 / aspect:.4f}")
