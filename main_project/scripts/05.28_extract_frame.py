import cv2
import pandas as pd
import os

# 원본 영상 경로
video_path = "../data/samples/Ran.1985_sample.mp4"
out_dir = "../data/frames/"
os.makedirs(out_dir, exist_ok=True)

# 필요한 sec(초)만 추출
df = pd.read_csv("../data/results/main_character_tracking.csv")
secs_needed = sorted(set(df['sec'].astype(int).tolist()))

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

for sec in secs_needed:
    frame_num = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    if ret:
        out_path = f"{out_dir}/frame_{sec:04d}.jpg"
        cv2.imwrite(out_path, frame)
    else:
        print(f"프레임 추출 실패: {sec}s ({frame_num}번째 프레임)")
cap.release()
