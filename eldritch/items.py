import operator

from eldritch.assets import Card, Deputy
from eldritch import events
from eldritch import places
from eldritch import values
from eldritch import monsters


class Item(Card):

  ITEM_TYPES = {"weapon", "tome", None}

  def __init__(
      self, name, idx, deck, active_bonuses, passive_bonuses, hands, price, item_type=None,
  ):
    assert item_type in self.ITEM_TYPES
    super().__init__(name, idx, deck, active_bonuses, passive_bonuses)
    self.hands = hands
    self.price = price
    self.item_type = item_type

  def hands_used(self):
    return self.hands if self.active else 0


class Weapon(Item):

  def __init__(self, name, idx, deck, active_bonuses, passive_bonuses, hands, price):
    super().__init__(name, idx, deck, active_bonuses, passive_bonuses, hands, price, "weapon")


class OneshotWeapon(Weapon):

  def get_trigger(self, event, owner, state):
    if not isinstance(event, events.Check) or event.check_type != "combat":
      return None
    if event.character != owner or not self.active:
      return None
    return events.DiscardSpecific(event.character, [self])


class Food(Item):

  def __init__(self, idx):
    super().__init__("Food", idx, "common", {}, {}, None, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.GainOrLoss) or owner != event.character:
      return None
    if isinstance(event.losses.get("stamina"), values.Value):
      if event.losses["stamina"].value(state) < 1:
        return None
    elif event.losses.get("stamina", 0) < 1:
      return None

    discard = events.DiscardSpecific(event.character, [self])
    prevent = events.LossPrevention(self, event, "stamina", 1)
    return events.Sequence([discard, prevent], owner)


class Whiskey(Item):

  def __init__(self, idx):
    super().__init__("Whiskey", idx, "common", {}, {}, None, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.GainOrLoss) or owner != event.character:
      return None
    if isinstance(event.losses.get("sanity"), values.Value):
      if event.losses["sanity"].value(state) < 1:
        return None
    elif event.losses.get("sanity", 0) < 1:
      return None

    discard = events.DiscardSpecific(event.character, [self])
    prevent = events.LossPrevention(self, event, "sanity", 1)
    return events.Sequence([discard, prevent], owner)


class ResearchMaterials(Item):

  def __init__(self, idx):
    super().__init__("Research Materials", idx, "common", {}, {}, None, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.SpendMixin) or event.is_done():
      return None
    if event.character != owner or "clues" not in event.spendable:
      return None
    if self.handle in event.spent_handles():
      return events.Unspend(owner, event, self.handle)
    return events.Spend(owner, event, self.handle, {"clues": 1})

  def get_spend_event(self, owner):
    return events.DiscardSpecific(owner, [self])


class Bullwhip(Weapon):

  def __init__(self, idx):
    super().__init__("Bullwhip", idx, "common", {"physical": 1}, {}, 1, 2)

  def get_usable_trigger(self, event, owner, state):
    if not isinstance(event, events.Check) or owner != event.character:
      return None
    if event.check_type != "combat":
      return None
    return None  # TODO: create an event here


class Cross(Weapon):

  def __init__(self, idx):
    super().__init__("Cross", idx, "common", {}, {"horror": 1}, 1, 3)

  def get_bonus(self, check_type, attributes):
    bonus = super().get_bonus(check_type, attributes)
    if self.active and check_type == "magical" and attributes and "undead" in attributes:
      bonus += 3
    return bonus


class Derringer18(Weapon):

  def __init__(self, idx):
    super().__init__(".18 Derringer", idx, "common", {"physical": 2}, {}, 1, 3)
    self.losable = False


