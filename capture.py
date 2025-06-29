# capture.py
import cv2
import numpy as np
import time
from pypylon import pylon
from lib import get_linerate, set_linerate, get_correction_factor

DEFAULT_LINERATE = 5000
NUM_FRAMES = 100  # ラインレート5000だとこれで5秒
OUTPUT_FILE_NAME = "stacked.png"

def acquire_images(camera, num_frames):
    camera.Open()
    print(f"""Width:{camera.Width.GetValue()}, Height:{camera.Height.GetValue()}, PixelFormat:{camera.PixelFormat.GetValue()}""")

    images = []
    print(f"📸 {num_frames}枚の連続撮像を開始...")

    start_time = time.time()
    camera.StartGrabbingMax(num_frames)

    i = 0
    while camera.IsGrabbing():
        t0 = time.time()
        grab = camera.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)
        if grab.GrabSucceeded():
            img = grab.Array
            images.append(img)
            t1 = time.time()
            print(f"  🔹 [{i+1}] Grab + append: {t1 - t0:.4f} sec")
            i += 1
        grab.Release()
    camera.StopGrabbing()
    camera.Close()

    end_time = time.time()
    total_time = end_time - start_time
    return images, total_time

def get_stacked_image(images):
    return np.vstack(images)

def main():
    #初期設定＋初期ラインレート保存
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    set_linerate(camera, DEFAULT_LINERATE)#ラインレート5000で初期化
    linerate = get_linerate(camera)
    if linerate is None:
        print("⚠️ 現在のラインレート取得に失敗しました。")
        return
    
    #画像取得＋保存
    images, total_time = acquire_images(camera, NUM_FRAMES)
    stacked = get_stacked_image(images)
    print(f"\n✅ 合計処理時間: {total_time:.4f} 秒")
    print(f"🧮 平均: {total_time / NUM_FRAMES:.4f} 秒/枚")
    cv2.imwrite(OUTPUT_FILE_NAME, stacked)
    print(f"🖼️ 画像保存: {OUTPUT_FILE_NAME} ({stacked.shape})")

    #img = cv2.imread("./qr_sample/qr_001.png", cv2.IMREAD_GRAYSCALE)#本来はstackedをそのまま使うけど、今はQRコード撮影できてないのでサンプルを利用
    img = stacked
    correction_factor = get_correction_factor(img)
    if correction_factor is None:
        print("⚠️ QRコードの読み込み、および補正率の取得に失敗しました。ラインレートは変更しません。")
        return
    corrected_linerate = linerate * correction_factor
    set_linerate(camera, corrected_linerate)
    return

if __name__ == "__main__":
    main()
