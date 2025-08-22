import math
from enum import Enum
import json
from typing import Dict, List


class MonsterClass(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


class Spell:
    def __init__(self, name: str, damage: int = 0, mana_cost: int = 0,
                 heal: int = 0, atk_float_buff: float = 0.0, atk_percent_buff: float = 0.0,
                 atk_float_debuff: float = 0.0, atk_percent_debuff: float = 0.0,
                 armor_buff: int = 0, armor_debuff: int = 0, duration: int = 0,
                 end_turn: bool = True):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.heal = heal
        self.atk_float_buff = atk_float_buff  # Плавающий бафф к атаке
        self.atk_percent_buff = atk_percent_buff  # Процентный бафф к атаке
        self.atk_float_debuff = atk_float_debuff  # Плавающий дебафф к атаке врага
        self.atk_percent_debuff = atk_percent_debuff  # Процентный дебафф к атаке врага
        self.armor_buff = armor_buff  # Абсолютный бафф к броне
        self.armor_debuff = armor_debuff  # Абсолютный дебафф к броне врага
        self.duration = duration  # Длительность эффекта в ходах
        self.end_turn = end_turn  # Завершает ли ход после использования

    def __str__(self):
        effects = []
        if self.damage > 0:
            effects.append(f"урон: {self.damage}")
        if self.mana_cost > 0:
            effects.append(f"мана: {self.mana_cost}")
        if self.heal > 0:
            effects.append(f"лечение: {self.heal}")
        if self.atk_float_buff != 0:
            effects.append(f"бафф атаки: {self.atk_float_buff:+}")
        if self.atk_percent_buff != 0:
            effects.append(f"бафф атаки: {self.atk_percent_buff * 100:+.1f}%")
        if self.atk_float_debuff != 0:
            effects.append(f"дебафф атаки врага: {self.atk_float_debuff:+}")
        if self.atk_percent_debuff != 0:
            effects.append(f"дебафф атаки врага: {self.atk_percent_debuff * 100:+.1f}%")
        if self.armor_buff != 0:
            effects.append(f"бафф брони: {self.armor_buff:+}")
        if self.armor_debuff != 0:
            effects.append(f"дебафф брони врага: {self.armor_debuff:+}")
        if self.duration > 0:
            effects.append(f"длительность: {self.duration} ходов")
        if not self.end_turn:
            effects.append("не завершает ход")

        return f"{self.name} ({', '.join(effects)})"


class Enemy:
    def __init__(self, name: str, hp: int, damage: int, mana: int,
                 monster_class: MonsterClass, spells: List[Spell], armor: int = 0):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.mana = mana
        self.max_mana = mana
        self.armor = armor
        self.monster_class = monster_class
        self.spells = spells

    def __str__(self):
        spells_info = "\n  ".join([str(spell) for spell in self.spells])
        return (f"{self.name} (Класс: {self.monster_class.value})\n"
                f"  Здоровье: {self.hp}/{self.max_hp}\n"
                f"  Урон: {self.damage}\n"
                f"  Мана: {self.mana}/{self.max_mana}\n"
                f"  Броня: {self.armor}\n"
                f"  Заклинания:\n  {spells_info}")

    @classmethod
    def load_from_json(cls, file_path: str) -> List['Enemy']:
        enemies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for enemy_data in data.get('enemies', []):
                    # Получаем класс монстра
                    monster_class = MonsterClass[enemy_data['monster_class']]

                    # Устанавливаем длительность баффов/дебаффов для монстров класса F
                    default_duration = 2 if monster_class == MonsterClass.F else 1

                    # Создаем список заклинаний
                    spells = []
                    for spell_data in enemy_data.get('spells', []):
                        # Устанавливаем длительность по умолчанию для баффов/дебаффов
                        duration = spell_data.get('duration',
                                                  default_duration if any([
                                                      spell_data.get('atk_float_buff', 0) != 0,
                                                      spell_data.get('atk_percent_buff', 0) != 0,
                                                      spell_data.get('atk_float_debuff', 0) != 0,
                                                      spell_data.get('atk_percent_debuff', 0) != 0,
                                                      spell_data.get('armor_buff', 0) != 0,
                                                      spell_data.get('armor_debuff', 0) != 0
                                                  ]) else 0)

                        spell = Spell(
                            name=spell_data['name'],
                            damage=spell_data.get('damage', 0),
                            mana_cost=spell_data.get('mana_cost', 0),
                            heal=spell_data.get('heal', 0),
                            atk_float_buff=spell_data.get('atk_float_buff', 0.0),
                            atk_percent_buff=spell_data.get('atk_percent_buff', 0.0),
                            atk_float_debuff=spell_data.get('atk_float_debuff', 0.0),
                            atk_percent_debuff=spell_data.get('atk_percent_debuff', 0.0),
                            armor_buff=spell_data.get('armor_buff', 0),
                            armor_debuff=spell_data.get('armor_debuff', 0),
                            duration=duration,
                            end_turn=spell_data.get('end_turn', True)
                        )
                        spells.append(spell)

                    # Создаем врага
                    enemy = cls(
                        name=enemy_data['name'],
                        hp=enemy_data['hp'],
                        damage=enemy_data['damage'],
                        mana=enemy_data['mana'],
                        armor=enemy_data.get('armor', 0),
                        monster_class=monster_class,
                        spells=spells
                    )

                    enemies.append(enemy)

        except FileNotFoundError:
            print(f"Файл {file_path} не найден.")
        except KeyError as e:
            print(f"Ошибка в структуре JSON: отсутствует ключ {e}")
        except Exception as e:
            print(f"Ошибка при загрузке врагов: {e}")

        return enemies


class EquipmentSlot(Enum):
    MAIN_HAND = "правая рука"
    OFF_HAND = "левая рука"
    HEAD = "голова"
    BODY = "тело"
    LEGS = "ноги"
    BOOTS = "ботинки"
    ACCESSORY_1 = "аксессуар 1"
    ACCESSORY_2 = "аксессуар 2"
    ACCESSORY_3 = "аксессуар 3"


class ItemType(Enum):
    WEAPON = "оружие"
    ARMOR = "броня"
    CONSUMABLE = "расходуемое"
    ACCESSORY = "аксессуар"


class Item:
    def __init__(self, name, item_type, slot_type, atk_bonus=0, damage_scale=0,
                 defense=0, dodge_bonus=0, hp_bonus=0, mana_bonus=0):
        self.name = name
        self.item_type = item_type
        self.slot_type = slot_type if slot_type is not None else []
        self.atk_bonus = atk_bonus
        self.damage_scale = damage_scale
        self.defense = defense
        self.dodge_bonus = dodge_bonus
        self.hp_bonus = hp_bonus
        self.mana_bonus = mana_bonus
        # Проверяем, является ли оружие двуручным
        self.is_two_handed = (len(self.slot_type) == 2 and
                              EquipmentSlot.MAIN_HAND in self.slot_type and
                              EquipmentSlot.OFF_HAND in self.slot_type)

    def __str__(self):
        return f"{self.name} ({self.item_type.value})"


class Character:
    _class_bonuses = {
        'warrior': {'str': 20, 'dex': 5, 'mag': 0, 'hp_bonus': 20, 'main_attr': 'str', 'dodge_multiplier': 0.7},
        'mage': {'str': 5, 'dex': 5, 'mag': 15, 'hp_bonus': 10, 'main_attr': 'mag', 'dodge_multiplier': 0.5},
        'assassin': {'str': 10, 'dex': 15, 'mag': 5, 'hp_bonus': 5, 'main_attr': 'dex', 'dodge_multiplier': 1.0}
    }

    _starting_items = {
        'warrior': [
            Item("Длинный меч", ItemType.WEAPON, [EquipmentSlot.MAIN_HAND], atk_bonus=10)
        ],
        'mage': [
            Item("Посох мага", ItemType.WEAPON, [EquipmentSlot.MAIN_HAND], atk_bonus=5, damage_scale=0.1)
        ],
        'assassin': [
            Item("Кинжал вдовца", ItemType.WEAPON, [EquipmentSlot.MAIN_HAND], atk_bonus=5),
            Item("Кинжал сироты", ItemType.WEAPON, [EquipmentSlot.OFF_HAND], atk_bonus=5)
        ]
    }

    def __init__(self, name, char_class):
        self.name = name

        # Преобразуем в число, если передана строка
        if isinstance(char_class, str):
            try:
                char_class = int(char_class)
            except ValueError:
                pass

        # Определяем класс
        if char_class == 1:
            self.char_class = 'warrior'
        elif char_class == 2:
            self.char_class = 'mage'
        elif char_class == 3:
            self.char_class = 'assassin'
        else:
            # Если передан не номер, а прямое название класса
            self.char_class = char_class.lower()

        if self.char_class not in self._class_bonuses:
            raise ValueError("Недопустимый класс персонажа")

        bonuses = self._class_bonuses[self.char_class]
        self.strength = bonuses['str']
        self.dexterity = bonuses['dex']
        self.magic = bonuses['mag']
        self.main_attr = bonuses['main_attr']
        self.dodge_multiplier = bonuses['dodge_multiplier']

        # Основные характеристики
        self.max_hp = self.strength * 10 + bonuses['hp_bonus']
        self.hp = self.max_hp
        self.max_mana = self.magic * 10
        self.mana = self.max_mana

        # Боевые параметры (изначально нулевые)
        self.spell_damage = 0
        self.atk_scale = 1.0
        self.debuff_atk_scale = 1.0
        self.float_buffs = 0

        # Экипировка
        self.equipment = {
            EquipmentSlot.MAIN_HAND: None,
            EquipmentSlot.OFF_HAND: None,
            EquipmentSlot.HEAD: None,
            EquipmentSlot.BODY: None,
            EquipmentSlot.LEGS: None,
            EquipmentSlot.BOOTS: None,
            EquipmentSlot.ACCESSORY_1: None,
            EquipmentSlot.ACCESSORY_2: None,
            EquipmentSlot.ACCESSORY_3: None
        }

        # Инвентарь
        self.inventory = []

        # Добавляем стартовые предметы
        self.add_starting_items()

        # Экипируем стартовое оружие
        self.equip_starting_weapon()

    def add_starting_items(self):
        # Добавляем 3 зелья лечения (используем пустой список для slot_type)
        health_potion = Item("Зелье лечения", ItemType.CONSUMABLE, [], hp_bonus=100)
        for _ in range(3):
            self.inventory.append(health_potion)

        # Добавляем стартовое оружие в зависимости от класса
        if self.char_class in self._starting_items:
            for item in self._starting_items[self.char_class]:
                self.inventory.append(item)

    def equip_starting_weapon(self):
        # Экипируем стартовое оружие
        if self.char_class in self._starting_items:
            for item in self._starting_items[self.char_class]:
                if item.item_type == ItemType.WEAPON:
                    self.equip_weapon(item)

    def calculate_base_dodge_chance(self):
        # Формула убывающей полезности: 0 ловкости = 0%, 100 ловкости ≈ 60%, 200 ловкости ≈ 90%
        return 99 * (1 - math.exp(-0.024 * self.dexterity))

    def calculate_equipment_bonuses(self):
        # Рассчитываем бонусы от всей экипировки
        weapon_atk_bonus = 0
        equipment_atk_bonus = 0
        weapon_damage_scale = 0
        equipment_damage_scale = 0
        dodge_bonus = 0
        defense = 0
        hp_bonus = 0
        mana_bonus = 0

        for item in self.equipment.values():
            if item:
                dodge_bonus += item.dodge_bonus
                defense += item.defense
                hp_bonus += item.hp_bonus
                mana_bonus += item.mana_bonus

                # Разделяем бонусы оружия и остальной экипировки
                if item.item_type == ItemType.WEAPON:
                    weapon_atk_bonus += item.atk_bonus
                    weapon_damage_scale += item.damage_scale
                else:
                    equipment_atk_bonus += item.atk_bonus
                    equipment_damage_scale += item.damage_scale

        return {
            'weapon_atk_bonus': weapon_atk_bonus,
            'equipment_atk_bonus': equipment_atk_bonus,
            'weapon_damage_scale': weapon_damage_scale,
            'equipment_damage_scale': equipment_damage_scale,
            'dodge_bonus': dodge_bonus,
            'defense': defense,
            'hp_bonus': hp_bonus,
            'mana_bonus': mana_bonus
        }

    def calculate_damage(self):
        # Получаем бонусы от экипировки
        bonuses = self.calculate_equipment_bonuses()

        # Получаем значение основного атрибута
        if self.main_attr == 'str':
            main_attr_value = self.strength
        elif self.main_attr == 'dex':
            main_attr_value = self.dexterity
        else:  # mag
            main_attr_value = self.magic

        # Формула урона
        damage = ((main_attr_value + self.spell_damage +
                   bonuses['weapon_atk_bonus'] + bonuses['equipment_atk_bonus']) *
                  self.atk_scale * self.debuff_atk_scale *
                  (1 + bonuses['weapon_damage_scale'] + bonuses['equipment_damage_scale'])) + self.float_buffs

        return max(1, damage)  # Минимальный урон - 1

    def get_effective_dodge_chance(self):
        # Получаем бонусы от экипировки
        bonuses = self.calculate_equipment_bonuses()

        # Базовая вероятность уворота + бонусы от экипировки, умноженные на множитель класса
        base_dodge = self.calculate_base_dodge_chance()
        total_dodge = (base_dodge + bonuses['dodge_bonus']) * self.dodge_multiplier

        return min(95, total_dodge)  # Максимум 95%

    def get_effective_hp(self):
        # Получаем бонусы от экипировки
        bonuses = self.calculate_equipment_bonuses()

        # Базовое здоровье + бонусы от экипировки
        return self.max_hp + bonuses['hp_bonus']

    def get_effective_mana(self):
        # Получаем бонусы от экипировки
        bonuses = self.calculate_equipment_bonuses()

        # Базовая мана + бонусы от экипировки
        return self.max_mana + bonuses['mana_bonus']

    def equip_weapon(self, weapon):
        """Экипирует оружие с учетом типа и занятости слотов"""
        if weapon.is_two_handed:
            # Для двуручного оружия
            if (self.equipment[EquipmentSlot.MAIN_HAND] is None and
                    self.equipment[EquipmentSlot.OFF_HAND] is None):
                # Оба слота свободны - экипируем
                self.equipment[EquipmentSlot.MAIN_HAND] = weapon
                self.equipment[EquipmentSlot.OFF_HAND] = weapon
                print(f"Экипировано двуручное оружие: {weapon.name}")
                return True
            else:
                # Слоты заняты - предлагаем выбор
                print("Оба слота для оружия заняты. Хотите заменить текущее оружие?")
                print("1 - Да, заменить")
                print("2 - Нет, отменить")

                try:
                    choice = int(input("Ваш выбор: "))
                    if choice == 1:
                        # Убираем текущее оружие в инвентарь
                        if self.equipment[EquipmentSlot.MAIN_HAND]:
                            old_weapon = self.equipment[EquipmentSlot.MAIN_HAND]
                            self.inventory.append(old_weapon)
                        if (self.equipment[EquipmentSlot.OFF_HAND] and
                                self.equipment[EquipmentSlot.OFF_HAND] != self.equipment[EquipmentSlot.MAIN_HAND]):
                            old_weapon = self.equipment[EquipmentSlot.OFF_HAND]
                            self.inventory.append(old_weapon)

                        # Экипируем новое оружие
                        self.equipment[EquipmentSlot.MAIN_HAND] = weapon
                        self.equipment[EquipmentSlot.OFF_HAND] = weapon
                        print(f"Экипировано двуручное оружие: {weapon.name}")
                        return True
                    else:
                        print("Экипировка отменена.")
                        return False
                except ValueError:
                    print("Неверный ввод. Экипировка отменена.")
                    return False
        else:
            # Для одноручного оружия
            available_slots = []

            # Проверяем доступные слоты для этого оружия
            for slot in weapon.slot_type:
                if self.equipment[slot] is None:
                    available_slots.append(slot)

            if available_slots:
                # Есть свободные слоты - экипируем в первый доступный
                slot = available_slots[0]
                self.equipment[slot] = weapon
                print(f"Экипировано оружие: {weapon.name} в слот {slot.value}")
                return True
            else:
                # Все слоты заняты - предлагаем выбор
                print("Все подходящие слоты заняты. Выберите слот для замены:")
                slot_options = []

                for i, slot in enumerate(weapon.slot_type):
                    print(f"{i + 1} - {slot.value} (сейчас: {self.equipment[slot].name})")
                    slot_options.append(slot)

                print(f"{len(weapon.slot_type) + 1} - Отменить экипировку")

                try:
                    choice = int(input("Ваш выбор: "))
                    if 1 <= choice <= len(weapon.slot_type):
                        selected_slot = slot_options[choice - 1]

                        # Убираем текущее оружие в инвентарь
                        old_weapon = self.equipment[selected_slot]
                        self.inventory.append(old_weapon)

                        # Экипируем новое оружие
                        self.equipment[selected_slot] = weapon
                        print(f"Экипировано оружие: {weapon.name} в слот {selected_slot.value}")
                        return True
                    else:
                        print("Экипировка отменена.")
                        return False
                except ValueError:
                    print("Неверный ввод. Экипировка отменена.")
                    return False

    def equip_armor(self, armor, slot):
        """Экипирует броню в указанный слот"""
        if self.equipment[slot] is None:
            # Слот свободен - экипируем
            self.equipment[slot] = armor
            print(f"Экипировано: {armor.name} в слот {slot.value}")
            return True
        else:
            # Слот занят - предлагаем замену
            print(f"Слот {slot.value} уже занят предметом: {self.equipment[slot].name}")
            print("Хотите заменить?")
            print("1 - Да, заменить")
            print("2 - Нет, отменить")

            try:
                choice = int(input("Ваш выбор: "))
                if choice == 1:
                    # Убираем текущую броню в инвентарь
                    old_armor = self.equipment[slot]
                    self.inventory.append(old_armor)

                    # Экипируем новую броню
                    self.equipment[slot] = armor
                    print(f"Экипировано: {armor.name} в слот {slot.value}")
                    return True
                else:
                    print("Экипировка отменена.")
                    return False
            except ValueError:
                print("Неверный ввод. Экипировка отменена.")
                return False

    def unequip_item(self, slot):
        if self.equipment[slot] is None:
            print(f"Слот {slot.value} пуст")
            return None

        item = self.equipment[slot]
        self.equipment[slot] = None

        # Для двуручного оружия освобождаем оба слота
        if (item.item_type == ItemType.WEAPON and item.is_two_handed and
                slot in [EquipmentSlot.MAIN_HAND, EquipmentSlot.OFF_HAND]):
            other_slot = EquipmentSlot.OFF_HAND if slot == EquipmentSlot.MAIN_HAND else EquipmentSlot.MAIN_HAND
            if self.equipment[other_slot] == item:
                self.equipment[other_slot] = None

        print(f"Предмет {item.name} снят с слота {slot.value}")
        return item

    def use_item(self, item_index):
        if item_index < 0 or item_index >= len(self.inventory):
            print("Неверный индекс предмета")
            return False

        item = self.inventory[item_index]

        if item.item_type != ItemType.CONSUMABLE:
            print("Этот предмет нельзя использовать")
            return False

        # Применяем эффект зелья
        if item.hp_bonus > 0:
            self.hp = min(self.get_effective_hp(), self.hp + item.hp_bonus)
            print(f"Использовано зелье лечения. Восстановлено {item.hp_bonus} HP.")

        # Удаляем предмет из инвентаря
        self.inventory.pop(item_index)
        return True

    def show_inventory(self):
        print("\n--- ИНВЕНТАРЬ ---")
        if not self.inventory:
            print("Инвентарь пуст")
            return

        for i, item in enumerate(self.inventory):
            print(f"{i + 1}. {item}")

    def show_equipment(self):
        print("\n--- ЭКИПИРОВКА ---")
        for slot, item in self.equipment.items():
            item_name = item.name if item else "Пусто"
            print(f"{slot.value}: {item_name}")

    def __str__(self):
        # Получаем название основного атрибута на русском
        attr_names = {'str': 'сила', 'dex': 'ловкость', 'mag': 'магия'}
        main_attr_name = attr_names.get(self.main_attr, self.main_attr)

        # Получаем бонусы от экипировки
        bonuses = self.calculate_equipment_bonuses()

        return (f"{self.name} ({self.char_class}):\n"
                f"  Характеристики: сила {self.strength}, ловкость {self.dexterity}, магия {self.magic}\n"
                f"  Основной атрибут: {main_attr_name}\n"
                f"  Здоровье: {self.hp}/{self.get_effective_hp()}\n"
                f"  Мана: {self.mana}/{self.get_effective_mana()}\n"
                f"  Шанс уворота: {self.get_effective_dodge_chance():.1f}% (множитель класса: {self.dodge_multiplier})\n"
                f"  Защита: {bonuses['defense']}\n"
                f"  Урон: {self.calculate_damage():.1f}")


# Пример использования:
def create_character():
    # name = input("Введите имя персонажа: ")
    name = 'Dumpy'
    char_class = 2
    print('''Выберите класс
        1) Воин
        2) Маг
        3) Ассасин
        Ваш выбор: ''')

    try:
        character = Character(name, char_class)
        print("\nПерсонаж создан успешно!")
        print(character)
        character.show_equipment()
        character.show_inventory()
        return character
    except ValueError as e:
        print(f"Ошибка: {e}")
        return None


if __name__ == '__main__':
    # Создание персонажа
    hero = create_character()

    # Загружаем врагов из JSON файла
    enemies = Enemy.load_from_json('enemies.json')

    for enemy in enemies:
        print(enemy)
        print("\n" + "=" * 40 + "\n")