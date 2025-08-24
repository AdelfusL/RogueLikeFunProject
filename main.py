import random
import math
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable, overload
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Константы для балансировки игры
DODGE_CONSTANT = 0.024
BASE_DODGE_MAX = 95
HEALTH_PER_STRENGTH = 10
MANA_PER_MAGIC = 10
MIN_DAMAGE = 1
DEFAULT_EFFECT_DURATION = 2


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


class MonsterClass(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


@dataclass
class Effect:
    name: str
    duration: int
    atk_float_buff: float = 0.0
    atk_percent_buff: float = 0.0
    atk_float_debuff: float = 0.0
    atk_percent_debuff: float = 0.0
    armor_buff: int = 0
    armor_debuff: int = 0
    evade_buff: float = 0.0
    evade_debuff: float = 0.0

    def __str__(self) -> str:
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


class Spell:
    def __init__(self, name: str, damage: int = 0, mana_cost: int = 0,
                 heal: int = 0, atk_float_buff: float = 0.0, atk_percent_buff: float = 0.0,
                 atk_float_debuff: float = 0.0, atk_percent_debuff: float = 0.0,
                 armor_buff: int = 0, armor_debuff: int = 0, evade_buff: float = 0.0,
                 evade_debuff: float = 0.0, duration: int = 0, end_turn: bool = True,
                 aimed_to_self: bool = True, is_buff: bool = False, aimed_to: int = 0):
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
        self.aimed_to = aimed_to

    def __str__(self) -> str:
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


class Item:
    def __init__(self, name: str, item_type: ItemType, slot_type: List[EquipmentSlot],
                 atk_bonus: int = 0, damage_scale: float = 0.0, defense: int = 0,
                 dodge_bonus: float = 0.0, hp_bonus: int = 0, mana_bonus: int = 0):
        self.name = name
        self.item_type = item_type
        self.slot_type = slot_type
        self.atk_bonus = atk_bonus
        self.damage_scale = damage_scale
        self.defense = defense
        self.dodge_bonus = dodge_bonus
        self.hp_bonus = hp_bonus
        self.mana_bonus = mana_bonus
        self.is_two_handed = (len(self.slot_type) == 2 and
                              EquipmentSlot.MAIN_HAND in self.slot_type and
                              EquipmentSlot.OFF_HAND in self.slot_type)

    def __str__(self) -> str:
        return f"{self.name} ({self.item_type.value})"


class InventoryManager:
    """Управление инвентарем персонажа"""

    def __init__(self):
        self.items: List[Item] = []

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def get_item(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def display(self) -> str:
        if not self.items:
            return "Инвентарь пуст"

        result = "--- ИНВЕНТАРЬ ---\n"
        for i, item in enumerate(self.items, 1):
            result += f"{i}. {item}\n"
        return result


class EquipmentManager:
    """Управление экипировкой персонажа"""

    def __init__(self):
        self.slots = {
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

    def equip(self, item: Item, slot: EquipmentSlot) -> Optional[Item]:
        if slot not in item.slot_type:
            return None

        old_item = self.slots[slot]
        self.slots[slot] = item

        # Для двуручного оружия занимаем оба слота
        if item.is_two_handed:
            other_slot = EquipmentSlot.OFF_HAND if slot == EquipmentSlot.MAIN_HAND else EquipmentSlot.MAIN_HAND
            self.slots[other_slot] = item

        return old_item

    def unequip(self, slot: EquipmentSlot) -> Optional[Item]:
        item = self.slots[slot]
        if item:
            self.slots[slot] = None

            # Для двуручного оружия освобождаем оба слота
            if item.is_two_handed:
                for s in [EquipmentSlot.MAIN_HAND, EquipmentSlot.OFF_HAND]:
                    if self.slots[s] == item:
                        self.slots[s] = None

        return item

    def get_equipment_bonuses(self) -> Dict[str, float]:
        weapon_atk_bonus = 0
        equipment_atk_bonus = 0
        weapon_damage_scale = 0
        equipment_damage_scale = 0
        dodge_bonus = 0
        defense = 0
        hp_bonus = 0
        mana_bonus = 0

        for item in self.slots.values():
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

    def display(self) -> str:
        result = "--- ЭКИПИРОВКА ---\n"
        for slot, item in self.slots.items():
            item_name = item.name if item else "Пусто"
            result += f"{slot.value}: {item_name}\n"
        return result


class SpellBook:
    """Управление заклинаниями персонажа"""

    def __init__(self):
        self.spells: List[Spell] = []

    def add_spell(self, spell: Spell) -> None:
        self.spells.append(spell)

    def get_spell(self, index: int) -> Optional[Spell]:
        if 0 <= index < len(self.spells):
            return self.spells[index]
        return None

    def display(self) -> str:
        if not self.spells:
            return "Заклинаний нет"

        result = "--- ЗАКЛИНАНИЯ ---\n"
        for i, spell in enumerate(self.spells, 1):
            result += f"{i}. {spell}\n"
        return result


class BattleUnit(ABC):
    """Абстрактный базовый класс для всех боевых единиц"""

    def __init__(self, name: str, hp: int, mana: int, damage: int,
                 evade: float, armor: int, is_hero: bool = False):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_mana = mana
        self.mana = mana
        self.damage = damage
        self.evade = evade
        self.armor = armor
        self.is_hero = is_hero
        self.alive = True
        self.effects: List[Effect] = []

    @abstractmethod
    def __str__(self) -> str:
        pass

    def take_damage(self, damage: float) -> None:
        """Нанесение урона юниту"""
        actual_damage = max(MIN_DAMAGE, damage - self.armor)
        self.hp -= actual_damage
        self.hp = max(self.hp, 0)

        if self.hp <= 0:
            self.alive = False

    def heal(self, amount: int) -> None:
        """Лечение юнита"""
        self.hp = min(self.max_hp, self.hp + amount)

    def add_effect(self, effect: Effect) -> None:
        """Добавление эффекта к юниту"""
        self.effects.append(effect)

    def remove_effect(self, effect: Effect) -> None:
        """Удаление эффекта у юнита"""
        if effect in self.effects:
            self.effects.remove(effect)

    def update_effects(self) -> None:
        """Обновление длительности эффектов"""
        effects_to_remove = []

        for effect in self.effects:
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
                logger.info(f"Эффект '{effect.name}' закончился у {self.name}")

        for effect in effects_to_remove:
            self.remove_effect(effect)

    def calculate_effective_stats(self) -> Dict[str, float]:
        """Расчет эффективных характеристик с учетом эффектов"""
        atk_float_buff = 0.0
        atk_percent_buff = 0.0
        armor_buff = 0
        evade_buff = 0.0

        for effect in self.effects:
            atk_float_buff += effect.atk_float_buff
            atk_percent_buff += effect.atk_percent_buff
            armor_buff += effect.armor_buff
            evade_buff += effect.evade_buff

        return {
            'damage': self.damage * (1 + atk_percent_buff) + atk_float_buff,
            'armor': self.armor + armor_buff,
            'evade': min(BASE_DODGE_MAX, self.evade + evade_buff)
        }


class Character(BattleUnit):
    _heroes_data: Dict[str, Any] = {}
    _loaded_heroes: Dict[str, Any] = {}

    def __init__(self, name: str, char_class: str):
        # Загружаем героев, если еще не загружены
        if not self._heroes_data:
            self.load_heroes_from_json('heroes.json')

        # Проверяем, что класс существует в загруженных данных
        if char_class not in self._heroes_data:
            raise ValueError(f"Недопустимый класс персонажа: {char_class}")

        # Получаем данные героя
        hero_data = self._heroes_data[char_class]
        bonuses = hero_data['bonuses']

        # Рассчитываем базовые характеристики
        strength = bonuses['str']
        dexterity = bonuses['dex']
        magic = bonuses['mag']

        max_hp = strength * HEALTH_PER_STRENGTH + bonuses.get('hp_bonus', 0)
        max_mana = magic * MANA_PER_MAGIC
        base_damage = 0  # Базовый урон будет рассчитываться через calculate_damage()
        base_evade = self.calculate_base_dodge_chance(dexterity)
        base_armor = 0

        # Инициализируем базовый класс
        super().__init__(name, max_hp, max_mana, base_damage, base_evade, base_armor, True)

        self.char_class = char_class
        self.strength = strength
        self.dexterity = dexterity
        self.magic = magic
        self.main_attr = bonuses['main_attr']
        self.dodge_multiplier = bonuses.get('dodge_multiplier', 1.0)
        self.mana_amplification_bonus = bonuses.get('mana_amplification_bonus', 1.0)

        # Менеджеры
        self.inventory = InventoryManager()
        self.equipment = EquipmentManager()
        self.spellbook = SpellBook()

        # Дополнительные атрибуты для модификаторов
        self.spell_damage = 0
        self.atk_scale = 1.0
        self.debuff_atk_scale = 1.0
        self.float_buffs = 0

        # Инициализация стартовых предметов и заклинаний
        self._initialize_starting_items(hero_data.get('starting_items', []))
        self._initialize_starting_spells(hero_data.get('starting_spells', []))
        self._equip_starting_weapon(hero_data.get('starting_items', []))

    @classmethod
    def load_heroes_from_json(cls, file_path: str, specific_classes: List[str] = None) -> None:
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
                    logger.warning("Предупреждение: не загружено ни одного класса героев!")

        except FileNotFoundError:
            logger.error(f"Файл {file_path} не найден.")
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке героев: {e}")
            raise

    def __str__(self) -> str:
        class_name = self._heroes_data.get(self.char_class, {}).get('name', self.char_class)
        status = "живой" if self.alive else "мертвый"
        effective_hp = self.get_effective_hp()

        return (f"Персонаж: {self.name} ({status})\n"
                f"Класс: {class_name}\n"
                f"Здоровье: {self.hp:.1f}/{effective_hp:.1f}\n"
                f"Мана: {self.mana:.1f}/{self.get_effective_mana():.1f}\n"
                f"Сила: {self.strength}\n"
                f"Ловкость: {self.dexterity}\n"
                f"Магия: {self.magic}\n"
                f"Урон: {self.calculate_damage():.1f}\n"
                f"Уклонение: {self.get_effective_dodge_chance():.1f}%")

    def _initialize_starting_items(self, starting_items_data: List[Dict]) -> None:
        """Инициализация стартовых предметов"""
        # Добавляем зелья лечения
        health_potion = Item("Зелье лечения", ItemType.CONSUMABLE, [], hp_bonus=100)
        for _ in range(3):
            self.inventory.add_item(health_potion)

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
            self.inventory.add_item(item)

    def _initialize_starting_spells(self, starting_spells_data: List[Dict]) -> None:
        """Инициализация стартовых заклинаний"""
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
                evade_buff=spell_data.get('evade_buff', 0.0),
                evade_debuff=spell_data.get('evade_debuff', 0.0),
                duration=spell_data.get('duration', 0),
                end_turn=spell_data.get('end_turn', True),
                aimed_to_self=spell_data.get('aimed_to_self', True),
                is_buff=spell_data.get('is_buff', False),
                aimed_to=spell_data.get('aimed_to', 0)
            )
            self.spellbook.add_spell(spell)

    def _equip_starting_weapon(self, starting_items_data: List[Dict]) -> None:
        """Экипировка стартового оружия"""
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

                # Экипируем в первый доступный слот
                for slot in item.slot_type:
                    if self.equipment.slots[slot] is None:
                        self.equipment.equip(item, slot)
                        break

    def calculate_base_dodge_chance(self, dexterity: int) -> float:
        """Расчет базового шанса уклонения"""
        return BASE_DODGE_MAX * (1 - math.exp(-DODGE_CONSTANT * dexterity))

    def calculate_damage(self) -> float:
        """Расчет урона с учетом всех модификаторов"""
        bonuses = self.equipment.get_equipment_bonuses()

        if self.main_attr == 'str':
            main_attr_value = self.strength
        elif self.main_attr == 'dex':
            main_attr_value = self.dexterity
        else:
            main_attr_value = self.magic

        # Учитываем эффекты
        effective_stats = self.calculate_effective_stats()
        base_damage = effective_stats['damage']

        damage = ((main_attr_value + self.spell_damage +
                   bonuses['weapon_atk_bonus'] + bonuses['equipment_atk_bonus']) *
                  self.atk_scale * self.debuff_atk_scale *
                  (1 + bonuses['weapon_damage_scale'] + bonuses['equipment_damage_scale'])) + self.float_buffs

        return max(MIN_DAMAGE, damage)

    def get_effective_dodge_chance(self) -> float:
        """Получение эффективного шанса уклонения"""
        bonuses = self.equipment.get_equipment_bonuses()
        base_dodge = self.calculate_base_dodge_chance(self.dexterity)

        # Учитываем эффекты
        effective_stats = self.calculate_effective_stats()
        base_dodge = effective_stats['evade']

        total_dodge = (base_dodge + bonuses['dodge_bonus']) * self.dodge_multiplier
        return min(BASE_DODGE_MAX, total_dodge)

    def get_effective_hp(self) -> float:
        """Получение эффективного здоровья"""
        bonuses = self.equipment.get_equipment_bonuses()
        return self.max_hp + bonuses['hp_bonus']

    def get_effective_mana(self) -> float:
        """Получение эффективной маны"""
        bonuses = self.equipment.get_equipment_bonuses()
        return self.max_mana + bonuses['mana_bonus']

    def use_item(self, item_index: int) -> bool:
        """Использование предмета из инвентаря"""
        item = self.inventory.get_item(item_index)
        if not item:
            logger.error("Неверный индекс предмета")
            return False

        if item.item_type != ItemType.CONSUMABLE:
            logger.error("Этот предмет нельзя использовать")
            return False

        if item.hp_bonus > 0:
            self.heal(item.hp_bonus)
            logger.info(f"Использовано зелье лечения. Восстановлено {item.hp_bonus} HP.")

        self.inventory.remove_item(item_index)
        return True


class Enemy(BattleUnit):
    def __init__(self, name: str, hp: int, damage: int, mana: int, evade: float,
                 monster_class: MonsterClass, spells: List[Spell], armor: int = 0):
        super().__init__(name, hp, mana, damage, evade, armor, False)
        self.monster_class = monster_class
        self.spells = spells

    def __str__(self) -> str:
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
        """Загрузка врагов из JSON файла"""
        enemies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                for enemy_data in data.get('enemies', []):
                    monster_class = MonsterClass[enemy_data['monster_class']]
                    default_duration = DEFAULT_EFFECT_DURATION if monster_class == MonsterClass.F else 1

                    spells = []
                    for spell_data in enemy_data.get('spells', []):
                        # Определяем длительность эффекта
                        has_effect = any([
                            spell_data.get('atk_float_buff', 0) != 0,
                            spell_data.get('atk_percent_buff', 0) != 0,
                            spell_data.get('atk_float_debuff', 0) != 0,
                            spell_data.get('atk_percent_debuff', 0) != 0,
                            spell_data.get('armor_buff', 0) != 0,
                            spell_data.get('armor_debuff', 0) != 0,
                            spell_data.get('evade_buff', 0) != 0,
                            spell_data.get('evade_debuff', 0) != 0
                        ])

                        duration = spell_data.get('duration', default_duration if has_effect else 0)

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
                            evade_buff=spell_data.get('evade_buff', 0.0),
                            evade_debuff=spell_data.get('evade_debuff', 0.0),
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
            logger.error(f"Файл {file_path} не найден.")
        except KeyError as e:
            logger.error(f"Ошибка в структуре JSON: отсутствует ключ {e}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке врагов: {e}")

        return enemies


class BattleState(ABC):
    """Абстрактный класс состояния битвы"""

    def __init__(self, battle: 'Battle'):
        self.battle = battle

    @abstractmethod
    def execute(self) -> None:
        pass


class HeroTurnState(BattleState):
    """Состояние хода героя"""

    def execute(self) -> None:
        print(f"\n=== Ход героя ({self.battle.hero.name}) ===")
        print(f"Здоровье: {self.battle.hero.hp:.1f}/{self.battle.hero.get_effective_hp()}")
        print(f"Мана: {self.battle.hero.mana:.1f}/{self.battle.hero.get_effective_mana()}")

        turn_ended = False
        while not turn_ended and not self.battle.is_battle_over():
            choice = self._get_action_choice()

            if choice == 1:
                self._handle_attack()
                turn_ended = True
            elif choice == 2:
                turn_ended = self._handle_spell()
            elif choice == 3:
                self._handle_item()
            elif choice == 4:
                print("Ход завершен.")
                turn_ended = True

    def _get_action_choice(self) -> int:
        """Получение выбора действия от игрока"""
        print("\nВыберите действие:")
        print("1 - Обычная атака")
        print("2 - Использовать заклинание")
        print("3 - Использовать предмет")
        print("4 - Закончить ход")

        while True:
            try:
                choice = int(input("Ваш выбор: "))
                if 1 <= choice <= 4:
                    return choice
                print("Неверный выбор! Введите число от 1 до 4.")
            except ValueError:
                print("Пожалуйста, введите число!")

    def _handle_attack(self) -> None:
        """Обработка обычной атаки"""
        target = self._select_target()
        if target:
            self.battle.hero_attack(target)

    def _handle_spell(self) -> bool:
        """Обработка использования заклинания"""
        if not self.battle.hero.spellbook.spells:
            print("У вас нет заклинаний!")
            return False

        print("\nВыберите заклинание:")
        for i, spell in enumerate(self.battle.hero.spellbook.spells, 1):
            print(f"{i} - {spell}")
        print("0 - Назад")

        try:
            spell_choice = int(input("Ваш выбор: "))
            if spell_choice == 0:
                return False
            elif 1 <= spell_choice <= len(self.battle.hero.spellbook.spells):
                spell = self.battle.hero.spellbook.spells[spell_choice - 1]

                if self.battle.hero.mana < spell.mana_cost:
                    print(f"Недостаточно маны! Нужно {spell.mana_cost}, есть {self.battle.hero.mana:.1f}")
                    return False

                self.battle.use_spell(self.battle.hero, spell)
                self.battle.hero.mana -= spell.mana_cost

                return spell.end_turn
            else:
                print("Неверный выбор!")
                return False
        except ValueError:
            print("Пожалуйста, введите число!")
            return False

    def _handle_item(self) -> None:
        """Обработка использования предмета"""
        if not self.battle.hero.inventory.items:
            print("Инвентарь пуст!")
            return

        print("\nВыберите предмет:")
        for i, item in enumerate(self.battle.hero.inventory.items, 1):
            print(f"{i} - {item}")
        print("0 - Назад")

        try:
            item_choice = int(input("Ваш выбор: "))
            if item_choice == 0:
                return
            elif 1 <= item_choice <= len(self.battle.hero.inventory.items):
                self.battle.hero.use_item(item_choice - 1)
            else:
                print("Неверный выбор!")
        except ValueError:
            print("Пожалуйста, введите число!")

    def _select_target(self) -> Optional[Enemy]:
        """Выбор цели для атаки или заклинания"""
        living_enemies = [i for i, enemy in enumerate(self.battle.enemies, 1)
                          if enemy.alive and enemy.hp > 0]

        if not living_enemies:
            return None

        print("\nВыберите цель:")
        for i in living_enemies:
            enemy = self.battle.enemies[i - 1]
            print(f"{i} - {enemy.name} (HP: {enemy.hp}/{enemy.max_hp})")

        try:
            target_choice = int(input("Ваш выбор: "))
            if target_choice in living_enemies:
                return self.battle.enemies[target_choice - 1]
            else:
                print("Неверный выбор цели!")
                return None
        except ValueError:
            print("Пожалуйста, введите число!")
            return None


class EnemyTurnState(BattleState):
    """Состояние хода врага"""

    def execute(self) -> None:
        enemy = self.battle.get_current_enemy()
        if not enemy:
            return

        print(f"\n=== Ход врага ({enemy.name}) ===")

        # Восстановление маны
        mana_regen = enemy.max_mana / 2
        enemy.mana = min(enemy.max_mana, enemy.mana + mana_regen)
        print(f"{enemy.name} восстановил {mana_regen:.1f} маны "
              f"(текущая: {enemy.mana:.1f}/{enemy.max_mana})")

        # Обновление эффектов
        self.battle.update_effects(self.battle.participants.index(enemy))

        # Проверка, не умер ли враг от эффектов
        if not enemy.alive or enemy.hp <= 0:
            print(f"{enemy.name} умер от эффектов в начале хода!")
            return

        # Выбор действия
        if enemy.spells and enemy.mana > 0:
            self._use_spells(enemy)
        else:
            self.battle.enemy_attack(enemy)

    def _use_spells(self, enemy: Enemy) -> None:
        """Использование заклинаний врагом"""
        # Создаем очередь заклинаний
        queue = []

        buffs_and_debuffs = [s for s in enemy.spells if s.aimed_to_self or s.is_buff]
        attacks = [s for s in enemy.spells if not s.is_buff and not s.aimed_to_self]
        ending_spells = [s for s in enemy.spells if s.end_turn]

        # Добавляем в очередь баффы и дебаффы, затем атаки
        queue.extend(buffs_and_debuffs)
        queue.extend(attacks)

        # Обрабатываем завершающие заклинания
        if ending_spells:
            spell_to_end = random.choice(ending_spells)
            if spell_to_end in queue:
                queue.remove(spell_to_end)
            queue.append(spell_to_end)

        # Очищаем очередь, чтобы маны хватило
        queue = self._clean_queue_by_mana(queue, enemy)

        # Применяем заклинания
        if queue:
            for spell in queue:
                if enemy.mana >= spell.mana_cost and not self.battle.is_battle_over():
                    target = self._select_target_for_spell(enemy, spell)
                    if target is None:
                        continue

                    enemy.mana -= spell.mana_cost
                    self.battle.use_spell(enemy, spell)

                    if self.battle.is_battle_over():
                        break
        else:
            # Если заклинаний нет или маны не хватает — обычная атака
            self.battle.enemy_attack(enemy)

    def _clean_queue_by_mana(self, queue: List[Spell], enemy: Enemy) -> List[Spell]:
        """Очистка очереди заклинаний по мане"""
        while queue and sum(s.mana_cost for s in queue) > enemy.mana:
            # Удаляем самое дешевое заклинание
            min_cost_spell = min(queue, key=lambda s: s.mana_cost)
            queue.remove(min_cost_spell)

        # Если очередь пуста после очистки, пробуем удалить дорогие заклинания
        if not queue:
            all_spells = enemy.spells.copy()
            all_spells.sort(key=lambda s: s.mana_cost, reverse=True)

            while all_spells and sum(s.mana_cost for s in all_spells) > enemy.mana:
                max_cost_spell = max(all_spells, key=lambda s: s.mana_cost)
                all_spells.remove(max_cost_spell)

            queue = all_spells

        return queue

    def _select_target_for_spell(self, enemy: Enemy, spell: Spell) -> Optional[BattleUnit]:
        """Выбор цели для заклинания врага"""
        if spell.aimed_to_self:
            return enemy
        else:
            if spell.is_buff:
                # Случайный союзник-враг, кроме себя
                allies = [u for u in self.battle.participants
                          if not u.is_hero and u != enemy and u.alive and u.hp > 0]
                return random.choice(allies) if allies else enemy
            else:
                # Атакующие заклинания всегда на героя
                return self.battle.hero if self.battle.hero.alive and self.battle.hero.hp > 0 else None


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

        # Состояния битвы
        self.states = {
            'hero_turn': HeroTurnState(self),
            'enemy_turn': EnemyTurnState(self)
        }
        self.current_state = None

    def start(self) -> None:
        """Начало битвы"""
        print("=== НАЧАЛО БОЯ ===")
        print(f"Герой: {self.hero.name} против {len(self.enemies)} врагов")

        for i, enemy in enumerate(self.enemies, 1):
            print(f"{i}. {enemy.name} (HP: {enemy.hp}, Урон: {enemy.damage})")

        while not self.is_battle_over():
            self.next_turn()

    def is_battle_over(self) -> bool:
        """Проверка окончания битвы"""
        if self.battle_ended:
            return True

        if not self.hero.alive or self.hero.hp <= 0:
            print("Герой побежден! Бой окончен.")
            return True

        if all(not enemy.alive or enemy.hp <= 0 for enemy in self.enemies):
            print("Все враги побеждены! Победа героя!")
            return True

        return False

    def next_turn(self) -> None:
        """Переход к следующему ходу"""
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

        # Восстановление маны в начале хода
        if self.current_turn_index == 0:
            mana_regen = self.hero.magic * self.hero.mana_amplification_bonus
            self.hero.mana = min(self.hero.get_effective_mana(), self.hero.mana + mana_regen)
            print(
                f"Восстановлено {mana_regen:.1f} маны. Текущая мана: {self.hero.mana:.1f}/{self.hero.get_effective_mana()}")
            self.hero_turn_count += 1
            self.current_state = self.states['hero_turn']
        else:
            mana_regen = current_unit.max_mana / 2
            current_unit.mana = min(current_unit.max_mana, current_unit.mana + mana_regen)
            print(f"{current_unit.name} восстановил {mana_regen:.1f} маны "
                  f"(текущая: {current_unit.mana:.1f}/{current_unit.max_mana})")
            self.current_state = self.states['enemy_turn']

        # Выполняем текущее состояние
        self.current_state.execute()

        # Переход к следующему участнику
        self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
        if self.current_turn_index == 0:
            self.turn_count += 1

    def get_current_enemy(self) -> Optional[Enemy]:
        """Получение текущего врага, который ходит"""
        if self.current_turn_index == 0:
            return None
        return self.enemies[self.current_turn_index - 1]

    def update_effects(self, participant_index: int) -> None:
        """Обновление эффектов участника"""
        participant = self.participants[participant_index]
        if not participant.alive or participant.hp <= 0:
            return

        effects_to_remove = []
        for effect in self.effects[participant_index]:
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
                print(f"Эффект '{effect.name}' закончился у {participant.name}.")

        for effect in effects_to_remove:
            self.effects[participant_index].remove(effect)

    def hero_attack(self, target: Enemy) -> None:
        """Атака героя по цели"""
        if not target.alive or target.hp <= 0:
            print(f"{target.name} уже мертв!")
            return

        dodge_chance = target.evade
        if random.random() * 100 < dodge_chance:
            print(f"{target.name} увернулся от атаки!")
            return

        damage = self.calculate_damage_with_effects(0)
        actual_damage = max(MIN_DAMAGE, damage - target.armor)

        target.take_damage(actual_damage)
        print(f"{self.hero.name} атакует {target.name} и наносит {actual_damage:.1f} урона! "
              f"Осталось HP: {target.hp:.1f}/{target.max_hp}")

        if target.hp <= 0:
            self.mark_target_dead(target)

    def enemy_attack(self, enemy: Enemy) -> None:
        """Атака врага по герою"""
        target = self.hero
        if not target.alive or target.hp <= 0:
            return

        dodge_chance = self.hero.get_effective_dodge_chance()
        if random.random() * 100 < dodge_chance:
            print(f"{self.hero.name} увернулся от атаки {enemy.name}!")
            return

        damage = self.calculate_damage_with_effects(self.participants.index(enemy))
        actual_damage = max(MIN_DAMAGE, damage - self.hero.calculate_effective_stats()['armor'])

        self.hero.take_damage(actual_damage)
        print(f"{enemy.name} атакует {self.hero.name} и наносит {actual_damage} урона!")

        if self.hero.hp <= 0:
            self.mark_target_dead(self.hero)

    def calculate_damage_with_effects(self, participant_index: int) -> float:
        """Расчет урона с учетом эффектов"""
        participant = self.participants[participant_index]
        if not participant.alive or participant.hp <= 0:
            return 0

        if isinstance(participant, Character):
            base_damage = participant.calculate_damage()
        else:
            base_damage = participant.damage

        atk_float_buff = 0.0
        atk_percent_buff = 0.0
        for effect in self.effects[participant_index]:
            atk_float_buff += effect.atk_float_buff
            atk_percent_buff += effect.atk_percent_buff
            atk_float_buff -= effect.atk_float_debuff
            atk_percent_buff -= effect.atk_percent_debuff

        damage = base_damage * (1 + atk_percent_buff) + atk_float_buff
        return max(MIN_DAMAGE, damage)

    def use_spell(self, caster: BattleUnit, spell: Spell) -> None:
        """Использование заклинания"""
        print(f"{caster.name} использует {spell.name}!")

        # Выбор цели
        if spell.aimed_to_self:
            target = caster
            target_index = self.participants.index(caster)
        else:
            if caster == self.hero:
                # Для героя выбираем цель через интерфейс
                target = self._select_target_for_hero_spell()
                if not target:
                    return
            else:
                # Для врага цель - герой
                target = self.hero
            target_index = self.participants.index(target)

        # Проверяем, жива ли цель
        if not target.alive or target.hp <= 0:
            print(f"{target.name} уже мертв!")
            return

        # Нанесение урона
        if spell.damage > 0:
            dodge_chance = target.evade if isinstance(target, Enemy) else target.get_effective_dodge_chance()
            if random.random() * 100 < dodge_chance:
                print(f"{target.name} увернулся от заклинания!")
                return

            caster_index = self.participants.index(caster)

            # Временное увеличение урона для расчета
            if isinstance(caster, Character):
                caster.spell_damage += spell.damage
                damage = self.calculate_damage_with_effects(caster_index)
                caster.spell_damage -= spell.damage
            else:
                caster.damage += spell.damage
                damage = self.calculate_damage_with_effects(caster_index)
                caster.damage -= spell.damage

            # Расчет защиты
            defense = target.armor if isinstance(target, Enemy) else target.calculate_effective_stats()['armor']
            actual_damage = max(MIN_DAMAGE, damage - defense)

            target.take_damage(actual_damage)
            print(f"Заклинание наносит {actual_damage:.1f} урона {target.name}! "
                  f"Осталось HP: {target.hp:.1f}/{target.max_hp}")

            if target.hp <= 0:
                self.mark_target_dead(target)

        # Лечение
        if spell.heal > 0:
            max_hp = target.max_hp if isinstance(target, Enemy) else target.get_effective_hp()
            target.heal(spell.heal)
            print(f"{target.name} восстанавливает {spell.heal} HP.")

        # Наложение эффектов
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

    def _select_target_for_hero_spell(self) -> Optional[Enemy]:
        """Выбор цели для заклинания героя"""
        living_enemies = [i for i, enemy in enumerate(self.enemies, 1)
                          if enemy.alive and enemy.hp > 0]

        if not living_enemies:
            return None

        print("\nВыберите цель для заклинания:")
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

    def mark_target_dead(self, target: BattleUnit) -> bool:
        """Помечаем цель как мёртвую"""
        if target.hp <= 0:
            target.alive = False
            target.hp = 0
            print(f"{target.name} побежден!")

            if isinstance(target, Character) and target.is_hero:
                self.battle_ended = True
                print("Герой побежден! Бой окончен.")
                return True

            if all(not enemy.alive or enemy.hp <= 0 for enemy in self.enemies):
                self.battle_ended = True
                print("Все враги побеждены! Победа героя!")
                return True

        return False


def safe_input_int(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Безопасный ввод целого числа с валидацией"""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Значение должно быть не меньше {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Значение должно быть не больше {max_val}")
                continue
            return value
        except ValueError:
            print("Пожалуйста, введите целое число!")


def create_character() -> Optional[Character]:
    """Создание персонажа"""
    # Сначала загружаем героев из JSON
    Character.load_heroes_from_json('heroes.json')

    # Получаем список доступных классов
    available_classes = list(Character._loaded_heroes.keys())

    name = input("Введите имя персонажа: ")

    print("\nВыберите класс:")
    for i, class_key in enumerate(available_classes, 1):
        class_data = Character._loaded_heroes[class_key]
        print(f"{i}) {class_data['name']} ({class_key})")

    try:
        choice = safe_input_int("Ваш выбор: ", 1, len(available_classes))
        selected_class = available_classes[choice - 1]

        character = Character(name, selected_class)
        print("\nПерсонаж создан успешно!")
        print(f"Имя: {character.name}")
        print(f"Класс: {Character._loaded_heroes[selected_class]['name']}")
        print(f"Здоровье: {character.hp}/{character.get_effective_hp()}")
        print(f"Мана: {character.mana}/{character.get_effective_mana()}")
        print(f"Сила: {character.strength}")
        print(f"Ловкость: {character.dexterity}")
        print(f"Магия: {character.magic}")

        print(character.equipment.display())
        print(character.inventory.display())
        print(character.spellbook.display())

        return character
    except Exception as e:
        logger.error(f"Ошибка при создании персонажа: {e}")
        return None


def main() -> None:
    """Основная функция игры"""
    hero = create_character()
    if not hero:
        return

    print("\n" + "=" * 40 + "\n")

    # Загрузка врагов
    enemies = Enemy.load_from_json('enemies.json')

    for enemy in enemies:
        print("\n" + "=" * 40 + "\n")
        print(enemy)

    print("\n" + "=" * 40 + "\n")

    # Начало битвы
    battle = Battle(hero, enemies)
    battle.start()


if __name__ == '__main__':
    main()