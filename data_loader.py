"""CSV 데이터 로딩 모듈"""
import pandas as pd
import re
import json


def load_unit_stats():
    """
    공_체 밸런싱.csv 파일을 읽어서 병종별 스탯을 반환합니다.
    
    Returns:
        dict: 병종명을 키로 하고, 공격력/체력/비용/식량소비량을 값으로 하는 딕셔너리
    """
    df = pd.read_csv('공_체 밸런싱.csv', encoding='utf-8')
    
    unit_stats = {}
    for _, row in df.iterrows():
        unit_type = row['병종']
        unit_stats[unit_type] = {
            'attack': int(row['공격력(Att)']),
            'hp': int(row['체력(HP)']),
            'cost': int(row['비용(Cost)'])
        }
        
        # 식량 소비량이 CSV에 있는 경우 읽어오기 (없으면 기본값 사용)
        if '식량(Food)' in row:
            unit_stats[unit_type]['food'] = int(row['식량(Food)'])
        elif '식량 소비량' in row:
            unit_stats[unit_type]['food'] = int(row['식량 소비량'])
        elif '식량' in row:
            unit_stats[unit_type]['food'] = int(row['식량'])
    
    return unit_stats


def get_food_consumption():
    """
    병종별 식량 소비량을 반환합니다.
    CSV 파일에서 읽어오며, CSV에 없으면 기본값을 사용합니다.
    
    Returns:
        dict: 병종명을 키로 하고, 라운드당 식량 소비량을 값으로 하는 딕셔너리
    """
    try:
        df = pd.read_csv('공_체 밸런싱.csv', encoding='utf-8')
        
        # CSV에서 식량 열 이름 찾기 (여러 가능한 열 이름 지원, 공백 허용)
        food_column = None
        # 컬럼명의 공백을 제거하고 비교하거나, 부분 문자열로 찾기
        for col in df.columns:
            col_stripped = col.strip()
            if col_stripped == '식량(Food)' or col_stripped == '식량 소비량':
                food_column = col  # 실제 컬럼명 사용 (공백 포함 가능)
                break
            elif '식량' in col_stripped and 'Food' in col_stripped:
                food_column = col
                break
            elif col_stripped == '식량':
                food_column = col
                break
        
        # 위 방법으로 찾지 못한 경우, 부분 문자열로 다시 시도
        if food_column is None:
            for col in df.columns:
                if '식량' in col or 'Food' in col:
                    food_column = col
                    break
        
        # 기본값 딕셔너리
        defaults = {
            '보병': 1,
            '기병': 3,
            '마법병': 2,
            '공성병': 2
        }
        
        food_consumption = {}
        for _, row in df.iterrows():
            unit_type = str(row['병종'])
            
            if food_column:
                try:
                    food_value = row[food_column]
                    if food_value is not None and str(food_value).strip() != '':
                        food_consumption[unit_type] = int(float(food_value))
                    else:
                        food_consumption[unit_type] = defaults.get(unit_type, 1)
                except (ValueError, TypeError):
                    food_consumption[unit_type] = defaults.get(unit_type, 1)
            else:
                # CSV에 식량 열이 없으면 기본값 사용
                food_consumption[unit_type] = defaults.get(unit_type, 1)
        
        return food_consumption
    except Exception:
        # 오류 발생 시 기본값 반환
        return {
            '보병': 1,
            '기병': 3,
            '마법병': 2,
            '공성병': 2
        }


def load_type_effectiveness():
    """
    상성 계수.csv 파일을 읽어서 상성 계수를 반환합니다.
    
    Returns:
        dict: (공격자, 방어자) 튜플을 키로 하고 상성 계수를 값으로 하는 딕셔너리
    """
    df = pd.read_csv('상성 계수.csv', encoding='utf-8')
    
    effectiveness = {}
    
    # 첫 번째 열이 공격자
    attacker_col = df.columns[0]
    
    for _, row in df.iterrows():
        attacker = row[attacker_col]
        
        # 각 방어자 병종에 대해 상성 계수 추출
        for col in df.columns[1:]:  # 첫 번째 열 제외
            defender = col.replace('vs ', '')
            
            value_str = str(row[col])
            # 괄호와 설명 제거하여 숫자만 추출
            # 예: "1.5 (강함)" -> "1.5"
            match = re.search(r'(\d+\.?\d*)', value_str)
            if match:
                multiplier = float(match.group(1))
                effectiveness[(attacker, defender)] = multiplier
    
    return effectiveness


def load_heroes():
    """
    heroes.json 파일을 읽어서 영웅 데이터를 반환합니다.
    
    Returns:
        dict: 영웅 이름을 키로 하고, 영웅 데이터(효과 리스트 포함)를 값으로 하는 딕셔너리
    """
    try:
        with open('heroes.json', 'r', encoding='utf-8') as f:
            heroes_list = json.load(f)
        
        heroes_dict = {}
        for hero in heroes_list:
            heroes_dict[hero['name']] = hero
        
        return heroes_dict
    except FileNotFoundError:
        # 파일이 없으면 기본 영웅만 반환
        return {'없음': {'name': '없음', 'effects': []}}


if __name__ == '__main__':
    # 테스트
    stats = load_unit_stats()
    print("병종 스탯:")
    for unit, stat in stats.items():
        print(f"{unit}: {stat}")
    
    print("\n상성 계수:")
    effectiveness = load_type_effectiveness()
    for (att, def_), mult in effectiveness.items():
        print(f"{att} vs {def_}: {mult}")

