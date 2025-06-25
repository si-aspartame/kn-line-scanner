import cv2
import numpy as np

image_path = "7.png"
img = cv2.imread(image_path)
detector = cv2.QRCodeDetector()

scale = 1.0
step = 0.05
max_scale = 10.0  # 念のため上限

print("📈 読めなくなるギリギリを探すよ...")

while scale <= max_scale:
    new_height = int(img.shape[0] * scale)
    resized = cv2.resize(img, (img.shape[1], new_height), interpolation=cv2.INTER_LINEAR)

    retval, decoded_info, points, _ = detector.detectAndDecodeMulti(resized)

    if retval and any(info.strip() for info in decoded_info):
        print(f"✅ OK: スケール {scale:.2f} -> {decoded_info[0]}")
        scale += step
    else:
        print(f"❌ 読めなくなった: スケール {scale:.2f}")
        cv2.imwrite(f"fail_at_scale_{scale:.2f}.png", resized)
        break
