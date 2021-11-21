from eldritch.assets import Card
from eldritch import events
from eldritch import places
from eldritch import values


class Item(Card):

  ITEM_TYPES = {"weapon", "tome", None}

  def __init__(self, name, deck, active_bonuses, passive_bonuses, hands, price, item_type=None):
    assert item_type in self.ITEM_TYPES
    super().__init__(name, deck, active_bonuses, passive_bonuses)
    self.hands = hands
    self.price = price
    self.item_type = item_type

  def hands_used(self):
    return self.hands if self.active else 0


class Weapon(Item):

  def __init__(self, name, deck, active_bonuses, passive_bonuses, hands, price):
    super().__init__(name, deck, active_bonuses, passive_bonuses, hands, price, "weapon")


class OneshotWeapon(Weapon):

  def get_trigger(self, event, owner, state):
    if not isinstance(event, events.Check) or event.check_type != "combat":
      return None
    if event.character != owner or not self.active:
      return None
    return events.DiscardSpecific(event.character, self)


class Food(Item):

  def __init__(self):
    super().__init__("Food", "common", {}, {}, None, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.GainOrLoss) or owner != event.character:
      return None
    if isinstance(event.losses.get("stamina"), values.Value):
      if event.losses["stamina"].value(state) < 1:
        return None
    elif event.losses.get("stamina", 0) < 1:
      return None

    discard = events.DiscardSpecific(event.character, self)
    prevent = events.LossPrevention(self, event, "stamina", 1)
    return events.Sequence([discard, prevent], owner)


class Whiskey(Item):

  def __init__(self):
    super().__init__("Whiskey", "common", {}, {}, None, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.GainOrLoss) or owner != event.character:
      return None
    if isinstance(event.losses.get("sanity"), values.Value):
      if event.losses["sanity"].value(state) < 1:
        return None
    elif event.losses.get("sanity", 0) < 1:
      return None

    discard = events.DiscardSpecific(event.character, self)
    prevent = events.LossPrevention(self, event, "sanity", 1)
    return events.Sequence([discard, prevent], owner)


class ResearchMaterials(Item):

  def __init__(self):
    super().__init__("Research Materials", "common", {}, {}, None, 1)

  def get_usable_trigger(self, event, owner, state):
    return None  # TODO


class Bullwhip(Weapon):

  def __init__(self):
    super().__init__("Bullwhip", "common", {"physical": 1}, {}, 1, 2)

  def get_usable_trigger(self, event, owner, state):
    if not isinstance(event, events.Check) or owner != event.character:
      return None
    if event.check_type != "combat":
      return None
    return None  # TODO: create an event here


class Cross(Weapon):

  def __init__(self):
    super().__init__("Cross", "common", {}, {"horror": 1}, 1, 3)

  def get_bonus(self, check_type, attributes):
    bonus = super().get_bonus(check_type, attributes)
    if self.active and check_type == "magical" and attributes and "undead" in attributes:
      bonus += 3
    return bonus


def DarkCloak():
  return Item("Dark Cloak", "common", {}, {"evade": 1}, None, 2)


def Revolver38():
  return Weapon(".38 Revolver", "common", {"physical": 3}, {}, 1, 4)


def Automatic45():
  return Weapon(".45 Automatic", "common", {"physical": 4}, {}, 1, 5)


def Dynamite():
  return OneshotWeapon("Dynamite", "common", {"physical": 8}, {}, 2, 4)


def HolyWater():
  return OneshotWeapon("Holy Water", "unique", {"magical": 6}, {}, 2, 4)


def EnchantedKnife():
  return Weapon("Enchanted Knife", "unique", {"magical": 3}, {}, 1, 5)


def MagicLamp():
  return Weapon("Magic Lamp", "unique", {"magical": 5}, {}, 2, 7)


def TommyGun():
  return Weapon("Tommy Gun", "common", {"physical": 6}, {}, 2, 7)


