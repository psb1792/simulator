"""전투 시뮬레이터 GUI 애플리케이션"""
import tkinter as tk
from tkinter import ttk, messagebox
from combat_calculator import CombatCalculator


class CombatSimulatorGUI:
    """전투 시뮬레이터 GUI 클래스"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("전투 시뮬레이터 V3.0")
        self.root.geometry("800x700")
        
        self.calculator = CombatCalculator()
        self.unit_types = ['보병', '기병', '마법병', '공성병']
        
        self.create_widgets()
    
    def load_heroes(self):
        """영웅 목록을 로드하고 콤보박스에 설정합니다."""
        hero_names = list(self.calculator.heroes.keys())
        self.hero_a_combo['values'] = hero_names
        self.hero_b_combo['values'] = hero_names
        if hero_names:
            self.hero_a_combo.current(0)
            self.hero_b_combo.current(0)
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 제목
        title_label = tk.Label(self.root, text="전투 시뮬레이터", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # A군 입력 섹션
        army_a_frame = ttk.LabelFrame(main_frame, text="A군 병력", padding="10")
        army_a_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.army_a_entries = {}
        for i, unit_type in enumerate(self.unit_types):
            row_frame = ttk.Frame(army_a_frame)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            
            label = ttk.Label(row_frame, text=f"{unit_type}:", width=10)
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(row_frame, width=15)
            entry.insert(0, "0")
            entry.pack(side=tk.LEFT, padx=5)
            self.army_a_entries[unit_type] = entry
        
        # A군 식량 입력
        food_a_frame = ttk.Frame(army_a_frame)
        food_a_frame.grid(row=len(self.unit_types), column=0, sticky="ew", pady=5)
        ttk.Label(food_a_frame, text="식량:", width=10).pack(side=tk.LEFT, padx=5)
        self.food_a_entry = ttk.Entry(food_a_frame, width=15)
        self.food_a_entry.insert(0, "무제한")
        self.food_a_entry.pack(side=tk.LEFT, padx=5)
        
        # A군 영웅 선택
        hero_a_frame = ttk.Frame(army_a_frame)
        hero_a_frame.grid(row=len(self.unit_types) + 1, column=0, sticky="ew", pady=5)
        ttk.Label(hero_a_frame, text="영웅:", width=10).pack(side=tk.LEFT, padx=5)
        self.hero_a_var = tk.StringVar()
        self.hero_a_combo = ttk.Combobox(hero_a_frame, textvariable=self.hero_a_var, 
                                         width=15, state="readonly")
        self.hero_a_combo.pack(side=tk.LEFT, padx=5)
        
        army_a_frame.columnconfigure(0, weight=1)
        
        # B군 입력 섹션
        army_b_frame = ttk.LabelFrame(main_frame, text="B군 병력", padding="10")
        army_b_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.army_b_entries = {}
        for i, unit_type in enumerate(self.unit_types):
            row_frame = ttk.Frame(army_b_frame)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            
            label = ttk.Label(row_frame, text=f"{unit_type}:", width=10)
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(row_frame, width=15)
            entry.insert(0, "0")
            entry.pack(side=tk.LEFT, padx=5)
            self.army_b_entries[unit_type] = entry
        
        # B군 식량 입력
        food_b_frame = ttk.Frame(army_b_frame)
        food_b_frame.grid(row=len(self.unit_types), column=0, sticky="ew", pady=5)
        ttk.Label(food_b_frame, text="식량:", width=10).pack(side=tk.LEFT, padx=5)
        self.food_b_entry = ttk.Entry(food_b_frame, width=15)
        self.food_b_entry.insert(0, "무제한")
        self.food_b_entry.pack(side=tk.LEFT, padx=5)
        
        # B군 영웅 선택
        hero_b_frame = ttk.Frame(army_b_frame)
        hero_b_frame.grid(row=len(self.unit_types) + 1, column=0, sticky="ew", pady=5)
        ttk.Label(hero_b_frame, text="영웅:", width=10).pack(side=tk.LEFT, padx=5)
        self.hero_b_var = tk.StringVar()
        self.hero_b_combo = ttk.Combobox(hero_b_frame, textvariable=self.hero_b_var, 
                                         width=15, state="readonly")
        self.hero_b_combo.pack(side=tk.LEFT, padx=5)
        
        army_b_frame.columnconfigure(0, weight=1)
        
        # 영웅 목록 로드 및 설정
        self.load_heroes()
        
        # 옵션 프레임
        option_frame = ttk.Frame(main_frame)
        option_frame.pack(fill=tk.X, pady=5)
        
        self.multi_round_var = tk.BooleanVar()
        multi_round_check = ttk.Checkbutton(option_frame, text="멀티 라운드 전투 (한쪽 전멸까지)", 
                                           variable=self.multi_round_var)
        multi_round_check.pack(side=tk.LEFT, padx=5)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        calc_button = ttk.Button(button_frame, text="전투 계산", 
                                command=self.calculate_combat)
        calc_button.pack(side=tk.LEFT, padx=5)
        
        reset_button = ttk.Button(button_frame, text="초기화", 
                                 command=self.reset_inputs)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # 결과 섹션
        result_frame = ttk.LabelFrame(main_frame, text="전투 결과", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 결과 텍스트 영역
        self.result_text = tk.Text(result_frame, height=15, width=70, 
                                   wrap=tk.WORD, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", 
                                 command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def get_army_units(self, entries_dict):
        """입력 필드에서 병력 정보를 가져옵니다."""
        army_units = {}
        for unit_type, entry in entries_dict.items():
            try:
                value = int(entry.get())
                if value < 0:
                    raise ValueError("음수는 입력할 수 없습니다.")
                army_units[unit_type] = value
            except ValueError:
                raise ValueError(f"{unit_type}의 수량이 올바르지 않습니다. 정수를 입력하세요.")
        return army_units
    
    def get_food_value(self, entry):
        """식량 입력 값을 가져옵니다. '무제한'이면 None을 반환합니다."""
        value = entry.get().strip()
        if value == "무제한" or value == "":
            return None
        try:
            food = int(value)
            if food < 0:
                raise ValueError("식량은 음수일 수 없습니다.")
            return food
        except ValueError:
            raise ValueError("식량은 정수 또는 '무제한'이어야 합니다.")
    
    def get_hero(self, hero_var):
        """영웅 선택 값을 가져옵니다."""
        hero_name = hero_var.get()
        if hero_name == "없음" or hero_name == "":
            return None
        return self.calculator.heroes.get(hero_name)
    
    def calculate_combat(self):
        """전투를 계산하고 결과를 표시합니다."""
        try:
            # 입력값 검증 및 가져오기
            army_a_units = self.get_army_units(self.army_a_entries)
            army_b_units = self.get_army_units(self.army_b_entries)
            
            # 식량 가져오기
            food_a = self.get_food_value(self.food_a_entry)
            food_b = self.get_food_value(self.food_b_entry)
            
            # 영웅 가져오기
            hero_a = self.get_hero(self.hero_a_var)
            hero_b = self.get_hero(self.hero_b_var)
            
            # 양쪽 모두 병력이 있는지 확인
            total_a = sum(army_a_units.values())
            total_b = sum(army_b_units.values())
            
            if total_a == 0:
                messagebox.showwarning("경고", "A군에 병력이 없습니다.")
                return
            if total_b == 0:
                messagebox.showwarning("경고", "B군에 병력이 없습니다.")
                return
            
            # 멀티 라운드 옵션 확인
            if self.multi_round_var.get():
                # 멀티 라운드 전투
                multi_result = self.calculator.simulate_multi_round_combat(
                    army_a_units, army_b_units,
                    initial_food_a=food_a, initial_food_b=food_b,
                    hero_a=hero_a, hero_b=hero_b
                )
                self.display_multi_round_results(army_a_units, army_b_units, multi_result, 
                                                 food_a, food_b, hero_a, hero_b)
            else:
                # 단일 라운드 전투 (식량 무제한으로 간주)
                has_food_a = food_a is None or food_a > 0
                has_food_b = food_b is None or food_b > 0
                result = self.calculator.simulate_combat(
                    army_a_units, army_b_units,
                    has_food_a=has_food_a, has_food_b=has_food_b,
                    hero_a=hero_a, hero_b=hero_b
                )
                self.display_results(army_a_units, army_b_units, result, hero_a, hero_b)
            
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
        except Exception as e:
            messagebox.showerror("오류", f"계산 중 오류가 발생했습니다: {str(e)}")
    
    def display_results(self, army_a_units, army_b_units, result, hero_a=None, hero_b=None):
        """전투 결과를 텍스트 영역에 표시합니다."""
        self.result_text.delete(1.0, tk.END)
        
        output = []
        output.append("=" * 70)
        output.append("전투 결과")
        output.append("=" * 70)
        output.append("")
        
        # A군 정보
        output.append("【 A군 】")
        if hero_a:
            output.append(f"영웅: {hero_a.get('name', '없음')}")
        output.append(f"총 HP: {result['army_a_total_hp']:,.2f}")
        output.append(f"최종 공격력 (FAP): {result['army_a_fap']:,.2f}")
        output.append(f"사상률: {result['army_a_casualty_ratio']:.2%}")
        output.append("")
        output.append("  초기 병력:")
        for unit_type in self.unit_types:
            if army_a_units[unit_type] > 0:
                output.append(f"    {unit_type}: {army_a_units[unit_type]:,}명")
        output.append("")
        output.append("  사상자:")
        has_casualties = False
        for unit_type in self.unit_types:
            casualties = result['army_a_casualties'].get(unit_type, 0)
            if casualties > 0:
                output.append(f"    {unit_type}: {casualties:,}명")
                has_casualties = True
        if not has_casualties:
            output.append("    없음")
        output.append("")
        output.append("  잔존 병력:")
        has_remaining = False
        for unit_type in self.unit_types:
            remaining = result['army_a_remaining'].get(unit_type, 0)
            if remaining > 0:
                output.append(f"    {unit_type}: {remaining:,}명")
                has_remaining = True
        if not has_remaining:
            output.append("    전멸")
        output.append("")
        
        # B군 정보
        output.append("【 B군 】")
        if hero_b:
            output.append(f"영웅: {hero_b.get('name', '없음')}")
        output.append(f"총 HP: {result['army_b_total_hp']:,.2f}")
        output.append(f"최종 공격력 (FAP): {result['army_b_fap']:,.2f}")
        output.append(f"사상률: {result['army_b_casualty_ratio']:.2%}")
        output.append("")
        output.append("  초기 병력:")
        for unit_type in self.unit_types:
            if army_b_units[unit_type] > 0:
                output.append(f"    {unit_type}: {army_b_units[unit_type]:,}명")
        output.append("")
        output.append("  사상자:")
        has_casualties = False
        for unit_type in self.unit_types:
            casualties = result['army_b_casualties'].get(unit_type, 0)
            if casualties > 0:
                output.append(f"    {unit_type}: {casualties:,}명")
                has_casualties = True
        if not has_casualties:
            output.append("    없음")
        output.append("")
        output.append("  잔존 병력:")
        has_remaining = False
        for unit_type in self.unit_types:
            remaining = result['army_b_remaining'].get(unit_type, 0)
            if remaining > 0:
                output.append(f"    {unit_type}: {remaining:,}명")
                has_remaining = True
        if not has_remaining:
            output.append("    전멸")
        output.append("")
        output.append("=" * 70)
        
        self.result_text.insert(1.0, "\n".join(output))
        self.result_text.see(1.0)
    
    def display_multi_round_results(self, initial_army_a, initial_army_b, multi_result,
                                    food_a=None, food_b=None, hero_a=None, hero_b=None):
        """멀티 라운드 전투 결과를 텍스트 영역에 표시합니다."""
        self.result_text.delete(1.0, tk.END)
        
        output = []
        output.append("=" * 70)
        output.append("멀티 라운드 전투 결과")
        output.append("=" * 70)
        output.append("")
        output.append(f"총 라운드 수: {multi_result['total_rounds']}")
        output.append("")
        
        # 영웅 정보
        if hero_a or hero_b:
            output.append("영웅:")
            if hero_a:
                output.append(f"  A군: {hero_a.get('name', '없음')}")
            if hero_b:
                output.append(f"  B군: {hero_b.get('name', '없음')}")
            output.append("")
        
        # 최종 승자 표시
        winner = multi_result['final_winner']
        if winner == 'A':
            output.append("🏆 승리: A군")
        elif winner == 'B':
            output.append("🏆 승리: B군")
        else:
            output.append("⚠ 최대 라운드 도달 (무승부)")
        output.append("")
        output.append("=" * 70)
        output.append("")
        
        # 각 라운드별 상세 정보
        for round_data in multi_result['rounds']:
            round_num = round_data['round']
            output.append(f"━━━ 라운드 {round_num} ━━━")
            output.append("")
            
            # A군 정보
            output.append("【 A군 】")
            output.append(f"  초기 병력:")
            for unit_type in self.unit_types:
                initial = round_data['army_a_initial'].get(unit_type, 0)
                if initial > 0:
                    output.append(f"    {unit_type}: {initial:,}명")
            if 'food_a' in round_data:
                food_display = "무제한" if round_data['food_a'] is None else f"{round_data['food_a']:,}"
                food_consumption = round_data.get('food_consumption_a', 0)
                output.append(f"  식량: {food_display} (소비: {food_consumption})")
            output.append(f"  총 HP: {round_data['army_a_total_hp']:,.2f}")
            output.append(f"  최종 공격력 (FAP): {round_data['army_a_fap']:,.2f}")
            output.append(f"  사상률: {round_data['army_a_casualty_ratio']:.2%}")
            output.append("  사상자:")
            has_casualties = False
            for unit_type in self.unit_types:
                casualties = round_data['army_a_casualties'].get(unit_type, 0)
                if casualties > 0:
                    output.append(f"    {unit_type}: {casualties:,}명")
                    has_casualties = True
            if not has_casualties:
                output.append("    없음")
            output.append("  잔존 병력:")
            has_remaining = False
            for unit_type in self.unit_types:
                remaining = round_data['army_a_remaining'].get(unit_type, 0)
                if remaining > 0:
                    output.append(f"    {unit_type}: {remaining:,}명")
                    has_remaining = True
            if not has_remaining:
                output.append("    전멸")
            output.append("")
            
            # B군 정보
            output.append("【 B군 】")
            output.append(f"  초기 병력:")
            for unit_type in self.unit_types:
                initial = round_data['army_b_initial'].get(unit_type, 0)
                if initial > 0:
                    output.append(f"    {unit_type}: {initial:,}명")
            if 'food_b' in round_data:
                food_display = "무제한" if round_data['food_b'] is None else f"{round_data['food_b']:,}"
                food_consumption = round_data.get('food_consumption_b', 0)
                output.append(f"  식량: {food_display} (소비: {food_consumption})")
            output.append(f"  총 HP: {round_data['army_b_total_hp']:,.2f}")
            output.append(f"  최종 공격력 (FAP): {round_data['army_b_fap']:,.2f}")
            output.append(f"  사상률: {round_data['army_b_casualty_ratio']:.2%}")
            output.append("  사상자:")
            has_casualties = False
            for unit_type in self.unit_types:
                casualties = round_data['army_b_casualties'].get(unit_type, 0)
                if casualties > 0:
                    output.append(f"    {unit_type}: {casualties:,}명")
                    has_casualties = True
            if not has_casualties:
                output.append("    없음")
            output.append("  잔존 병력:")
            has_remaining = False
            for unit_type in self.unit_types:
                remaining = round_data['army_b_remaining'].get(unit_type, 0)
                if remaining > 0:
                    output.append(f"    {unit_type}: {remaining:,}명")
                    has_remaining = True
            if not has_remaining:
                output.append("    전멸")
            output.append("")
            output.append("-" * 70)
            output.append("")
        
        # 최종 상태
        output.append("=" * 70)
        output.append("최종 상태")
        output.append("=" * 70)
        output.append("")
        output.append("【 A군 최종 병력 】")
        final_a_total = sum(multi_result['final_army_a'].values())
        if final_a_total > 0:
            for unit_type in self.unit_types:
                remaining = multi_result['final_army_a'].get(unit_type, 0)
                if remaining > 0:
                    output.append(f"  {unit_type}: {remaining:,}명")
        else:
            output.append("  전멸")
        output.append("")
        output.append("【 B군 최종 병력 】")
        final_b_total = sum(multi_result['final_army_b'].values())
        if final_b_total > 0:
            for unit_type in self.unit_types:
                remaining = multi_result['final_army_b'].get(unit_type, 0)
                if remaining > 0:
                    output.append(f"  {unit_type}: {remaining:,}명")
        else:
            output.append("  전멸")
        output.append("")
        output.append("=" * 70)
        
        self.result_text.insert(1.0, "\n".join(output))
        self.result_text.see(1.0)
    
    def reset_inputs(self):
        """입력 필드를 초기화합니다."""
        for entry in self.army_a_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        for entry in self.army_b_entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        self.food_a_entry.delete(0, tk.END)
        self.food_a_entry.insert(0, "무제한")
        self.food_b_entry.delete(0, tk.END)
        self.food_b_entry.insert(0, "무제한")
        if hasattr(self, 'hero_a_combo'):
            self.hero_a_combo.current(0)
        if hasattr(self, 'hero_b_combo'):
            self.hero_b_combo.current(0)
        self.result_text.delete(1.0, tk.END)


def main():
    """메인 함수"""
    root = tk.Tk()
    app = CombatSimulatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

