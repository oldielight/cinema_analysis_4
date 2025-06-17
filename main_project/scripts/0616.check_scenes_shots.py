#!/usr/bin/env python3
import json

def check_scenes_shots():
    """Check if Azure JSON contains scene and shot data"""
    
    with open('azure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🎬 씬과 샷 데이터 확인")
    print("=" * 50)
    
    # 전체 JSON 구조 확인
    print("📊 JSON 최상위 키들:")
    for key in data.keys():
        print(f"  - {key}")
    print()
    
    # 비디오 인사이트 내부 확인
    if 'videos' in data and len(data['videos']) > 0:
        video = data['videos'][0]
        insights = video.get('insights', {})
        
        print("🔍 인사이트 섹션 내 키들:")
        for key in insights.keys():
            if isinstance(insights[key], list):
                print(f"  - {key}: {len(insights[key])}개 항목")
            else:
                print(f"  - {key}: {type(insights[key])}")
        print()
        
        # 씬 데이터 확인
        scenes = insights.get('scenes', [])
        if scenes:
            print("🎭 씬(Scene) 데이터 발견!")
            print(f"  총 씬 수: {len(scenes)}")
            
            print("  샘플 씬 정보:")
            for i, scene in enumerate(scenes[:3]):
                print(f"    씬 {i+1}:")
                for key, value in scene.items():
                    if key == 'instances' and isinstance(value, list):
                        print(f"      {key}: {len(value)}개 인스턴스")
                        if value:
                            first_instance = value[0]
                            start = first_instance.get('start', 'N/A')
                            end = first_instance.get('end', 'N/A')
                            print(f"        첫 번째: {start} - {end}")
                    else:
                        print(f"      {key}: {value}")
        else:
            print("❌ 씬(Scene) 데이터 없음")
        
        # 샷 데이터 확인
        shots = insights.get('shots', [])
        if shots:
            print("\n📷 샷(Shot) 데이터 발견!")
            print(f"  총 샷 수: {len(shots)}")
            
            print("  샘플 샷 정보:")
            for i, shot in enumerate(shots[:5]):
                print(f"    샷 {i+1}:")
                for key, value in shot.items():
                    if key == 'instances' and isinstance(value, list):
                        print(f"      {key}: {len(value)}개 인스턴스")
                        if value:
                            first_instance = value[0]
                            start = first_instance.get('start', 'N/A')
                            end = first_instance.get('end', 'N/A')
                            print(f"        시간: {start} - {end}")
                    else:
                        print(f"      {key}: {value}")
        else:
            print("\n❌ 샷(Shot) 데이터 없음")
        
        # 기타 비디오 분석 데이터 확인
        print("\n🔍 기타 가능한 비디오 분석 데이터:")
        
        analysis_fields = [
            'faces', 'keywords', 'labels', 'brands', 'emotions', 
            'sentiments', 'visualContentModeration', 'audioEffects',
            'blocks', 'framePatterns', 'speakers'
        ]
        
        for field in analysis_fields:
            if field in insights:
                data_item = insights[field]
                if isinstance(data_item, list):
                    if len(data_item) > 0:
                        print(f"  ✅ {field}: {len(data_item)}개 항목")
                    else:
                        print(f"  ⚪ {field}: 빈 배열")
                else:
                    print(f"  ⚪ {field}: {type(data_item)}")
        
        # 비어있지 않은 섹션들 상세 보기
        print("\n📋 데이터가 있는 섹션들:")
        for key, value in insights.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"  • {key}: {len(value)}개")
                # 첫 번째 항목 구조 확인
                if value:
                    first_item = value[0]
                    if isinstance(first_item, dict):
                        print(f"    구조: {list(first_item.keys())}")

if __name__ == "__main__":
    check_scenes_shots() 