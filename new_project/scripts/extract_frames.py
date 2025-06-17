import cv2
import numpy as np
from collections import defaultdict
from ultralytics import YOLO
from tqdm import tqdm
import os
import pandas as pd

# 설정값
start_time = 109  # seconds
end_time = 349    # seconds

# 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
output_candidates_dir = os.path.join(script_dir, "..", "data", "results", "candidates")
os.makedirs(output_candidates_dir, exist_ok=True)

track_samples = defaultdict(list)
results_data = []

weights_path = os.path.join(script_dir, "yolo11_jde/weights/YOLO11s_JDE-CHMOT17-64b-100e_TBHS_m075_1280px.pt")
video_path_relative = os.path.join("..", "data", "raw", "Cure_1997.mp4")
video_path_absolute = os.path.join(script_dir, video_path_relative)

model = YOLO(weights_path, task="jde")
cap = cv2.VideoCapture(video_path_absolute)

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps
track_history = defaultdict(lambda: [])

print(f"영상 FPS: {fps}, 총 프레임: {total_frames}, 총 길이: {duration:.2f}초")

# 유효 시간 범위 내에서만 처리
assert 0 <= start_time < end_time <= duration, "시간 범위가 잘못되었습니다."

with tqdm(total=(end_time - start_time), desc="1초 단위 샘플링", unit="sec") as pbar:
    sec = start_time
    while sec < end_time:
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = cap.read()
        if not success:
            print(f"[경고] {sec}초에서 프레임을 읽을 수 없음")
            break

        try:
            results = model.track(
                frame,
                tracker="smiletrack.yaml",
                persist=True,
                verbose=False
            )
        except Exception as e:
            print(f"[에러] YOLO 추적 실패 @ {sec}s: {e}")
            sec += 1
            pbar.update(1)
            continue

        boxes = results[0].boxes.xywh.cpu()
        track_ids_raw = results[0].boxes.id
        track_ids = track_ids_raw.int().cpu().tolist() if track_ids_raw is not None else []

        annotated_frame = results[0].plot()

        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))
            if len(track) > 30:
                track.pop(0)

            # 트랙 궤적 시각화 (선택)
            try:
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
            except Exception:
                pass  # 잘못된 좌표가 있을 경우 무시

            # 크롭 영역
            l, t = int(x - w / 2), int(y - h / 2)
            r, b = int(x + w / 2), int(y + h / 2)
            crop = frame[t:b, l:r] if l >= 0 and t >= 0 and r > l and b > t else None

            if crop is not None and crop.size > 0 and len(track_samples[track_id]) < 20:
                track_samples[track_id].append((sec, crop))

            results_data.append({
                "sec": int(sec),
                "track_id": int(track_id),
                "x": float(x),
                "y": float(y),
                "w": float(w),
                "h": float(h)
            })

        # 실시간 디버깅용 화면 표시 (GUI 없는 서버에서는 주석)
        # cv2.imshow("YOLO11 Tracking", annotated_frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

        sec += 1
        pbar.update(1)

cap.release()
cv2.destroyAllWindows()

# 샘플 이미지 저장
for track_id, samples in track_samples.items():
    n = len(samples)
    if n == 0:
        continue
    indices = [0, n // 2, n - 1] if n >= 3 else list(range(n))
    for i, idx in enumerate(indices):
        sec, crop = samples[idx]
        fname = os.path.join(output_candidates_dir, f"track_{track_id}_sample_{i+1}_sec_{int(sec)}.jpg")
        cv2.imwrite(fname, crop)

# 결과 CSV 저장
df = pd.DataFrame(results_data)
output_csv_path = os.path.join(script_dir, "..", "data", "results", "all_tracking_results_1.csv")
df.to_csv(output_csv_path, index=False)
print(f"전체 추적 결과 csv 저장 완료: {output_csv_path}")
