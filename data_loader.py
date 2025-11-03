"""CSV 데이터 로딩 모듈"""
import pandas as pd
import re


def load_unit_stats():
    """
    공_체 밸런싱.csv 파일을 읽어서 병종별 스탯을 반환합니다.
    
    Returns:
        dict: 병종명을 키로 하고, 공격력/체력/비용을 값으로 하는 딕셔너리
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
    
    return unit_stats


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

