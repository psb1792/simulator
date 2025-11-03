"""전투 계산 엔진"""
from data_loader import load_unit_stats, load_type_effectiveness


class CombatCalculator:
    """전투 공식 V3.0에 따른 전투 계산 클래스"""
    
    def __init__(self):
        self.unit_stats = load_unit_stats()
        self.effectiveness = load_type_effectiveness()
    
    def calculate_total_hp(self, army_units):
        """
        군대의 총 HP를 계산합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리 (예: {'보병': 50, '기병': 30})
        
        Returns:
            float: 총 HP
        """
        total_hp = 0
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                total_hp += quantity * self.unit_stats[unit_type]['hp']
        return total_hp
    
    def calculate_base_total_attack(self, army_units):
        """
        군대의 기본 총 공격력을 계산합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
        
        Returns:
            float: 기본 총 공격력
        """
        total_attack = 0
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                total_attack += quantity * self.unit_stats[unit_type]['attack']
        return total_attack
    
    def calculate_hp_ratios(self, army_units):
        """
        군대의 병종별 HP 비율을 계산합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
        
        Returns:
            dict: 병종별 HP 비율 딕셔너리
        """
        total_hp = self.calculate_total_hp(army_units)
        
        if total_hp == 0:
            return {}
        
        ratios = {}
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                unit_hp = quantity * self.unit_stats[unit_type]['hp']
                ratios[unit_type] = unit_hp / total_hp
        
        return ratios
    
    def calculate_final_attack_power(self, attacker_units, defender_units):
        """
        공격자의 최종 공격력(FAP)을 계산합니다.
        상대방의 병종별 HP 비율을 고려한 가중 평균을 사용합니다.
        
        Args:
            attacker_units (dict): 공격자 병종별 수량
            defender_units (dict): 방어자 병종별 수량
        
        Returns:
            float: 최종 공격력 (FAP)
        """
        # 1. 기본 총 공격력 계산
        base_total_attack = self.calculate_base_total_attack(attacker_units)
        
        # 2. 방어자의 병종별 HP 비율 계산
        defender_hp_ratios = self.calculate_hp_ratios(defender_units)
        
        # 3. 최종 공격력 계산 (가중 평균)
        # 공격자의 기본 총 공격력 전체에 방어자 병종별 HP 비율을 고려한 상성 계수를 적용
        final_attack_power = 0
        
        for defender_type, hp_ratio in defender_hp_ratios.items():
            # 공격자 병종별로 상성 계수를 적용하여 가중 평균 계산
            weighted_multiplier = 0
            
            for attacker_type, attacker_quantity in attacker_units.items():
                if attacker_quantity > 0 and attacker_type in self.unit_stats:
                    # 해당 공격자 병종의 공격력 비율 계산
                    attacker_damage = attacker_quantity * self.unit_stats[attacker_type]['attack']
                    attacker_ratio = attacker_damage / base_total_attack if base_total_attack > 0 else 0
                    
                    # 상성 계수 가져오기
                    key = (attacker_type, defender_type)
                    if key in self.effectiveness:
                        multiplier = self.effectiveness[key]
                    else:
                        multiplier = 1.0  # 기본값
                    
                    # 각 공격자 병종의 기여도 누적
                    weighted_multiplier += attacker_ratio * multiplier
            
            # 가중 평균: (기본 총 공격력 * 가중 상성계수 * HP비율)
            final_attack_power += base_total_attack * weighted_multiplier * hp_ratio
        
        return final_attack_power
    
    def calculate_casualty_ratio(self, final_attack_power, total_hp):
        """
        사상률을 계산합니다.
        
        Args:
            final_attack_power (float): 최종 공격력
            total_hp (float): 총 HP
        
        Returns:
            float: 사상률 (최대 1.0)
        """
        if total_hp == 0:
            return 0.0
        
        ratio = final_attack_power / total_hp
        return min(ratio, 1.0)  # 최대 1.0 (100%)
    
    def calculate_casualties(self, army_units, casualty_ratio):
        """
        병종별 사상자 수를 계산합니다.
        소수점 이하는 버립니다 (내림).
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
            casualty_ratio (float): 사상률
        
        Returns:
            dict: 병종별 사상자 수 딕셔너리
        """
        casualties = {}
        for unit_type, quantity in army_units.items():
            casualties[unit_type] = int(quantity * casualty_ratio)
        return casualties
    
    def simulate_combat(self, army_a_units, army_b_units):
        """
        전투를 시뮬레이션하고 결과를 반환합니다.
        
        Args:
            army_a_units (dict): A군 병종별 수량
            army_b_units (dict): B군 병종별 수량
        
        Returns:
            dict: 전투 결과
                - army_a_total_hp: A군 총 HP
                - army_b_total_hp: B군 총 HP
                - army_a_fap: A군 최종 공격력
                - army_b_fap: B군 최종 공격력
                - army_a_casualty_ratio: A군 사상률
                - army_b_casualty_ratio: B군 사상률
                - army_a_casualties: A군 병종별 사상자
                - army_b_casualties: B군 병종별 사상자
                - army_a_remaining: A군 병종별 잔존 병력
                - army_b_remaining: B군 병종별 잔존 병력
        """
        # 1단계: 총 HP 풀 계산
        army_a_total_hp = self.calculate_total_hp(army_a_units)
        army_b_total_hp = self.calculate_total_hp(army_b_units)
        
        # 2단계: 최종 공격력 계산
        army_a_fap = self.calculate_final_attack_power(army_a_units, army_b_units)
        army_b_fap = self.calculate_final_attack_power(army_b_units, army_a_units)
        
        # 3단계: 사상률 계산
        army_a_casualty_ratio = self.calculate_casualty_ratio(army_b_fap, army_a_total_hp)
        army_b_casualty_ratio = self.calculate_casualty_ratio(army_a_fap, army_b_total_hp)
        
        # 4단계: 최종 사상자 수 계산
        army_a_casualties = self.calculate_casualties(army_a_units, army_a_casualty_ratio)
        army_b_casualties = self.calculate_casualties(army_b_units, army_b_casualty_ratio)
        
        # 잔존 병력 계산 (병력수 - 사상자수)
        army_a_remaining = {}
        army_b_remaining = {}
        for unit_type in army_a_units:
            army_a_remaining[unit_type] = max(0, army_a_units[unit_type] - army_a_casualties.get(unit_type, 0))
        for unit_type in army_b_units:
            army_b_remaining[unit_type] = max(0, army_b_units[unit_type] - army_b_casualties.get(unit_type, 0))
        
        return {
            'army_a_total_hp': army_a_total_hp,
            'army_b_total_hp': army_b_total_hp,
            'army_a_fap': army_a_fap,
            'army_b_fap': army_b_fap,
            'army_a_casualty_ratio': army_a_casualty_ratio,
            'army_b_casualty_ratio': army_b_casualty_ratio,
            'army_a_casualties': army_a_casualties,
            'army_b_casualties': army_b_casualties,
            'army_a_remaining': army_a_remaining,
            'army_b_remaining': army_b_remaining
        }
    
    def check_army_destroyed(self, army_units):
        """
        군대가 전멸했는지 확인합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
        
        Returns:
            bool: 전멸 여부
        """
        total = sum(army_units.values())
        return total == 0
    
    def simulate_multi_round_combat(self, army_a_units, army_b_units, max_rounds=100):
        """
        한쪽 세력이 전멸할 때까지 전투를 반복합니다.
        
        Args:
            army_a_units (dict): A군 초기 병종별 수량
            army_b_units (dict): B군 초기 병종별 수량
            max_rounds (int): 최대 라운드 수 (무한 루프 방지)
        
        Returns:
            dict: 멀티 라운드 전투 결과
                - rounds: 각 라운드별 전투 결과 리스트
                - final_winner: 승리 세력 ('A', 'B', None)
                - total_rounds: 총 라운드 수
        """
        # 초기 병력 복사
        current_a_units = army_a_units.copy()
        current_b_units = army_b_units.copy()
        
        rounds = []
        round_num = 1
        winner = None
        no_casualty_stalemate_count = 0  # 사상자 없이 같은 결과가 나온 연속 횟수
        
        # 한쪽 세력이 전멸하거나 최대 라운드에 도달할 때까지 반복
        while round_num <= max_rounds:
            # 전멸 여부 확인
            if self.check_army_destroyed(current_a_units):
                winner = 'B'
                break
            if self.check_army_destroyed(current_b_units):
                winner = 'A'
                break
            
            # 현재 라운드 전투 수행
            round_result = self.simulate_combat(current_a_units, current_b_units)
            round_result['round'] = round_num
            round_result['army_a_initial'] = current_a_units.copy()
            round_result['army_b_initial'] = current_b_units.copy()
            rounds.append(round_result)
            
            # 다음 라운드를 위한 잔존 병력 업데이트
            next_a_units = round_result['army_a_remaining'].copy()
            next_b_units = round_result['army_b_remaining'].copy()
            
            # 사상자 총합 계산
            total_a_casualties = sum(round_result['army_a_casualties'].values())
            total_b_casualties = sum(round_result['army_b_casualties'].values())
            
            # 사상자가 없고 병력이 동일한지 확인
            if total_a_casualties == 0 and total_b_casualties == 0:
                # 이전 병력과 비교
                if (current_a_units == next_a_units and current_b_units == next_b_units):
                    no_casualty_stalemate_count += 1
                    # 사상자 없이 같은 결과가 2번 이상이면 무승부
                    if no_casualty_stalemate_count >= 2:
                        winner = None
                        break
                else:
                    # 병력이 변경되었으면 카운터 리셋
                    no_casualty_stalemate_count = 0
            else:
                # 사상자가 있으면 카운터 리셋
                no_casualty_stalemate_count = 0
            
            # 다음 라운드를 위한 병력 업데이트
            current_a_units = next_a_units
            current_b_units = next_b_units
            
            round_num += 1
        
        # 최대 라운드에 도달했는데도 승자가 없는 경우 (무승부)
        if winner is None and round_num > max_rounds:
            winner = None
        
        return {
            'rounds': rounds,
            'final_winner': winner,
            'total_rounds': len(rounds),
            'final_army_a': current_a_units,
            'final_army_b': current_b_units
        }


if __name__ == '__main__':
    # 테스트
    calculator = CombatCalculator()
    
    # 예제: 보병 70 + 마법병 30 vs 기병 80
    army_a = {'보병': 70, '마법병': 30, '기병': 0, '공성병': 0}
    army_b = {'기병': 80, '보병': 0, '마법병': 0, '공성병': 0}
    
    result = calculator.simulate_combat(army_a, army_b)
    
    print("=== 전투 결과 ===")
    print(f"A군 총 HP: {result['army_a_total_hp']:.2f}")
    print(f"B군 총 HP: {result['army_b_total_hp']:.2f}")
    print(f"A군 최종 공격력: {result['army_a_fap']:.2f}")
    print(f"B군 최종 공격력: {result['army_b_fap']:.2f}")
    print(f"A군 사상률: {result['army_a_casualty_ratio']:.2%}")
    print(f"B군 사상률: {result['army_b_casualty_ratio']:.2%}")
    print("\nA군 사상자:", result['army_a_casualties'])
    print("B군 사상자:", result['army_b_casualties'])

