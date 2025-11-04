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
        
        # 식량 소비량 읽어오기 (공백 허용)
        food_col = None
        for col in df.columns:
            if col.strip() == '식량(Food)':
                food_col = col
                break
        
        if food_col:
            unit_stats[unit_type]['food'] = int(row[food_col])
    
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
        
        # 식량 컬럼 찾기 (공백 허용)
        food_column = None
        for col in df.columns:
            if col.strip() == '식량(Food)':
                food_column = col  # 실제 컬럼명 사용 (공백 포함 가능)
                break
        
        # 기본값 딕셔너리
        defaults = {
            '보병': 0,
            '기병': 0,
            '마법병': 0,
            '공성병': 0
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
            '보병': 0,
            '기병': 0,
            '마법병': 0,
            '공성병': 0
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


def load_equipment():
    """
    heroes.json 파일을 읽어서 장비 데이터를 반환합니다.
    
    Returns:
        dict: 장비 ID를 키로 하고, 장비 데이터(효과 리스트 포함)를 값으로 하는 딕셔너리
    """
    try:
        with open('heroes.json', 'r', encoding='utf-8') as f:
            equipment_list = json.load(f)
        
        equipment_dict = {}
        for equipment in equipment_list:
            equipment_dict[equipment['id']] = equipment
        
        return equipment_dict
    except FileNotFoundError:
        # 파일이 없으면 빈 딕셔너리 반환
        return {}


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

