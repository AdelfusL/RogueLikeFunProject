import random
import math
from enum import Enum
import json
from typing import Dict, List, Optional


class Spell:
    def __init__(self, name: str, damage: int = 0, mana_cost: int = 0,
                 heal: int = 0, atk_float_buff: float = 0.0, atk_percent_buff: float = 0.0,
                 atk_float_debuff: float = 0.0, atk_percent_debuff: float = 0.0,
                 armor_buff: int = 0, armor_debuff: int = 0, evade_buff: float = 0, evade_debuff: float = 0,
                 duration: int = 0, end_turn: bool = True, aimed_to_self: bool = True,
                 is_buff: bool = False, aimed_to: int = 0):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.heal = heal
        self.atk_float_buff = atk_float_buff
        self.atk_percent_buff = atk_percent_buff
        self.atk_float_debuff = atk_float_debuff
        self.atk_percent_debuff = atk_percent_debuff
        self.armor_buff = armor_buff
        self.armor_debuff = armor_debuff
        self.evade_buff = evade_buff
        self.evade_debuff = evade_debuff
        self.duration = duration
        self.end_turn = end_turn
        self.aimed_to_self = aimed_to_self
        self.is_buff = is_buff
        self.aimed_to = aimed_to  # aimed_to мог бы пригодиться для реализовать множественных цели или более сложные схемы выбора цели для врагов. но пока не используется

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
        if self.evade_buff != 0:
            effects.append(f"бафф уклонения: {self.evade_buff:+.1f}")
        if self.evade_debuff != 0:
            effects.append(f"дебафф уклонения: {self.evade_debuff:+.1f}")
        if self.duration > 0:
            effects.append(f"длительность: {self.duration} ходов")
        if not self.end_turn:
            effects.append("не завершает ход")
        if not self.aimed_to_self:
            effects.append("направлено на врага")

        return f"{self.name} ({', '.join(effects)})"


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
        self.is_two_handed = (len(self.slot_type) == 2 and
                              EquipmentSlot.MAIN_HAND in self.slot_type and
                              EquipmentSlot.OFF_HAND in self.slot_type)

    def __str__(self):
        return f"{self.name} ({self.item_type.value})"


class Effect:
    def __init__(self, name: str, duration: int,
                 atk_float_buff: float = 0.0, atk_percent_buff: float = 0.0,
                 atk_float_debuff: float = 0.0, atk_percent_debuff: float = 0.0,
                 armor_buff: int = 0, armor_debuff: int = 0,
                 evade_buff: float = 0, evade_debuff: float = 0):
        self.name = name
        self.duration = duration
        self.atk_float_buff = atk_float_buff
        self.atk_percent_buff = atk_percent_buff
        self.atk_float_debuff = atk_float_debuff
        self.atk_percent_debuff = atk_percent_debuff
        self.armor_buff = armor_buff
        self.armor_debuff = armor_debuff
        self.evade_buff = evade_buff
        self.evade_debuff = evade_debuff

    def __str__(self):
        effects = []
        if self.atk_float_buff != 0:
            effects.append(f"бафф атаки: {self.atk_float_buff:+}")
        if self.atk_percent_buff != 0:
            effects.append(f"бафф атаки: {self.atk_percent_buff * 100:+.1f}%")
        if self.atk_float_debuff != 0:
            effects.append(f"дебафф атаки: {self.atk_float_debuff:+}")
        if self.atk_percent_debuff != 0:
            effects.append(f"дебафф атаки: {self.atk_percent_debuff * 100:+.1f}%")
        if self.armor_buff != 0:
            effects.append(f"бафф брони: {self.armor_buff:+}")
        if self.armor_debuff != 0:
            effects.append(f"дебафф брони: {self.armor_debuff:+}")
        if self.evade_buff != 0:
            effects.append(f"бафф уклонения: {self.evade_buff:+.1f}")
        if self.evade_debuff != 0:
            effects.append(f"дебафф уклонения: {self.evade_debuff:+.1f}")

        return f"{self.name} ({', '.join(effects)}), длительность: {self.duration} ходов"