class Tome(Item):

  def __init__(self, name, idx, deck, price, movement_cost):
    super().__init__(name, idx, deck, {}, {}, None, price, "tome")
    self.movement_cost = movement_cost

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.CityMovement) or event.character != owner or event.is_done():
      return None
    if self.exhausted:
      return None
    if event.character.movement_points < self.movement_cost:
      return None
    return events.ReadTome([
        events.ExhaustAsset(owner, self),
        events.ChangeMovementPoints(owner, -self.movement_cost),
        self.read_event(owner),
    ], owner)

  def get_usable_trigger(self, event, owner, state):
    if not isinstance(event, events.WagonMove) or event.character != owner:
      return None
    if self.exhausted:
      return None
    if event.character.movement_points < self.movement_cost:
      return None
    return events.ReadTome([
        events.ExhaustAsset(owner, self),
        events.ChangeMovementPoints(owner, -self.movement_cost),
        self.read_event(owner),
    ], owner)

  def read_event(self, owner):  # pylint: disable=unused-argument
    return events.Nothing()


class AncientTome(Tome):

  def __init__(self, idx):
    super().__init__("Ancient Tome", idx, "common", 4, 2)

  def read_event(self, owner):
    check = events.Check(owner, "lore", -1)
    success = events.Sequence(
        [events.Draw(owner, "spells", 1), events.DiscardSpecific(owner, [self])], owner,
    )
    return events.PassFail(owner, check, success, events.Nothing())


def DarkCloak(idx):
  return Item("Dark Cloak", idx, "common", {}, {"evade": 1}, None, 2)


def Revolver38(idx):
  return Weapon(".38 Revolver", idx, "common", {"physical": 3}, {}, 1, 4)


def Automatic45(idx):
  return Weapon(".45 Automatic", idx, "common", {"physical": 4}, {}, 1, 5)


def Dynamite(idx):
  return OneshotWeapon("Dynamite", idx, "common", {"physical": 8}, {}, 2, 4)


def HolyWater(idx):
  return OneshotWeapon("Holy Water", idx, "unique", {"magical": 6}, {}, 2, 4)


def EnchantedKnife(idx):
  return Weapon("Enchanted Knife", idx, "unique", {"magical": 3}, {}, 1, 5)


def MagicLamp(idx):
  return Weapon("Magic Lamp", idx, "unique", {"magical": 5}, {}, 2, 7)


def TommyGun(idx):
  return Weapon("Tommy Gun", idx, "common", {"physical": 6}, {}, 2, 7)


class Spell(Item):

  def __init__(self, name, idx, active_bonuses, hands, difficulty, sanity_cost):
    super().__init__(name, idx, "spells", active_bonuses, {}, hands, None)
    self.difficulty = difficulty
    self.sanity_cost = sanity_cost
    self.in_use = False
    self.deactivatable = False
    self.choice = None
    self.check = None

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
    hands_available = owner.hands_available()
    if isinstance(event, events.CombatChoice):
      hands_available -= event.hands_used()
    if hands_available < self.hands:
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


def Wither(idx):
  return CombatSpell("Wither", idx, {"magical": 3}, 1, 0, 0)


def Shrivelling(idx):
  return CombatSpell("Shrivelling", idx, {"magical": 6}, 1, -1, 1)


def DreadCurse(idx):
  return CombatSpell("Dread Curse", idx, {"magical": 9}, 2, -2, 2)


class BindMonster(CombatSpell):
  def __init__(self, idx):
    super().__init__("Bind Monster", idx, {}, 2, 4, 2)
    self.combat_round = None

  def get_required_successes(self, state):
    self.combat_round = state.event_stack[-2].combat_round
    # CombatRound[-3] > CombatChoice[-2] > CastSpell[-1]
    return self.combat_round.monster.toughness(state, self.combat_round.character)

  def get_usable_interrupt(self, event, owner, state):
    if (
        isinstance(event, events.CombatChoice)
        and event.combat_round is not None
        and isinstance(event.combat_round.monster, monsters.Monster)
    ):
      return super().get_usable_interrupt(event, owner, state)
    return None

  def get_cast_event(self, owner, state):
    return events.Sequence(
        [
            events.DiscardSpecific(owner, [self]),
            events.PassCombatRound(self.combat_round),
        ],
        owner,
    )


