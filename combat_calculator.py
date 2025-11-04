"""전투 계산 엔진"""
from data_loader import load_unit_stats, load_type_effectiveness, get_food_consumption, load_equipment


class CombatCalculator:
    """전투 공식 V3.0에 따른 전투 계산 클래스"""
    
    def __init__(self):
        self.unit_stats = load_unit_stats()
        self.effectiveness = load_type_effectiveness()
        self.food_consumption = get_food_consumption()
        self.equipment = load_equipment()
    
    def calculate_food_consumption(self, army_units):
        """
        병력의 라운드당 식량 소비량을 계산합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
        
        Returns:
            int: 총 식량 소비량
        """
        total_food = 0
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.food_consumption:
                total_food += quantity * self.food_consumption[unit_type]
        return total_food
    
    def apply_food_penalty(self, fap, has_food):
        """
        식량 부족 시 FAP에 패널티를 적용합니다.
        식량이 0 이하면 FAP이 70% 감소합니다.
        
        Args:
            fap (float): 최종 공격력
            has_food (bool): 식량이 있는지 여부 (True면 식량 >= 1)
        
        Returns:
            float: 패널티가 적용된 FAP
        """
        if not has_food:
            return fap * 0.3  # 70% 감소 = 원래 값의 30%
        return fap
    
    def calculate_total_hp(self, army_units, equipment_list=None):
        """
        군대의 총 HP를 계산합니다. 장비의 HP 보너스를 적용합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리 (예: {'보병': 50, '기병': 30})
            equipment_list (list): 장비 딕셔너리 리스트 (None이면 장비 없음)
        
        Returns:
            float: 총 HP
        """
        total_hp = 0
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                total_hp += quantity * self.unit_stats[unit_type]['hp']
        
        # 장비 HP 보너스 적용 (곱연산)
        if equipment_list:
            hp_multiplier = 1.0
            for equipment in equipment_list:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'hp_bonus':
                            hp_multiplier *= effect.get('value', 1.0)
            total_hp *= hp_multiplier
        
        return total_hp
    
    def calculate_base_total_attack(self, army_units, equipment_list=None):
        """
        군대의 기본 총 공격력을 계산합니다. 장비의 공격력 보너스를 적용합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
            equipment_list (list): 장비 딕셔너리 리스트 (None이면 장비 없음)
        
        Returns:
            float: 기본 총 공격력
        """
        total_attack = 0
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                total_attack += quantity * self.unit_stats[unit_type]['attack']
        
        # 장비 공격력 보너스 적용 (곱연산)
        if equipment_list:
            attack_multiplier = 1.0
            for equipment in equipment_list:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'attack_bonus':
                            attack_multiplier *= effect.get('value', 1.0)
            total_attack *= attack_multiplier
        
        return total_attack
    
    def calculate_hp_ratios(self, army_units, equipment_list=None):
        """
        군대의 병종별 HP 비율을 계산합니다.
        
        Args:
            army_units (dict): 병종별 수량 딕셔너리
            equipment_list (list): 장비 딕셔너리 리스트 (None이면 장비 없음)
        
        Returns:
            dict: 병종별 HP 비율 딕셔너리
        """
        total_hp = self.calculate_total_hp(army_units, equipment_list)
        
        if total_hp == 0:
            return {}
        
        # 장비 HP 보너스 적용 (곱연산)
        hp_multiplier = 1.0
        if equipment_list:
            for equipment in equipment_list:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'hp_bonus':
                            hp_multiplier *= effect.get('value', 1.0)
        
        ratios = {}
        for unit_type, quantity in army_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                unit_hp = quantity * self.unit_stats[unit_type]['hp'] * hp_multiplier
                ratios[unit_type] = unit_hp / total_hp
        
        return ratios
    
    def calculate_final_attack_power(self, attacker_units, defender_units, 
                                     attacker_equipment_list=None, defender_equipment_list=None, enemy_attack_penalty=1.0):
        """
        공격자의 최종 공격력(FAP)을 계산합니다.
        상대방의 병종별 HP 비율을 고려한 가중 평균을 사용합니다.
        장비 효과를 적용합니다.
        
        Args:
            attacker_units (dict): 공격자 병종별 수량
            defender_units (dict): 방어자 병종별 수량
            attacker_equipment_list (list): 공격자 장비 딕셔너리 리스트 (None이면 장비 없음)
            defender_equipment_list (list): 방어자 장비 딕셔너리 리스트 (None이면 장비 없음, 적 공격력 패널티에 사용)
            enemy_attack_penalty (float): 적 공격력 패널티 (기본값 1.0, 장비 효과로 인한 감소)
        
        Returns:
            float: 최종 공격력 (FAP)
        """
        # 1. 기본 총 공격력 계산 (보너스 없이)
        base_total_attack_no_bonus = 0
        for unit_type, quantity in attacker_units.items():
            if quantity > 0 and unit_type in self.unit_stats:
                base_total_attack_no_bonus += quantity * self.unit_stats[unit_type]['attack']
        
        # 장비 공격력 보너스 계산 (곱연산)
        attack_multiplier = 1.0
        if attacker_equipment_list:
            for equipment in attacker_equipment_list:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'attack_bonus':
                            attack_multiplier *= effect.get('value', 1.0)
        
        # 보너스 적용된 기본 총 공격력
        base_total_attack = base_total_attack_no_bonus * attack_multiplier
        
        # 2. 방어자의 병종별 HP 비율 계산 (방어자 장비 효과 적용)
        defender_hp_ratios = self.calculate_hp_ratios(defender_units, defender_equipment_list)
        
        # 3. 최종 공격력 계산 (가중 평균)
        # 공격자의 기본 총 공격력 전체에 방어자 병종별 HP 비율을 고려한 상성 계수를 적용
        final_attack_power = 0
        
        # 공격자 장비의 상성 보너스 수집 (합연산)
        type_effectiveness_bonuses = {}
        if attacker_equipment_list:
            for equipment in attacker_equipment_list:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'type_effectiveness_bonus':
                            key = (effect.get('attacker'), effect.get('defender'))
                            if key not in type_effectiveness_bonuses:
                                type_effectiveness_bonuses[key] = 0
                            type_effectiveness_bonuses[key] += effect.get('value', 0)
        
        for defender_type, hp_ratio in defender_hp_ratios.items():
            # 공격자 병종별로 상성 계수를 적용하여 가중 평균 계산
            weighted_multiplier = 0
            
            for attacker_type, attacker_quantity in attacker_units.items():
                if attacker_quantity > 0 and attacker_type in self.unit_stats:
                    # 해당 공격자 병종의 공격력 계산 (보너스 적용 전)
                    attacker_damage = attacker_quantity * self.unit_stats[attacker_type]['attack']
                    
                    # 공격력 비율 계산 (보너스 없는 기본 총 공격력 기준)
                    attacker_ratio = attacker_damage / base_total_attack_no_bonus if base_total_attack_no_bonus > 0 else 0
                    
                    # 상성 계수 가져오기
                    key = (attacker_type, defender_type)
                    multiplier = 1.0
                    if key in self.effectiveness:
                        multiplier = self.effectiveness[key]
                    
                    # 장비 상성 보너스 적용 (합연산)
                    if key in type_effectiveness_bonuses:
                        multiplier += type_effectiveness_bonuses[key]
                    
                    # 각 공격자 병종의 기여도 누적
                    weighted_multiplier += attacker_ratio * multiplier
            
            # 가중 평균: (기본 총 공격력 * 가중 상성계수 * HP비율)
            final_attack_power += base_total_attack * weighted_multiplier * hp_ratio
        
        # 적 공격력 패널티 적용 (방어자 장비 효과)
        final_attack_power *= enemy_attack_penalty
        
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
    
    def simulate_combat(self, army_a_units, army_b_units, has_food_a=True, has_food_b=True,
                        equipment_list_a=None, equipment_list_b=None):
        """
        전투를 시뮬레이션하고 결과를 반환합니다.
        
        Args:
            army_a_units (dict): A군 병종별 수량
            army_b_units (dict): B군 병종별 수량
            has_food_a (bool): A군 식량 보유 여부 (기본값: True)
            has_food_b (bool): B군 식량 보유 여부 (기본값: True)
            equipment_list_a (list): A군 장비 딕셔너리 리스트 (None이면 장비 없음)
            equipment_list_b (list): B군 장비 딕셔너리 리스트 (None이면 장비 없음)
        
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
        # 적 공격력 패널티 계산 (방어자 장비 효과, 곱연산)
        enemy_penalty_a = 1.0  # B군이 A군을 공격할 때 적용되는 패널티
        enemy_penalty_b = 1.0  # A군이 B군을 공격할 때 적용되는 패널티
        
        if equipment_list_a:
            for equipment in equipment_list_a:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'enemy_attack_penalty':
                            enemy_penalty_b *= effect.get('value', 1.0)
        
        if equipment_list_b:
            for equipment in equipment_list_b:
                if equipment and equipment.get('effects'):
                    for effect in equipment['effects']:
                        if effect.get('type') == 'enemy_attack_penalty':
                            enemy_penalty_a *= effect.get('value', 1.0)
        
        # 1단계: 총 HP 풀 계산 (장비 효과 적용)
        army_a_total_hp = self.calculate_total_hp(army_a_units, equipment_list_a)
        army_b_total_hp = self.calculate_total_hp(army_b_units, equipment_list_b)
        
        # 2단계: 최종 공격력 계산 (장비 효과 적용)
        army_a_fap = self.calculate_final_attack_power(army_a_units, army_b_units,
                                                       attacker_equipment_list=equipment_list_a, 
                                                       defender_equipment_list=equipment_list_b,
                                                       enemy_attack_penalty=enemy_penalty_b)
        army_b_fap = self.calculate_final_attack_power(army_b_units, army_a_units,
                                                       attacker_equipment_list=equipment_list_b, 
                                                       defender_equipment_list=equipment_list_a,
                                                       enemy_attack_penalty=enemy_penalty_a)
        
        # 식량 패널티 적용
        army_a_fap = self.apply_food_penalty(army_a_fap, has_food_a)
        army_b_fap = self.apply_food_penalty(army_b_fap, has_food_b)
        
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
    
    def simulate_multi_round_combat(self, army_a_units, army_b_units, max_rounds=12, 
                                     initial_food_a=None, initial_food_b=None,
                                     equipment_list_a=None, equipment_list_b=None):
        """
        한쪽 세력이 전멸할 때까지 전투를 반복합니다.
        
        Args:
            army_a_units (dict): A군 초기 병종별 수량
            army_b_units (dict): B군 초기 병종별 수량
            max_rounds (int): 최대 라운드 수 (무한 루프 방지, 기본값 12)
            initial_food_a (int): A군 초기 식량 (None이면 식량 무제한)
            initial_food_b (int): B군 초기 식량 (None이면 식량 무제한)
            equipment_list_a (list): A군 장비 딕셔너리 리스트 (None이면 장비 없음)
            equipment_list_b (list): B군 장비 딕셔너리 리스트 (None이면 장비 없음)
        
        Returns:
            dict: 멀티 라운드 전투 결과
                - rounds: 각 라운드별 전투 결과 리스트
                - final_winner: 승리 세력 ('A', 'B', None)
                - total_rounds: 총 라운드 수
                - initial_army_a: 초기 A군 병력
                - initial_army_b: 초기 B군 병력
                - final_food_a: 최종 A군 식량
                - final_food_b: 최종 B군 식량
        """
        # 초기 병력 복사 및 저장
        initial_a_units = army_a_units.copy()
        initial_b_units = army_b_units.copy()
        current_a_units = army_a_units.copy()
        current_b_units = army_b_units.copy()
        
        # 식량 초기화
        food_a = initial_food_a
        food_b = initial_food_b
        
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
            
            # 식량 소비 (전투 전)
            food_consumption_a = self.calculate_food_consumption(current_a_units) if food_a is not None else 0
            food_consumption_b = self.calculate_food_consumption(current_b_units) if food_b is not None else 0
            
            if food_a is not None:
                food_a = max(0, food_a - food_consumption_a)
            if food_b is not None:
                food_b = max(0, food_b - food_consumption_b)
            
            # 현재 라운드 전투 수행 (식량 고려)
            has_food_a = food_a is None or food_a > 0
            has_food_b = food_b is None or food_b > 0
            
            round_result = self.simulate_combat(current_a_units, current_b_units, 
                                                has_food_a=has_food_a, has_food_b=has_food_b,
                                                equipment_list_a=equipment_list_a, 
                                                equipment_list_b=equipment_list_b)
            round_result['round'] = round_num
            round_result['army_a_initial'] = current_a_units.copy()
            round_result['army_b_initial'] = current_b_units.copy()
            round_result['food_a'] = food_a
            round_result['food_b'] = food_b
            round_result['food_consumption_a'] = food_consumption_a
            round_result['food_consumption_b'] = food_consumption_b
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
        
        # 최대 라운드에 도달했는데도 승자가 없는 경우 손실 비율로 판정
        if winner is None:
            # 초기 병력 총합 계산
            initial_a_total = sum(initial_a_units.values())
            initial_b_total = sum(initial_b_units.values())
            
            # 최종 병력 총합 계산
            final_a_total = sum(current_a_units.values())
            final_b_total = sum(current_b_units.values())
            
            # 손실 비율 계산
            if initial_a_total > 0:
                a_loss_ratio = (initial_a_total - final_a_total) / initial_a_total
            else:
                a_loss_ratio = 0.0
            
            if initial_b_total > 0:
                b_loss_ratio = (initial_b_total - final_b_total) / initial_b_total
            else:
                b_loss_ratio = 0.0
            
            # 손실 비율이 더 큰 쪽이 패배
            if a_loss_ratio > b_loss_ratio:
                winner = 'B'
            elif b_loss_ratio > a_loss_ratio:
                winner = 'A'
            else:
                winner = None  # 무승부
        
        return {
            'rounds': rounds,
            'final_winner': winner,
            'total_rounds': len(rounds),
            'final_army_a': current_a_units,
            'final_army_b': current_b_units,
            'initial_army_a': initial_a_units,
            'initial_army_b': initial_b_units,
            'final_food_a': food_a,
            'final_food_b': food_b
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