class Character:
    _heroes_data = {}
    _loaded_heroes = {}

    @classmethod
    def load_heroes_from_json(cls, file_path: str, specific_classes: List[str] = None):  # List[str] = ['warrior', 'mage']
        """Загружает героев из JSON файла, опционально только указанные классы"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                cls._heroes_data = {}
                cls._loaded_heroes = {}

                for hero_data in data.get('heroes', []):
                    hero_class = hero_data['class']

                    if specific_classes and hero_class not in specific_classes:
                        continue

                    cls._heroes_data[hero_class] = hero_data
                    cls._loaded_heroes[hero_class] = hero_data

                if not cls._heroes_data:
                    print("Предупреждение: не загружено ни одного класса героев!")

        except FileNotFoundError:
            print(f"Файл {file_path} не найден.")
        except Exception as e:
            print(f"Ошибка при загрузке героев: {e}")

    def __init__(self, name, char_class):
        self.name = name

        # Загружаем героев, если еще не загружены
        if not self._heroes_data:
            self.load_heroes_from_json('heroes.json')

        # Проверяем, что класс существует в загруженных данных
        if char_class not in self._heroes_data:
            raise ValueError(f"Недопустимый класс персонажа: {char_class}")

        self.char_class = char_class

        # Получаем данные героя
        hero_data = self._heroes_data[self.char_class]
        bonuses = hero_data['bonuses']

        self.strength = bonuses['str']
        self.dexterity = bonuses['dex']
        self.magic = bonuses['mag']
        self.main_attr = bonuses['main_attr']
        self.dodge_multiplier = bonuses['dodge_multiplier']
        self.is_hero = True
        self.alive = True  # Добавляем флаг живой/мертвый
        self.max_hp = self.strength * 10 + bonuses.get('hp_bonus', 0)
        self.hp = self.max_hp
        self.max_mana = self.magic * 10
        self.mana = self.max_mana

        # Бонус восстановления маны (по умолчанию 1.0)
        self.mana_amplification_bonus = bonuses.get('mana_amplification_bonus', 1.0)

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

        self.inventory = []
        self.spells = []

        self.add_starting_items(hero_data.get('starting_items', []))
        self.add_starting_spells(hero_data.get('starting_spells', []))
        self.equip_starting_weapon(hero_data.get('starting_items', []))

    def __str__(self):
        class_name = self._heroes_data.get(self.char_class, {}).get('name', self.char_class)
        status = "живой" if self.alive else "мертвый"
        return (f"Персонаж: {self.name} ({status})\n"
                f"Класс: {class_name}\n"
                f"Здоровье: {self.hp:.1f}/{self.get_effective_hp():.1f}\n"
                f"Мана: {self.mana:.1f}/{self.get_effective_mana():.1f}\n"
                f"Сила: {self.strength}\n"
                f"Ловкость: {self.dexterity}\n"
                f"Магия: {self.magic}\n"
                f"Урон: {self.calculate_damage():.1f}\n"
                f"Уклонение: {self.get_effective_dodge_chance():.1f}%")

    def add_starting_items(self, starting_items_data):
        # Добавляем зелья лечения
        health_potion = Item("Зелье лечения", ItemType.CONSUMABLE, [], hp_bonus=100)
        for _ in range(3):
            self.inventory.append(health_potion)

        # Добавляем стартовые предметы из JSON
        for item_data in starting_items_data:
            slot_type = [EquipmentSlot[slot] for slot in item_data.get('slot_type', [])]

            item = Item(
                name=item_data['name'],
                item_type=ItemType[item_data['item_type']],
                slot_type=slot_type,
                atk_bonus=item_data.get('atk_bonus', 0),
                damage_scale=item_data.get('damage_scale', 0),
                defense=item_data.get('defense', 0),
                dodge_bonus=item_data.get('dodge_bonus', 0),
                hp_bonus=item_data.get('hp_bonus', 0),
                mana_bonus=item_data.get('mana_bonus', 0)
            )
            self.inventory.append(item)

    def add_starting_spells(self, starting_spells_data):
        for spell_data in starting_spells_data:
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
                evade_buff=spell_data.get('evade_buff', 0),
                evade_debuff=spell_data.get('evade_debuff', 0),
                duration=spell_data.get('duration', 0),
                end_turn=spell_data.get('end_turn', True),
                aimed_to_self=spell_data.get('aimed_to_self', True),
                is_buff=spell_data.get('is_buff', False),
                aimed_to=spell_data.get('aimed_to', 0)
            )
            self.spells.append(spell)

    def equip_starting_weapon(self, starting_items_data):
        for item_data in starting_items_data:
            if item_data['item_type'] == 'WEAPON':
                slot_type = [EquipmentSlot[slot] for slot in item_data.get('slot_type', [])]

                item = Item(
                    name=item_data['name'],
                    item_type=ItemType[item_data['item_type']],
                    slot_type=slot_type,
                    atk_bonus=item_data.get('atk_bonus', 0),
                    damage_scale=item_data.get('damage_scale', 0)
                )
                self.equip_weapon(item)

    def calculate_base_dodge_chance(self):
        return 99 * (1 - math.exp(-0.024 * self.dexterity))

    def calculate_equipment_bonuses(self):
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
        bonuses = self.calculate_equipment_bonuses()

        if self.main_attr == 'str':
            main_attr_value = self.strength
        elif self.main_attr == 'dex':
            main_attr_value = self.dexterity
        else:
            main_attr_value = self.magic

        damage = ((main_attr_value + self.spell_damage +
                   bonuses['weapon_atk_bonus'] + bonuses['equipment_atk_bonus']) *
                  self.atk_scale * self.debuff_atk_scale *
                  (1 + bonuses['weapon_damage_scale'] + bonuses['equipment_damage_scale'])) + self.float_buffs

        return max(1, damage)

    def get_effective_dodge_chance(self):
        bonuses = self.calculate_equipment_bonuses()
        base_dodge = self.calculate_base_dodge_chance()
        total_dodge = (base_dodge + bonuses['dodge_bonus']) * self.dodge_multiplier
        return min(95, total_dodge)

    def get_effective_hp(self):
        bonuses = self.calculate_equipment_bonuses()
        return self.max_hp + bonuses['hp_bonus']

    def get_effective_mana(self):
        bonuses = self.calculate_equipment_bonuses()
        return self.max_mana + bonuses['mana_bonus']

    def equip_weapon(self, weapon):
        if weapon.is_two_handed:
            if (self.equipment[EquipmentSlot.MAIN_HAND] is None and
                    self.equipment[EquipmentSlot.OFF_HAND] is None):
                self.equipment[EquipmentSlot.MAIN_HAND] = weapon
                self.equipment[EquipmentSlot.OFF_HAND] = weapon
                print(f"Экипировано двуручное оружие: {weapon.name}")
                return True
            else:
                print("Оба слота для оружия заняты. Хотите заменить текущее оружие?")
                print("1 - Да, заменить")
                print("2 - Нет, отменить")

                try:
                    choice = int(input("Ваш выбор: "))
                    if choice == 1:
                        if self.equipment[EquipmentSlot.MAIN_HAND]:
                            old_weapon = self.equipment[EquipmentSlot.MAIN_HAND]
                            self.inventory.append(old_weapon)
                        if (self.equipment[EquipmentSlot.OFF_HAND] and
                                self.equipment[EquipmentSlot.OFF_HAND] != self.equipment[EquipmentSlot.MAIN_HAND]):
                            old_weapon = self.equipment[EquipmentSlot.OFF_HAND]
                            self.inventory.append(old_weapon)

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
            available_slots = []

            for slot in weapon.slot_type:
                if self.equipment[slot] is None:
                    available_slots.append(slot)

            if available_slots:
                slot = available_slots[0]
                self.equipment[slot] = weapon
                print(f"Экипировано оружие: {weapon.name} в слот {slot.value}")
                return True
            else:
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
                        old_weapon = self.equipment[selected_slot]
                        self.inventory.append(old_weapon)
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
        if self.equipment[slot] is None:
            self.equipment[slot] = armor
            print(f"Экипировано: {armor.name} в слот {slot.value}")
            return True
        else:
            print(f"Слот {slot.value} уже занят предметом: {self.equipment[slot].name}")
            print("Хотите заменить?")
            print("1 - Да, заменить")
            print("2 - Нет, отменить")

            try:
                choice = int(input("Ваш выбор: "))
                if choice == 1:
                    old_armor = self.equipment[slot]
                    self.inventory.append(old_armor)
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

        if item.hp_bonus > 0:
            self.hp = min(self.get_effective_hp(), self.hp + item.hp_bonus)
            print(f"Использовано зелье лечения. Восстановлено {item.hp_bonus} HP.")

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

    def show_spells(self):
        print("\n--- ЗАКЛИНАНИЯ ---")
        if not self.spells:
            print("Заклинаний нет")
            return

        for i, spell in enumerate(self.spells):
            print(f"{i + 1}. {spell}")


class MonsterClass(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


class Enemy:
    def __init__(self, name: str, hp: int, damage: int, mana: int, evade: float,
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
        self.evade = evade
        self.is_hero = False
        self.alive = True  # Добавляем флаг живой/мертвый

    def __str__(self):
        status = "живой" if self.alive else "мертвый"
        spells_info = "\n  ".join([str(spell) for spell in self.spells])
        return (f"{self.name} (Класс: {self.monster_class.value}, {status})\n"
                f"  Здоровье: {self.hp}/{self.max_hp}\n"
                f"  Урон: {self.damage}\n"
                f"  Мана: {self.mana}/{self.max_mana}\n"
                f"  Броня: {self.armor}\n"
                f"  Уклонение: {self.evade:.1f}%\n"
                f"  Заклинания:\n  {spells_info}")

    @classmethod
    def load_from_json(cls, file_path: str) -> List['Enemy']:
        enemies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for enemy_data in data.get('enemies', []):
                    monster_class = MonsterClass[enemy_data['monster_class']]
                    default_duration = 2 if monster_class == MonsterClass.F else 1

                    spells = []
                    for spell_data in enemy_data.get('spells', []):
                        duration = spell_data.get('duration',
                                                  default_duration if any([
                                                      spell_data.get('atk_float_buff', 0) != 0,
                                                      spell_data.get('atk_percent_buff', 0) != 0,
                                                      spell_data.get('atk_float_debuff', 0) != 0,
                                                      spell_data.get('atk_percent_debuff', 0) != 0,
                                                      spell_data.get('armor_buff', 0) != 0,
                                                      spell_data.get('armor_debuff', 0) != 0,
                                                      spell_data.get('evade_buff', 0) != 0,
                                                      spell_data.get('evade_debuff', 0) != 0
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
                            evade_buff=spell_data.get('evade_buff', 0),
                            evade_debuff=spell_data.get('evade_debuff', 0),
                            duration=duration,
                            end_turn=spell_data.get('end_turn', True),
                            aimed_to_self=spell_data.get('aimed_to_self', True)
                        )
                        spells.append(spell)

                    enemy = cls(
                        name=enemy_data['name'],
                        hp=enemy_data['hp'],
                        damage=enemy_data['damage'],
                        mana=enemy_data['mana'],
                        evade=enemy_data.get('evade', 0),
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


class Battle:
    def __init__(self, hero: Character, enemies: List[Enemy]):
        self.hero = hero
        self.enemies = enemies
        self.participants = [hero] + enemies
        self.current_turn_index = 0
        self.turn_count = 0
        self.hero_turn_count = 0
        self.effects = [[] for _ in range(len(self.participants))]
        self.battle_ended = False

    def start(self):
        print("=== НАЧАЛО БОЯ ===")
        print(f"Герой: {self.hero.name} против {len(self.enemies)} врагов")

        for i, enemy in enumerate(self.enemies, 1):
            print(f"{i}. {enemy.name} (HP: {enemy.hp}, Урон: {enemy.damage})")

        while not self.is_battle_over():
            self.next_turn()

    def is_battle_over(self):
        # если флаг выставлен, бой должен закончиться сразу
        if self.battle_ended:
            return True

        if not self.hero.alive or self.hero.hp <= 0:
            print("Герой побежден! Бой окончен.")
            return True

        if all(not enemy.alive or enemy.hp <= 0 for enemy in self.enemies):
            print("Все враги побеждены! Победа героя!")
            return True

        return False

    def next_turn(self):
        # Пропускаем мертвых участников
        while (self.current_turn_index < len(self.participants) and
               (not self.participants[self.current_turn_index].alive or
                self.participants[self.current_turn_index].hp <= 0)):
            self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
            if self.current_turn_index == 0:
                self.turn_count += 1

        if self.is_battle_over():
            return

        current_unit = self.participants[self.current_turn_index]

        # Проверяем, не умер ли участник от эффектов до начала хода
        if not current_unit.alive or current_unit.hp <= 0:
            self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
            if self.current_turn_index == 0:
                self.turn_count += 1
            return

        if self.current_turn_index == 0:
            mana_regen = self.hero.magic * self.hero.mana_amplification_bonus
            self.hero.mana = min(self.hero.max_mana, self.hero.mana + mana_regen)
            print(f"\n=== Ход героя ({self.hero.name}) ===")
            print(f"Восстановлено {mana_regen:.1f} маны. Текущая мана: {self.hero.mana:.1f}/{self.hero.max_mana}")
            self.hero_turn_count += 1
        else:
            mana_regen = current_unit.max_mana / 2
            current_unit.mana = min(current_unit.max_mana, current_unit.mana + mana_regen)
            print(f"\n=== Ход врага ({current_unit.name}) ===")
            print(f"{current_unit.name} восстановил {mana_regen:.1f} маны "
                  f"(текущая: {current_unit.mana:.1f}/{current_unit.max_mana})")

        self.update_effects(self.current_turn_index)

        # Проверяем, не умер ли участник после обновления эффектов
        if not current_unit.alive or current_unit.hp <= 0:
            print(f"{current_unit.name} умер от эффектов в начале хода!")
            self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
            if self.current_turn_index == 0:
                self.turn_count += 1
            return

        if self.effects[self.current_turn_index]:
            print("Активные эффекты:")
            for effect in self.effects[self.current_turn_index]:
                print(f"  - {effect}")

        if self.current_turn_index == 0:
            self.hero_turn()
        else:
            self.enemy_turn(current_unit)

        self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
        if self.current_turn_index == 0:
            self.turn_count += 1

    def update_effects(self, participant_index):
        participant = self.participants[participant_index]
        if not participant.alive or participant.hp <= 0:
            return

        effects_to_remove = []
        for effect in self.effects[participant_index]:
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
                print(f"Эффект '{effect.name}' закончился.")

        for effect in effects_to_remove:
            self.effects[participant_index].remove(effect)

    def hero_turn(self):
        turn_ended = False

        while not turn_ended and not self.is_battle_over():
            print(f"\n=== Ход героя ({self.hero.name}) ===")
            print(f"Здоровье: {self.hero.hp:.1f}/{self.hero.max_hp}")
            print(f"Мана: {self.hero.mana:.1f}/{self.hero.max_mana}")
            print("\nВыберите действие:")
            print("1 - Обычная атака")
            print("2 - Использовать заклинание")
            print("3 - Использовать предмет")
            print("4 - Закончить ход")

            try:
                choice = int(input("Ваш выбор: "))

                if choice == 1:
                    target = self.select_target()
                    if target:
                        self.hero_attack(target)
                        turn_ended = True

                elif choice == 2:
                    if not self.hero.spells:
                        print("У вас нет заклинаний!")
                        continue

                    print("\nВыберите заклинание:")
                    for i, spell in enumerate(self.hero.spells, 1):
                        print(f"{i} - {spell}")
                    print("0 - Назад")

                    spell_choice = int(input("Ваш выбор: "))

                    if spell_choice == 0:
                        continue
                    elif 1 <= spell_choice <= len(self.hero.spells):
                        spell = self.hero.spells[spell_choice - 1]

                        if self.hero.mana < spell.mana_cost:
                            print(f"Недостаточно маны! Нужно {spell.mana_cost}, есть {self.hero.mana:.1f}")
                            continue

                        self.use_spell(self.hero, spell)
                        self.hero.mana -= spell.mana_cost

                        if spell.end_turn:
                            turn_ended = True

                elif choice == 3:
                    if not self.hero.inventory:
                        print("Инвентарь пуст!")
                        continue

                    print("\nВыберите предмет:")
                    for i, item in enumerate(self.hero.inventory, 1):
                        print(f"{i} - {item}")
                    print("0 - Назад")

                    item_choice = int(input("Ваш выбор: "))

                    if item_choice == 0:
                        continue
                    elif 1 <= item_choice <= len(self.hero.inventory):
                        item = self.hero.inventory[item_choice - 1]

                        if item.item_type == ItemType.CONSUMABLE:
                            if item.hp_bonus > 0:
                                self.hero.hp = min(self.hero.get_effective_hp(), self.hero.hp + item.hp_bonus)
                                print(f"Использовано {item.name}. Восстановлено {item.hp_bonus} HP.")

                            self.hero.inventory.pop(item_choice - 1)
                        else:
                            print("Этот предмет нельзя использовать в бою!")

                elif choice == 4:
                    print("Ход завершен.")
                    turn_ended = True

                else:
                    print("Неверный выбор!")

            except ValueError:
                print("Пожалуйста, введите число!")

    def select_target(self):
        living_enemies = [i for i, enemy in enumerate(self.enemies, 1) if enemy.alive and enemy.hp > 0]

        if not living_enemies:
            return None

        print("\nВыберите цель:")
        for i in living_enemies:
            enemy = self.enemies[i - 1]
            print(f"{i} - {enemy.name} (HP: {enemy.hp}/{enemy.max_hp})")

        try:
            target_choice = int(input("Ваш выбор: "))
            if target_choice in living_enemies:
                return self.enemies[target_choice - 1]
            else:
                print("Неверный выбор цели!")
                return None
        except ValueError:
            print("Пожалуйста, введите число!")
            return None

    def hero_attack(self, target):
        if not target.alive or target.hp <= 0:
            print(f"{target.name} уже мертв!")
            return

        dodge_chance = target.evade if isinstance(target, Enemy) else target.get_effective_dodge_chance()
        if random.random() * 100 < dodge_chance:
            print(f"{target.name} увернулся от атаки!")
            return

        damage = self.calculate_damage_with_effects(0)
        defense = target.armor if isinstance(target, Enemy) else target.calculate_equipment_bonuses()['defense']
        actual_damage = max(1, damage - defense)

        target.hp -= actual_damage
        target.hp = max(target.hp, 0)  # чтобы не было отрицательного HP

        print(f"{self.hero.name} атакует {target.name} и наносит {actual_damage:.1f} урона! "
              f"Осталось HP: {target.hp:.1f}/{target.max_hp}")

        if target.hp <= 0:
            self.mark_target_dead(target)

    def calculate_damage_with_effects(self, participant_index):
        participant = self.participants[participant_index]
        if not participant.alive or participant.hp <= 0:
            return 0

        if isinstance(participant, Character):
            base_damage = participant.calculate_damage()
        else:
            base_damage = participant.damage

        atk_float_buff = 0
        atk_percent_buff = 0
        for effect in self.effects[participant_index]:
            atk_float_buff += effect.atk_float_buff
            atk_percent_buff += effect.atk_percent_buff
            atk_float_buff -= effect.atk_float_debuff
            atk_percent_buff -= effect.atk_percent_debuff

        damage = base_damage * (1 + atk_percent_buff) + atk_float_buff
        return max(1, damage)

    def use_spell(self, caster, spell):
        # единый вывод, чтобы не было дубля с enemy_turn
        print(f"{caster.name} использует {spell.name}!")

        # выбор цели
        if spell.aimed_to_self:
            target = caster
            target_index = self.participants.index(caster)
        else:
            if caster == self.hero:
                target = self.select_target()
                if not target:
                    return
            else:
                target = self.hero
            target_index = self.participants.index(target)

        # проверяем, жива ли цель
        if not target.alive or target.hp <= 0:
            print(f"{target.name} уже мертв!")
            return

        # урон заклинанием через ОБЩУЮ ФОРМУЛУ
        if spell.damage > 0:
            dodge_chance = target.get_effective_dodge_chance() if isinstance(target, Character) else target.evade
            if random.random() * 100 < dodge_chance:
                print(f"{target.name} увернулся от заклинания!")
                return

            caster_index = self.participants.index(caster)

            if isinstance(caster, Character):
                caster.spell_damage += spell.damage
                damage = self.calculate_damage_with_effects(caster_index)
                caster.spell_damage -= spell.damage
            else:
                caster.damage += spell.damage
                damage = self.calculate_damage_with_effects(caster_index)
                caster.damage -= spell.damage

            defense = target.calculate_equipment_bonuses()['defense'] if isinstance(target, Character) else target.armor
            actual_damage = max(1, damage - defense)

            target.hp -= actual_damage
            target.hp = max(target.hp, 0)

            print(f"Заклинание наносит {actual_damage:.1f} урона {target.name}! "
                  f"Осталось HP: {target.hp:.1f}/{target.max_hp}")

            if target.hp <= 0:
                self.mark_target_dead(target)

        # лечение
        if spell.heal > 0:
            max_hp = target.get_effective_hp() if isinstance(target, Character) else target.max_hp
            target.hp = min(max_hp, target.hp + spell.heal)
            print(f"{target.name} восстанавливает {spell.heal} HP.")

        # наложение эффектов
        effect_params = {}
        if spell.atk_float_buff != 0: effect_params['atk_float_buff'] = spell.atk_float_buff
        if spell.atk_percent_buff != 0: effect_params['atk_percent_buff'] = spell.atk_percent_buff
        if spell.atk_float_debuff != 0: effect_params['atk_float_debuff'] = spell.atk_float_debuff
        if spell.atk_percent_debuff != 0: effect_params['atk_percent_debuff'] = spell.atk_percent_debuff
        if spell.armor_buff != 0: effect_params['armor_buff'] = spell.armor_buff
        if spell.armor_debuff != 0: effect_params['armor_debuff'] = spell.armor_debuff
        if spell.evade_buff != 0: effect_params['evade_buff'] = spell.evade_buff
        if spell.evade_debuff != 0: effect_params['evade_debuff'] = spell.evade_debuff

        if effect_params and spell.duration > 0:
            existing = None
            for eff in self.effects[target_index]:
                if eff.name == spell.name:
                    existing = eff
                    break

            if existing:
                existing.duration += spell.duration
                print(f"Эффект '{existing.name}' продлён до {existing.duration} ходов!")
            else:
                effect = Effect(spell.name, spell.duration, **effect_params)
                self.effects[target_index].append(effect)
                print(f"На {target.name} наложен эффект: {effect}")

    def enemy_turn(self, enemy):
        enemy_index = self.participants.index(enemy)

        def select_target_for_spell(spell):
            if spell.aimed_to_self:
                return enemy
            else:
                if spell.is_buff:
                    # случайный союзник-враг, кроме себя
                    allies = [u for u in self.participants if not u.is_hero and u != enemy and u.alive and u.hp > 0]
                    return random.choice(allies) if allies else enemy
                else:
                    # атакующие заклинания всегда на героя
                    return self.hero if self.hero.alive and self.hero.hp > 0 else None

        # --- Создаем очередь заклинаний ---
        queue = []

        buffs_and_debuffs = [s for s in enemy.spells if s.aimed_to_self or s.is_buff]
        attacks = [s for s in enemy.spells if not s.is_buff and not s.aimed_to_self]
        ending_spells = [s for s in enemy.spells if s.end_turn]

        # Баффы на себя и дебаффы на героя
        queue.extend(buffs_and_debuffs)
        # Атаки на героя
        queue.extend(attacks)

        # Обрабатываем завершающие заклинания
        if ending_spells:
            spell_to_end = random.choice(ending_spells)
            if spell_to_end in queue:
                queue.remove(spell_to_end)
            queue.append(spell_to_end)

        # --- Очистка очереди чтобы маны хватило ---
        def clean_queue_by_mana(queue, enemy):
            while queue and sum(s.mana_cost for s in queue) > enemy.mana:
                # удаляем самое дешевое заклинание
                min_cost_spell = min(queue, key=lambda s: s.mana_cost)
                queue.remove(min_cost_spell)
            return queue

        queue = clean_queue_by_mana(queue, enemy)

        # Если очередь пуста после очистки, пробуем удалить дорогие заклинания
        if not queue:
            queue = buffs_and_debuffs + attacks
            queue = sorted(queue, key=lambda s: s.mana_cost, reverse=True)
            while queue and sum(s.mana_cost for s in queue) > enemy.mana:
                max_cost_spell = max(queue, key=lambda s: s.mana_cost)
                queue.remove(max_cost_spell)

        # --- Применяем заклинания ---
        if queue:
            for spell in queue:
                if enemy.mana >= spell.mana_cost and not self.is_battle_over():
                    target = select_target_for_spell(spell)
                    if target is None:
                        continue
                    enemy.mana -= spell.mana_cost
                    self.use_spell(enemy, spell)
                    if self.is_battle_over():
                        break
        else:
            # Если заклинаний нет или маны не хватает — обычная атака
            if not self.is_battle_over():
                self.enemy_attack(enemy)

    def enemy_attack(self, enemy):
        target = self.hero
        if not target.alive or target.hp <= 0:
            return

        dodge_chance = self.hero.get_effective_dodge_chance()
        if random.random() * 100 < dodge_chance:
            print(f"{self.hero.name} увернулся от атаки {enemy.name}!")
            return

        damage = self.calculate_damage_with_effects(self.participants.index(enemy))
        actual_damage = max(1, damage - self.hero.calculate_equipment_bonuses()['defense'])

        self.hero.hp -= actual_damage
        print(f"{enemy.name} атакует {self.hero.name} и наносит {actual_damage} урона!")

        if self.hero.hp <= 0:
            self.mark_target_dead(self.hero)

    def mark_target_dead(self, target):
        """Помечаем цель как мёртвую вместо удаления из списков"""
        if target.hp <= 0:
            target.alive = False
            target.hp = 0
            print(f"{target.name} побежден!")

            if isinstance(target, Character) and getattr(target, "is_hero", False):
                self.battle_ended = True
                print("Герой побежден! Бой окончен.")
                return True

            if all(not enemy.alive or enemy.hp <= 0 for enemy in self.enemies):
                self.battle_ended = True
                print("Все враги побеждены! Победа героя!")
                return True

        return False


def create_character():
    # Сначала загружаем героев из JSON
    Character.load_heroes_from_json('heroes.json')

    # Получаем список доступных классов
    available_classes = list(Character._loaded_heroes.keys())

    name = input("Назовитесь: ")

    print("\nВыберите класс:")
    for i, class_key in enumerate(available_classes, 1):
        class_data = Character._loaded_heroes[class_key]
        print(f"{i}) {class_data['name']} ({class_key})")

    try:
        choice = int(input("Ваш выбор: "))
        if 1 <= choice <= len(available_classes):
            selected_class = available_classes[choice - 1]

            character = Character(name, selected_class)
            print("\nПерсонаж создан успешно!")
            print(f"Имя: {character.name}")
            print(f"Класс: {Character._loaded_heroes[selected_class]['name']}")
            print(f"Здоровье: {character.hp}/{character.max_hp}")
            print(f"Мана: {character.mana}/{character.max_mana}")
            print(f"Сила: {character.strength}")
            print(f"Ловкость: {character.dexterity}")
            print(f"Магия: {character.magic}")

            character.show_equipment()
            character.show_inventory()
            character.show_spells()
            return character
        else:
            print("Неверный выбор класса!")
            return None

    except ValueError:
        print("Пожалуйста, введите число!")
        return None
    except Exception as e:
        print(f"Ошибка при создании персонажа: {e}")
        return None


if __name__ == '__main__':
    hero = create_character()

    print()
    enemies = Enemy.load_from_json('enemies.json')

    for enemy in enemies:
        print("\n" + "=" * 40 + "\n")
        print(enemy)

    print("\n" + "=" * 40 + "\n")

    battle = Battle(hero, enemies)
    battle.start()