class EnchantWeapon(CombatSpell):
  def __init__(self, idx):
    super().__init__("Enchant Weapon", idx, {}, 0, 0, 1)
    self.weapon = None
    self.active_change = 0
    self.passive_change = 0

  def get_usable_interrupt(self, event, owner, state):
    interrupt = super().get_usable_interrupt(event, owner, state)
    if not isinstance(interrupt, events.CastSpell):
      return interrupt

    # Instead of immediately casting the spell, ask the user to make a choice. If they have no
    # valid choices (or if they choose nothing), then don't cast the spell at all.
    spend = values.ExactSpendPrerequisite({"sanity": self.sanity_cost})
    choice = events.SinglePhysicalWeaponChoice(
        owner, "Choose a physical weapon to enchant", spend=spend,
    )
    return events.CastSpell(owner, self, choice=choice)

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


class FleshWard(Spell):
  def __init__(self, idx):
    super().__init__("Flesh Ward", idx, {}, 0, -2, 1)
    self.loss = None

  def get_trigger(self, event, owner, state):
    if isinstance(event, events.AncientOneAwaken):
      return events.DiscardSpecific(owner, [self])
    return None

  def get_usable_interrupt(self, event, owner, state):
    if (
        not isinstance(event, events.GainOrLoss)
        or event.character != owner
        or "stamina" not in event.losses
        or owner.sanity < self.sanity_cost
        or self.exhausted
    ):
      return None
    stam_loss = event.losses["stamina"]
    if (
        (isinstance(stam_loss, values.Value) and stam_loss.value(state) == 0)
        or (isinstance(stam_loss, (int, float)) and stam_loss == 0)
    ):
      return None
    self.loss = event
    return events.CastSpell(owner, self)

  def get_cast_event(self, owner, state):
    return events.LossPrevention(self, self.loss, "stamina", float("inf"))


class Heal(Spell):
  def __init__(self, idx):
    super().__init__("Heal", idx, {}, 0, 1, 1)

  def get_usable_interrupt(self, event, owner, state):
    if not self.exhausted and isinstance(event, events.UpkeepActions):
      return events.CastSpell(owner, self)
    return None

  def get_cast_event(self, owner, state):
    neighbors = [char for char in state.characters if char.place == owner.place]
    gains = {idx: events.Gain(char, {"stamina": self.check.successes})
             for idx, char in enumerate(neighbors)}
    choice = events.MultipleChoice(
        owner, "Choose a character to heal", [char.name for char in neighbors])
    cond = events.Conditional(owner, choice, "choice_index", gains)
    return events.Sequence([choice, cond], owner)


class Mists(Spell):
  def __init__(self, idx):
    super().__init__("Mists", idx, {}, 0, None, 0)
    self.evade = None

  def get_usable_interrupt(self, event, owner, state):
    if event.is_done() or self.exhausted or getattr(event, "character", None) != owner:
      return None
    # TODO: be able to cast Mists on an EvadeCheck
    if isinstance(event, events.EvadeRound):
      self.difficulty = event.monster.difficulty("evade", state, owner)
      self.evade = event
      return events.CastSpell(owner, self)
    if (
        isinstance(event, events.SpendChoice)
        and len(state.event_stack) >= 3
        and isinstance(state.event_stack[-2], events.Check)
        and isinstance(state.event_stack[-3], events.EvadeRound)
        and not state.event_stack[-3].is_done()
    ):
      self.evade = state.event_stack[-3]
      self.difficulty = self.evade.monster.difficulty("evade", state, owner)
      return events.CastSpell(owner, self)
    return None

  def get_cast_event(self, owner, state):
    return events.PassEvadeRound(self.evade)


class RedSign(CombatSpell):

  INVALID_ATTRIBUTES = {"magical immunity", "elusive", "mask", "spawn"}

  def __init__(self, idx):
    super().__init__("Red Sign", idx, {}, 1, -1, 1)

  def get_usable_interrupt(self, event, owner, state):
    interrupt = super().get_usable_interrupt(event, owner, state)
    if not isinstance(interrupt, events.CastSpell):
      return interrupt

    if not hasattr(event, "monster"):
      return None
    attributes = sorted(event.monster.attributes(state, owner) - self.INVALID_ATTRIBUTES)
    choices = attributes + ["none", "Cancel"]
    spend = values.ExactSpendPrerequisite({"sanity": self.sanity_cost})
    spends = [spend] * (len(choices)-1) + [None]
    choice = events.SpendChoice(owner, "Choose an ability to ignore", choices, spends=spends)
    return events.CastSpell(owner, self, choice=choice)

  def get_modifier(self, other, attribute):
    if self.active and attribute == "toughness":
      return -1
    return None

  def get_override(self, other, attribute):
    if self.active and self.choice is not None and attribute == self.choice.choice:
      return False
    return None