class Spell(Item):

  def __init__(self, name, active_bonuses, hands, difficulty, sanity_cost):
    super().__init__(name, "spells", active_bonuses, {}, hands, None)
    self.difficulty = difficulty
    self.sanity_cost = sanity_cost
    self.in_use = False
    self.deactivatable = False
    self.choice = None

  def get_difficulty(self, state):  # pylint: disable=unused-argument
    return self.difficulty

  def get_required_successes(self, state):  # pylint: disable=unused-argument
    return 1

  def hands_used(self):
    return self.hands if self.in_use else 0

  def get_cast_event(self, owner, state):  # pylint: disable=unused-argument
    return events.Nothing()


class CombatSpell(Spell):

  def is_combat(self, event, owner):
    if getattr(event, "character", None) != owner:
      return False
    if isinstance(event, events.CombatChoice) and not event.is_resolved():
      return True
    # May cast even before making the decision to fight or evade. TODO: this is hacky/fragile.
    if isinstance(event, events.MultipleChoice) and hasattr(event, "monster"):
      if not event.is_resolved():
        return True
    return False

  def get_usable_interrupt(self, event, owner, state):
    if not self.is_combat(event, owner):
      return None
    if self.in_use:
      if self.deactivatable:
        return events.DeactivateSpell(owner, self)
      return None
    if self.exhausted or owner.sanity < self.sanity_cost:
      return None
    if owner.hands_available() < self.hands:
      return None
    return events.CastSpell(owner, self)

  def get_trigger(self, event, owner, state):
    if not self.in_use:
      return None
    if isinstance(event, (events.CombatRound, events.EvadeRound)) and event.character == owner:
      return events.MarkDeactivatable(owner, self)
    return None

  def get_cast_event(self, owner, state):
    return events.ActivateItem(owner, self)

  def activate(self):
    pass

  def deactivate(self):
    pass


def Wither():
  return CombatSpell("Wither", {"magical": 3}, 1, 0, 0)


def Shrivelling():
  return CombatSpell("Shrivelling", {"magical": 6}, 1, -1, 1)


def DreadCurse():
  return CombatSpell("Dread Curse", {"magical": 9}, 2, -2, 2)


class EnchantWeapon(CombatSpell):

  def __init__(self):
    super().__init__("Enchant Weapon", {}, 0, 0, 1)
    self.weapon = None
    self.active_change = 0
    self.passive_change = 0

  def get_usable_interrupt(self, event, owner, state):
    interrupt = super().get_usable_interrupt(event, owner, state)
    if not isinstance(interrupt, events.CastSpell):
      return interrupt

    # Instead of immediately casting the spell, ask the user to make a choice. If they have no
    # valid choices (or if they choose nothing), then don't cast the spell at all.
    choice = events.SinglePhysicalWeaponChoice(owner, "Choose a physical weapon to enchant")
    cast = events.CastSpell(owner, self, choice=choice)
    return events.Sequence([
        choice, events.Conditional(owner, choice, "choice_count", {0: events.Nothing(), 1: cast})],
        owner,
    )

  def activate(self):
    assert self.choice.is_resolved()
    assert len(self.choice.chosen) == 1
    self.weapon = self.choice.chosen[0]
    self.active_change = self.weapon.active_bonuses["physical"]
    self.passive_change = self.weapon.passive_bonuses["physical"]
    self.weapon.active_bonuses["physical"] -= self.active_change
    self.weapon.active_bonuses["magical"] += self.active_change
    self.weapon.passive_bonuses["physical"] -= self.passive_change
    self.weapon.passive_bonuses["magical"] += self.passive_change

  def deactivate(self):
    if self.weapon is None:
      return
    self.weapon.active_bonuses["physical"] += self.active_change
    self.weapon.active_bonuses["magical"] -= self.active_change
    self.weapon.passive_bonuses["physical"] += self.passive_change
    self.weapon.passive_bonuses["magical"] -= self.passive_change
    self.active_change = 0
    self.passive_change = 0
    self.weapon = None


