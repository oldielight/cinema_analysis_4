#!/usr/bin/env python3
import json
from collections import defaultdict

def parse_duration(duration_str):
    """Parse duration string like '0:00:11.68' to seconds"""
    try:
        time_parts = duration_str.split(':')
        if len(time_parts) == 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = float(time_parts[2])
            return hours * 3600 + minutes * 60 + seconds
        return 0
    except:
        return 0

def format_time(seconds):
    """Convert seconds to readable time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"

def analyze_scenes_shots():
    """Analyze scenes and shots data from Azure JSON"""
    
    with open('azure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    video = data['videos'][0]
    insights = video['insights']
    scenes = insights['scenes']
    shots = insights['shots']
    
    print("🎬 씬(Scene) & 샷(Shot) 상세 분석")
    print("=" * 60)
    
    # 1. 씬 분석
    print("🎭 씬(Scene) 분석:")
    print(f"  총 씬 수: {len(scenes)}")
    
    scene_durations = []
    total_duration = 0
    
    print("  씬별 상세 정보:")
    for i, scene in enumerate(scenes):
        scene_id = scene['id']
        instances = scene['instances']
        
        if instances:
            instance = instances[0]
            start_time = parse_duration(instance['start'])
            end_time = parse_duration(instance['end'])
            duration = end_time - start_time
            scene_durations.append(duration)
            total_duration += duration
            
            print(f"    씬 {scene_id:2d}: {format_time(start_time)} - {format_time(end_time)} "
                  f"(길이: {duration:.1f}초)")
    
    # 씬 통계
    if scene_durations:
        avg_scene_duration = sum(scene_durations) / len(scene_durations)
        max_scene_duration = max(scene_durations)
        min_scene_duration = min(scene_durations)
        
        print(f"\n  씬 통계:")
        print(f"    평균 씬 길이: {avg_scene_duration:.1f}초")
        print(f"    최장 씬: {max_scene_duration:.1f}초")
        print(f"    최단 씬: {min_scene_duration:.1f}초")
        print(f"    총 영상 길이: {total_duration:.1f}초")
    
    print()
    
    # 2. 샷 분석
    print("📷 샷(Shot) 분석:")
    print(f"  총 샷 수: {len(shots)}")
    
    shot_durations = []
    shots_per_scene = defaultdict(int)
    keyframes_count = 0
    
    print("  첫 10개 샷 정보:")
    for i, shot in enumerate(shots[:10]):
        shot_id = shot['id']
        instances = shot['instances']
        keyframes = shot.get('keyFrames', [])
        keyframes_count += len(keyframes)
        
        if instances:
            instance = instances[0]
            start_time = parse_duration(instance['start'])
            end_time = parse_duration(instance['end'])
            duration = end_time - start_time
            shot_durations.append(duration)
            
            # 어느 씬에 속하는지 찾기
            for scene in scenes:
                scene_instance = scene['instances'][0] if scene['instances'] else None
                if scene_instance:
                    scene_start = parse_duration(scene_instance['start'])
                    scene_end = parse_duration(scene_instance['end'])
                    if scene_start <= start_time < scene_end:
                        shots_per_scene[scene['id']] += 1
                        break
            
            print(f"    샷 {shot_id:3d}: {format_time(start_time)} - {format_time(end_time)} "
                  f"(길이: {duration:.1f}초, 키프레임: {len(keyframes)}개)")
    
    # 샷 통계
    if shot_durations:
        avg_shot_duration = sum(shot_durations) / len(shot_durations)
        max_shot_duration = max(shot_durations)
        min_shot_duration = min(shot_durations)
        
        print(f"\n  샷 통계:")
        print(f"    평균 샷 길이: {avg_shot_duration:.1f}초")
        print(f"    최장 샷: {max_shot_duration:.1f}초")
        print(f"    최단 샷: {min_shot_duration:.1f}초")
        print(f"    총 키프레임: {keyframes_count}개")
    
    print()
    
    # 3. 씬별 샷 분포
    print("🎯 씬별 샷 분포:")
    total_shots_analyzed = 0
    for scene_id in sorted(shots_per_scene.keys()):
        shot_count = shots_per_scene[scene_id]
        total_shots_analyzed += shot_count
        bar = "█" * (shot_count // 2) + "▌" * (1 if shot_count % 2 == 1 else 0)
        print(f"    씬 {scene_id:2d}: {shot_count:2d}개 샷 {bar}")
    
    print(f"\n  분석된 샷 수: {total_shots_analyzed}/{len(shots)}")
    
    # 4. 편집 리듬 분석
    print("\n⏱️ 편집 리듬 분석:")
    
    # 샷 길이별 분포
    if shot_durations:
        short_shots = sum(1 for d in shot_durations if d < 3)
        medium_shots = sum(1 for d in shot_durations if 3 <= d < 10)
        long_shots = sum(1 for d in shot_durations if d >= 10)
        
        print(f"  샷 길이별 분포:")
        print(f"    짧은 샷 (<3초): {short_shots}개 ({short_shots/len(shot_durations)*100:.1f}%)")
        print(f"    중간 샷 (3-10초): {medium_shots}개 ({medium_shots/len(shot_durations)*100:.1f}%)")
        print(f"    긴 샷 (>10초): {long_shots}개 ({long_shots/len(shot_durations)*100:.1f}%)")
    
    # 5. 키프레임 분석
    print(f"\n🖼️ 키프레임 분석:")
    keyframe_distribution = []
    
    for shot in shots:
        keyframes = shot.get('keyFrames', [])
        keyframe_distribution.append(len(keyframes))
    
    if keyframe_distribution:
        avg_keyframes = sum(keyframe_distribution) / len(keyframe_distribution)
        max_keyframes = max(keyframe_distribution)
        
        print(f"  평균 키프레임/샷: {avg_keyframes:.1f}개")
        print(f"  최대 키프레임/샷: {max_keyframes}개")
        
        # 키프레임 수별 샷 분포
        keyframe_counts = {}
        for count in keyframe_distribution:
            keyframe_counts[count] = keyframe_counts.get(count, 0) + 1
        
        print(f"  키프레임 수별 샷 분포:")
        for count, shots_num in sorted(keyframe_counts.items()):
            if count <= 5:  # 처음 몇 개만 표시
                print(f"    {count}개 키프레임: {shots_num}개 샷")
    
    print("\n✅ 씬&샷 분석 완료!")
    
    # 결과 요약 반환
    return {
        'total_scenes': len(scenes),
        'total_shots': len(shots),
        'avg_scene_duration': avg_scene_duration if scene_durations else 0,
        'avg_shot_duration': avg_shot_duration if shot_durations else 0,
        'total_keyframes': keyframes_count
    }

if __name__ == "__main__":
    analyze_scenes_shots() 