class Voice(Spell):

  def __init__(self, idx):
    super().__init__(
        "Voice", idx, {"speed": 1, "sneak": 1, "fight": 1, "will": 1, "lore": 1, "luck": 1},
        0, -1, 1,
    )

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

  def __init__(self, idx):
    super().__init__("Find Gate", idx, {}, 0, -1, 1)

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
    if not isinstance(event, (events.Travel, events.ForceMovement)):
      return None
    # Food for thought: should we have a SpendMixin for GateChoice so that you only get one choice?
    return events.CastSpell(owner, self)

  def get_cast_event(self, owner, state):
    if len(state.event_stack) > 1 and isinstance(state.event_stack[-2], events.ForceMovement):
      return events.Sequence(
          [events.Return(owner, owner.place.info.name), events.CancelEvent(state.event_stack[-2])],
          owner,
      )
    return events.Return(owner, owner.place.info.name)


class DeputysRevolver(Weapon):

  def __init__(self):
    super().__init__("Deputy's Revolver", None, "tradables", {"physical": 3}, {}, 1, 0)
    self.losable = False


class PatrolWagon(Card):

  def __init__(self):
    super().__init__("Patrol Wagon", None, "tradables", {}, {})

  def get_usable_interrupt(self, event, owner, state):
    if not isinstance(event, events.CityMovement) or event.character != owner:
      return None
    if event.is_done() or event.moved:
      return None
    choice = events.PlaceChoice(owner, "Move using Patrol Wagon?", none_choice="Cancel")
    # TODO: add an annotation to the PlaceChoice (e.g. "Move").
    was_cancelled = values.Calculation(choice, None, operator.methodcaller("is_cancelled"))
    patrol = events.ForceMovement(owner, choice)
    cancel = events.CancelEvent(event)
    move = events.WagonMove([patrol, cancel], owner)
    cond = events.Conditional(owner, was_cancelled, None, {0: move, 1: events.Nothing()})
    return events.Sequence([choice, cond], owner)

  def get_trigger(self, event, owner, state):
    if not isinstance(event, (events.Combat, events.Return)) or event.character != owner:
      return None
    die = events.DiceRoll(owner, 1)
    discard = events.DiscardSpecific(owner, [self], to_box=True)
    cond = events.Conditional(owner, values.Die(die), None, {0: discard, 2: events.Nothing()})
    return events.Sequence([die, cond], owner)


def CreateCommon():
  common = []
  for item in [
      AncientTome, Automatic45, DarkCloak, Derringer18, Revolver38, Dynamite,
      TommyGun, Food, ResearchMaterials, Bullwhip, Cross,
  ]:
    common.extend([item(0), item(1)])
  return common


def CreateUnique():
  counts = {
      HolyWater: 4,
      EnchantedKnife: 2,
      MagicLamp: 1,
  }
  uniques = []
  for item, count in counts.items():
    uniques.extend([item(idx) for idx in range(count)])
  return uniques


def CreateSpells():
  counts = {
      BindMonster: 2,
      DreadCurse: 4,
      EnchantWeapon: 3,
      FindGate: 4,
      FleshWard: 4,
      Mists: 4,
      RedSign: 2,
      Shrivelling: 5,
      Voice: 3,
      Wither: 6,
  }
  spells = []
  for item, count in counts.items():
    spells.extend([item(idx) for idx in range(count)])
  return spells


def CreateTradables():
  return [DeputysRevolver(), PatrolWagon()]


def CreateSpecials():
  return [Deputy()]
