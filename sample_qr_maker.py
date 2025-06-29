import os
import cv2
import numpy as np
import qrcode
import random
from PIL import Image
from tqdm import tqdm

# 保存フォルダ作成
output_dir = './qr_sample'
os.makedirs(output_dir, exist_ok=True)
n_samples = 10

# 背景画像読み込み（グレースケール）
base_img = cv2.imread('./stacked.png', cv2.IMREAD_GRAYSCALE)
if base_img is None:
    raise FileNotFoundError("背景画像が読み込めません")

h_img, w_img = base_img.shape

# 100回ループ
for i in tqdm(range(n_samples)):
    # === QRコード生成 ===
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data("kanai")  # 固定でOK／毎回ランダムでもOK
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")
    qr_np = np.array(qr_img)

    # === 正方形にリサイズ ===
    scale_w = random.uniform(0.1, 0.9)
    target_w = int(w_img * scale_w)
    qr_square = cv2.resize(qr_np, (target_w, target_w), interpolation=cv2.INTER_NEAREST)

    # === 貼り付け位置とストレッチ倍率 ===
    max_y_offset = h_img - int(target_w * 2.5)
    if max_y_offset < 1:
        continue  # 小さすぎて貼れない場合はスキップ

    x_offset = random.randint(0, w_img - target_w)
    y_offset = random.randint(0, max_y_offset)

    max_stretch = (h_img - y_offset) / target_w
    stretch_factor = random.uniform(2.5, min(10.0, max_stretch))
    target_h = int(target_w * stretch_factor)

    # === 縦ストレッチ処理 ===
    qr_stretched = cv2.resize(qr_square, (target_w, target_h), interpolation=cv2.INTER_NEAREST)

    # === ROI取得（resize結果のサイズで！）===
    h_qr, w_qr = qr_stretched.shape
    roi = base_img[y_offset:y_offset+h_qr, x_offset:x_offset+w_qr]

    # === マスク合成 ===
    overlay = base_img.copy()
    mask = qr_stretched < 128
    if roi.shape != mask.shape:
        continue  # サイズ不一致が発生したら飛ばす

    roi_blended = roi.copy()
    roi_blended[mask] = ((roi[mask].astype(np.uint16) * 0.5)).astype(np.uint8)

    overlay[y_offset:y_offset+h_qr, x_offset:x_offset+w_qr] = roi_blended

    # === 保存 ===
    filename = os.path.join(output_dir, f'qr_{i:03d}.png')
    cv2.imwrite(filename, overlay)

print(f"✅ 完了:{n_samples}枚のQR画像が ./qr_sample に保存されたよ！")
