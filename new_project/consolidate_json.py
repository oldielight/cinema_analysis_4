import json
import os
from datetime import datetime

def consolidate_json_files(directory):
    consolidated = {
        'analysis_info': {
            'timestamp': datetime.now().isoformat(),
            'total_images': 0,
            'source_directory': 'data/processed/cure_frames_109_349'
        },
        'results': []
    }

    json_files = [f for f in os.listdir(directory) if f.endswith('_leading_lines.json')]
    consolidated['analysis_info']['total_images'] = len(json_files)

    for json_file in sorted(json_files):
        filepath = os.path.join(directory, json_file)
        with open(filepath, 'r') as f:
            data = json.load(f)
        consolidated['results'].append(data)

    output_path = os.path.join(directory, 'consolidated_all_leading_lines.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)

    print(f'통합 완료: {len(json_files)}개 파일을 consolidated_all_leading_lines.json으로 병합')
    return output_path

if __name__ == '__main__':
    directory = 'results/leading_lines_cure_frames'
    consolidate_json_files(directory) 