class RedSign(CombatSpell):

  INVALID_ATTRIBUTES = {"magical immunity", "elusive", "mask", "spawn"}

  def __init__(self):
    super().__init__("Red Sign", {}, 1, -1, 1)

  def get_usable_interrupt(self, event, owner, state):
    interrupt = super().get_usable_interrupt(event, owner, state)
    if not isinstance(interrupt, events.CastSpell):
      return interrupt

    assert hasattr(event, "monster")
    attributes = sorted(event.monster.attributes(state, owner) - self.INVALID_ATTRIBUTES)
    choice = events.MultipleChoice(owner, "Choose an ability to ignore", attributes + ["none"])
    cast = events.CastSpell(owner, self, choice=choice)
    return events.Sequence([choice, cast], owner)

  def get_modifier(self, other, attribute):
    if self.active and attribute == "toughness":
      return -1
    return None

  def get_override(self, other, attribute):
    if self.active and self.choice is not None and attribute == self.choice.choice:
      return False
    return None


class Voice(Spell):

  def __init__(self):
    super().__init__(
        "Voice", {"speed": 1, "sneak": 1, "fight": 1, "will": 1, "lore": 1, "luck": 1}, 0, -1, 1)

  def get_usable_trigger(self, event, owner, state):
    return None
    # TODO: an actual event for upkeep
    # if self.exhausted or owner.sanity < self.sanity_cost:
    #   return None
    # if state.turn_phase != "upkeep" or state.characters[state.turn_idx] != owner:
    #   return None
    # return events.CastSpell(owner, self)

  def get_trigger(self, event, owner, state):
    if isinstance(event, events.Mythos) and self.active:
      return events.DeactivateSpell(owner, self)
    return None


class FindGate(Spell):

  def __init__(self):
    super().__init__("Find Gate", {}, 0, -1, 1)

  def movement_in_other_world(self, owner, state):
    if state.turn_phase != "movement" or state.characters[state.turn_idx] != owner:
      return False
    if not isinstance(owner.place, places.OtherWorld):
      return False
    return True

  def get_usable_interrupt(self, event, owner, state):
    if self.exhausted or owner.sanity < self.sanity_cost:
      return None
    if not self.movement_in_other_world(owner, state):
      return None
    if not isinstance(event, events.ForceMovement):
      return None
    return events.CastSpell(owner, self)

  def get_usable_trigger(self, event, owner, state):
    if self.exhausted or owner.sanity < self.sanity_cost:
      return None
    if not self.movement_in_other_world(owner, state):
      return None
    # Note: you can travel into another world during the movement phase by failing a combat check
    # against certain types of monsters.
    if not isinstance(event, events.Travel):
      return None
    return events.CastSpell(owner, self)

  def get_cast_event(self, owner, state):
    return events.Return(owner, owner.place.info.name)  # TODO: cancel the ForceMovement if any.


def CreateCommon():
  common = []
  for item in [
      Automatic45, DarkCloak, Revolver38, Dynamite,
      TommyGun, Food, ResearchMaterials, Bullwhip, Cross,
  ]:
    common.extend([item(), item()])
  return common


def CreateUnique():
  counts = {
      HolyWater: 4,
      EnchantedKnife: 2,
      MagicLamp: 1,
  }
  uniques = []
  for item, count in counts.items():
    uniques.extend([item() for _ in range(count)])
  return uniques


def CreateSpells():
  counts = {
      DreadCurse: 4,
      EnchantWeapon: 3,
      FindGate: 4,
      RedSign: 2,
      Shrivelling: 5,
      Voice: 3,
      Wither: 6,
  }
  spells = []
  for item, count in counts.items():
    spells.extend([item() for _ in range(count)])
  return spells
