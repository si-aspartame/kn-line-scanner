import cv2
import numpy as np
import time
from pypylon import pylon

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

images = []
num_frames = 10

print(f"📸 {num_frames}枚の撮像を開始...")

start_time = time.time()

for i in range(num_frames):
    t0 = time.time()
    grab = camera.GrabOne(500)
    print(grab.Array.shape)
    t1 = time.time()
    
    img = grab.Array
    images.append(img)

    print(f"  🔹 [{i+1}] Grab + append: {t1 - t0:.4f} sec")

end_time = time.time()
total_time = end_time - start_time

camera.Close()

# 結合して保存
stacked = np.vstack(images)
cv2.imwrite("stacked.png", stacked)

print(f"\n✅ 合計処理時間: {total_time:.4f} 秒")
print(f"🧮 平均: {total_time / num_frames:.4f} 秒/枚")
