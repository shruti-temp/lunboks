import eldritch.events as events


class EncounterCard(object):

  def __init__(self, name, encounter_creators):
    self.name = name
    self.encounters = {}
    for location_name, encounter_creator in encounter_creators.items():
      self.add_encounter(location_name, encounter_creator)

  def add_encounter(self, location_name, encounter_creator):
    self.encounters[location_name] = encounter_creator

  # TODO: fixed encounters
  def encounter_event(self, character, location_name):
    if location_name not in self.encounters:
      print(f"TODO: missing encounters for {self.name} at {location_name}")
      return events.Nothing()
    return self.encounters[location_name](character)


def Diner1(char):
  prereq = events.AttributePrerequisite(char, "dollars", 1, "at least")
  dollar_choice = events.MultipleChoice(
      char, "How many dollars do you want to pay?", [x for x in range(0, min(char.dollars+1, 7))])
  spend = events.Loss(char, {"dollars": dollar_choice})
  gain = events.SplitGain(char, "stamina", "sanity", dollar_choice)
  spend_and_gain = events.Sequence([dollar_choice, spend, gain], char)
  return events.PassFail(char, prereq, spend_and_gain, events.Nothing())
def Diner2(char):
  return events.DrawSpecific(char, "common", "Food")
def Diner3(char):
  adj = events.GainOrLoss(char, {"stamina": 2}, {"dollars": 1})
  choice = events.BinaryChoice(char, "Pay $1 for pie?", "Pay $1", "Go Hungry", adj, events.Nothing())
  prereq = events.AttributePrerequisite(char, "dollars", 1, "at least")
  return events.PassFail(char, prereq, choice, events.Nothing())
def Diner4(char):
  gain = events.Gain(char, {"dollars": 5})
  check = events.Check(char, "will", -2)
  return events.PassFail(char, check, gain, events.Nothing())
def Diner5(char):
  bless = events.Bless(char)
  curse = events.Curse(char)
  check = events.Check(char, "luck", -1)
  return events.PassFail(char, check, bless, curse)
def Diner6(char):
  loss = events.Loss(char, {"stamina": 2})
  check = events.Check(char, "luck", -1)
  return events.PassFail(char, check, events.Nothing(), loss)
def Diner7(char):
  move = events.ForceMovement(char, "Easttown")
  die = events.DiceRoll(char, 1)
  gain = events.Gain(char, {"dollars": die})
  check = events.Check(char, "sneak", -1)
  return events.PassFail(char, check, events.Sequence([die, gain]), move)

def Roadhouse1(char):
  # TODO: this prerequisite should account for characters that can spend clues in other ways, such
  # as by discarding a research materials, or by using the violinist's clues, etc.
  prereq = events.AttributePrerequisite(char, "clues", 3, "at least")
  spend = events.Loss(char, {"clues": 3})
  # TODO: prerequisite of the ally being in the deck.
  draw = events.DrawSpecific(char, "allies", "Traveling Salesman")
  take = events.Sequence([spend, draw], char)
  nothing = events.Nothing()
  choice = events.BinaryChoice(char, "Spend 3 clues for an ally?", "Yes", "No", take, nothing)
  return events.PassFail(char, prereq, choice, nothing)
def Roadhouse2(char):
  check = events.Check(char, "luck", -1)
  gain = events.Gain(char, {"dollars": 5})
  dollar_loss = events.Loss(char, {"dollars": 3})
  stamina_loss = events.Loss(char, {"stamina": 1})
  move = events.ForceMovement(char, "Easttown")
  prereq = events.AttributePrerequisite(char, "dollars", 3, "at least")
  loss = events.PassFail(char, prereq, dollar_loss, events.Sequence([stamina_loss, move], char))
  return events.PassFail(char, check, gain, loss)
def Roadhouse3(char):
  return events.DrawSpecific(char, "common", "Whiskey")
def Roadhouse4(char):
  return events.Nothing() # TODO buying stuff
def Roadhouse5(char):
  return events.Nothing() # TODO monster cup
def Roadhouse6(char):
  check = events.Check(char, "will", -1)
  clues = events.Gain(char, {"clues": 2})
  move = events.ForceMovement(char, "Easttown")
  dollars_stolen = events.Loss(char, {"dollars": float("inf")})
  # TODO: allow the character to choose an item to be stolen instead, but this needs to be
  # conditional on a prerequisite of the character having at least one item.
  return events.PassFail(char, check, clues, events.Sequence([move, dollars_stolen], char))
def Roadhouse7(char):
  loss = events.Loss(char, {"dollars": float("inf")})
  check = events.Check(char, "luck", -1)
  return events.PassFail(char, check, events.Nothing(), loss)

def Police1(char):
  check = events.Check(char, "will", -1)
  gain = events.Gain(char, {"clues": 1})
  move = events.ForceMovement(char, "Easttown")
  loss = events.Loss(char, {"sanity": 1})
  return events.PassFail(char, check, gain, events.Sequence([move, loss], char))
def Police2(char):
  check = events.Check(char, "luck", -1)
  loss = events.Loss(char, {"stamina": 2})
  return events.PassFail(char, check, events.Nothing(), loss)
def Police3(char):
  check = events.Check(char, "will", -1)
  gain = events.Gain(char, {"clues": 2})
  return events.PassFail(char, check, gain, events.Nothing())
def Police4(char):
  check = events.Check(char, "luck", -1)
  draw = events.DrawSpecific(char, "common", ".38 Revolver")
  return events.PassFail(char, check, draw, events.Nothing())
def Police5(char):
  return events.Nothing()  # TODO discarding all weapons
def Police6(char):
  check = events.Check(char, "luck", -2)
  draw = events.Draw(char, "unique", 1)
  return events.PassFail(char, check, draw, events.Nothing())
def Police7(char):
  check = events.Check(char, "sneak", 0)
  draw = events.DrawSpecific(char, "common", "Research Materials")
  return events.PassFail(char, check, draw, events.Nothing())

def Lodge1(char):
  check = events.Check(char, "lore", -1)
  draw = events.Draw(char, "spells", 2)
  return events.PassFail(char, check, draw, events.Nothing())

def Witch2(char):
  check = events.Check(char, "luck", -1)
  draw = events.Draw(char, "unique", 1)
  return events.PassFail(char, check, draw, events.Nothing())

def Store5(char):
  check = events.Check(char, "will", -2)
  draw = events.Draw(char, "common", 3)
  return events.PassFail(char, check, draw, events.Nothing())

def Society4(char):
  check = events.Check(char, "luck", -1)
  skill = events.Sequence([events.Draw(char, "skills", 1), events.Delayed(char)], char)
  cond = events.Conditional(char, check, "successes", {0: events.Nothing(), 2: skill})
  return events.Sequence([check, cond], char)

def Administration7(char):
  check = events.Check(char, "will", -2)
  gain = events.Gain(char, {"dollars": 8})
  arrest = events.Arrested(char)
  return events.PassFail(char, check, gain, arrest)
def Train3(char):
  return events.SplitGain(char, "stamina", "sanity", 2)

def Asylum1(char):
  check = events.Check(char, "lore", 0)
  roll0 = events.GainOrLoss(char, {"clues": 1}, {"sanity": 1})
  roll1 = events.Gain(char, {"clues": 2})
  roll3 = events.Gain(char, {"clues": 3})
  cond = events.Conditional(char, check, "successes", {0: roll0, 1: roll1, 3: roll3})
  return events.Sequence([check, cond], char)
def Asylum2(char):
  check = events.Check(char, "speed", -1)
  item = events.Draw(char, "unique", 1)
  move = events.ForceMovement(char, "Downtown")
  return events.PassFail(char, check, item, move)
def Asylum3(char):
  check = events.Check(char, "sneak", -1)
  escape = events.ForceMovement(char, "Downtown")
  arrested = events.Arrested(char)
  return events.PassFail(char, check, escape, arrested)
def Asylum4(char):
  check = events.Check(char, "lore", -1)
  spell = events.Draw(char, "spells", 1)
  return events.PassFail(char, check, spell, events.Nothing())
def Asylum5(char):
  check = events.Check(char, "will", -1)
  lose = events.Nothing() #TODO: Oh dear...so many choices
  skill = events.Draw(char, "skills", 1)
  cond = events.Conditional(char, check, "successes", {0: lose, 2: skill})
  return events.Sequence([check, cond], char)
def Asylum6(char):
  check = events.Check(char, "lore", -2)
  gain = events.Gain(char, {"clues": 2})
  loss = events.Loss(char, {"stamina": 1})
  return events.PassFail(char, check, gain, loss)
def Asylum7(char):
  check = events.Check(char, "fight", -2)
  stamina = events.Gain(char, {"stamina": 2})
  rest = events.Sequence([stamina, events.LoseTurn(char)], char)
  fight = events.PassFail(char, check, events.Nothing(), rest)
  return events.BinaryChoice(char, "Do you resist?", "Yes", "No", fight, rest)

def Bank1(char):
  return events.Nothing() # TODO: implement location choice
def Bank2(char):
  check = events.Check(char, "luck", -1)
  spend = events.Loss(char, {"dollars": 2})
  common = events.Draw(char, "common", 1)
  unique = events.Draw(char, "unique", 1)
  cond = events.Conditional(char, check, "successes", {0: common, 1: unique})
  prereq = events.AttributePrerequisite(char, "dollars", 2, "at least")
  nothing = events.Nothing()
  choice = events.BinaryChoice(
                              char, "Pay $2 for man's last possession?",
                              "Pay $2",
                              "Let man and his family go hungry", 
                              events.Sequence([spend, check, cond], char), nothing)
  return events.PassFail(char, prereq, choice, nothing)
def Bank3(char):
  prep = events.CombatChoice(char, "Choose weapons to fight the bank robbers")
  check = events.Check(char, "combat", -1)
  robbed = events.Loss(char, {"dollars": char.dollars})
  nothing = events.Nothing()
  cond = events.Conditional(char, check, "successes", {0: robbed, 1: nothing})
  return events.Sequence([prep, check, cond], char)
def Bank4(char):
  check = events.Check(char, "luck", -2)
  bless = events.Bless(char)
  curse = events.Curse(char)
  return events.PassFail(char, check, bless, curse)
def Bank5(char):
  check = events.Check(char, "speed", -1)
  gain = events.Gain(char, {"dollars": 2})
  return events.PassFail(char, check, gain, events.Nothing())
def Bank6(char):
  return events.Loss(char, {"sanity": 1})
def Bank7(char):
  return events.GainOrLoss(char, {"dollars": 5}, {"sanity": 1})

def Square1(char):
  return events.Gain(char, {"stamina": 1})
def Square2(char):
  check = events.Check(char, "will", -1)
  # TODO: prerequisite ally being in the deck, otherwise two clue tokens
  ally = events.DrawSpecific(char, "allies", "Fortune Teller")
  return events.PassFail(char, check, ally, events.Nothing())
def Square3(char):
  check = events.Check(char, "will", -1)
  loss = events.Loss(char, {"sanity": 1, "stamina": 1})
  return events.PassFail(char, check, events.Nothing(), loss)
def Square4(char):
  check = events.Check(char, "luck", -2)
  loss = events.Nothing()  #TODO: Choose an item to lose
  return events.PassFail(char, check, events.Nothing(), loss)
def Square5(char):
  check = events.Check(char, "fight", -1)
  move = events.ForceMovement(char, "Downtown")
  return events.PassFail(char, check, events.Nothing(), move)
def Square6(char):
  check = events.Check(char, "luck", -1)
  stamina = events.Loss(char, {"stamina": 1})
  lose = events.Sequence([stamina, events.Curse(char)], char)
  buy = events.Nothing() #TODO: Buying stuff
  interact = events.PassFail(char, check, buy, lose)
  return events.BinaryChoice(char, "Interact with the gypsies?", "Yes", "No", interact, events.Nothing())
def Square7(char):
  check = events.Check(char, "luck", -1)
  draw = events.Draw(char, "spells", 1)
  gain = events.GainOrLoss(char, {"clues": 2}, {"stamina": 1})
  success = events.Sequence([draw, gain], char)
  fail = events.Nothing() # TODO: RUN!!! It's a GATE!
  return events.PassFail(char, check, success, fail)

def Docks1(char):
  check = events.Check(char, "luck", -1)
  spell = events.Draw(char, "spells", 1)
  return events.PassFail(char, check, spell, events.Nothing())
def Docks2(char):
  # TODO: you should just be able to draw two items
  item1 = events.Draw(char, "common", 1)
  item2 = events.Draw(char, "common", 1)
  items = events.Sequence([item1, item2], char)
  check = events.Check(char, "luck", -1)
  success = events.Nothing()
  fail = events.Arrested(char)
  passfail = events.PassFail(char, check, success, fail)
  return events.Sequence([items, passfail], char)
def Docks3(char):
  check = events.Check(char, "fight", 0)
  dollars = events.Gain(char, {"dollars": 3}) # TODO: This is really dollars * number of successes
  move = events.ForceMovement(char, "Merchant")
  stamina = events.Loss(char, {"stamina": 1})
  cond= events.Conditional(char, check, "successes", {0: events.Sequence([stamina, move], char), 1: dollars})
  return events.Sequence([check, cond], char)
def Docks4(char):
  check = events.Check(char, "will", -1)
  item = events.Draw(char, "unique", 1)
  success = events.Sequence([events.Loss(char, {"sanity": 1}), item], char)
  fail = events.Sequence([events.Loss(char, {"sanity": 2}), item], char)
  return events.PassFail(char, check, success, fail)
def Docks5(char):
  check = events.Check(char, "speed", -1)
  loss = events.Loss(char, {"sanity": 1})
  return events.PassFail(char, check, events.Nothing(), loss)
def Docks6(char):
  check = events.Check(char, "will", 1)
  lost = events.Nothing() # TODO: Oh No, what time is it?  Where am I?  I'm lost in Time AND Space!
  return events.PassFail(char, check, events.Nothing(), lost)
def Docks7(char):
  check = events.Check(char, "luck", -1)
  draw = events.Draw(char, "common", 1)
  struggle = events.Loss(char, {"stamina": 3, "sanity": 1})
  return events.PassFail(char, check, draw, struggle)

def Unnamable1(char):
  loss = events.Loss(char, {"sanity": 2})
  # TODO: add prerequisite of ally being in deck
  ally = events.DrawSpecific(char, "allies", "Brave Guy")
  listen = events.Sequence([loss, ally], char)
  return events.BinaryChoice(char, "Listen to the tale?", "Yes", "No", listen, events.Nothing())
def Unnamable2(char):
  check = events.Check(char, "lore", -1)
  spell = events.Draw(char, "spells", 1)
  clues = events.Gain(char, {"clues": 2})
  delayed = events.Delayed(char)
  read = events.PassFail(char, check, spell, events.Sequence([clues, delayed], char))
  return events.BinaryChoice(char, "Read the manuscript?", "Yes", "No", read, events.Nothing())
def Unnamable3(char):
  # TODO: WHAT IS THAT THING??? IT LOOKS LIKE A GATE!
  return events.Nothing()
def Unnamable4(char):
  check = events.Check(char, "speed", -1)
  move = events.ForceMovement(char, "Merchant")
  loss = events.Loss(char, {"stamina": 2})
  return events.PassFail(char, check, move, loss)
def Unnamable5(char):
  check = events.Check(char, "luck", -1)
  unique = events.Draw(char, "unique", 1)
  loss = events.Loss(char, {"sanity": 1, "stamina": 2})
  return events.PassFail(char, check, unique, loss)
def Unnamable6(char):
  check = events.Check(char, "speed", -1)
  lost = events.Nothing() #TODO: I'm stuck inside a clock and I'm somewhere around Mars?
  return events.PassFail(char, check, events.Nothing(), lost)
def Unnamable7(char):
  check = events.Check(char, "luck", -1)
  unique = events.Draw(char, "unique", 1)
  return events.PassFail(char, check, unique, events.Nothing())

def Isle1(char):
  spell = events.Draw(char, "spells", 1)
  loss = events.Loss(char, {"sanity": 1})
  return events.Sequence([spell, loss], char)
def Isle2(char):
  check = events.Check(char, "sneak", -1)
  # TODO add prerequisite for Ally in deck
  ally = events.DrawSpecific(char, "allies", "Mortician")
  return events.PassFail(char, check, ally, events.Nothing())
def Isle3(char):
  stamina = events.Loss(char, {"stamina": 1})
  check = events.Check(char, "will", -1)
  sanity = events.Loss(char, {"sanity": 1})
  will = events.PassFail(char, check, events.Nothing(), sanity)
  return events.Sequence([stamina, will], char)
def Isle4(char):
  check = events.Check(char, "will", -1)
  return events.PassFail(char, check, events.Nothing(), events.Curse(char))
def Isle5(char):
  check = events.Check(char, "will", -2)
  sanity = events.Loss(char, {"sanity": 3})
  return events.PassFail(char, check, events.Nothing(), sanity)
def Isle6(char):
  return events.GainOrLoss(char, {"clues": 1}, {"sanity": 1})
def Isle7(char):
  check = events.Check(char, "sneak", -1)
  clues = events.Gain(char, {"clues": 2})
  return events.PassFail(char, check, clues, events.Nothing())

def Hospital1(char):
  return events.Loss(char, {"clues": 1})
def Hospital2(char):
  prep = events.CombatChoice(char, "Choose weapons to fight the corpse")
  check = events.Check(char, "combat", -1)
  won = events.Gain(char, {"clues", 1})
  lost = events.ForceMovement(char, "Uptown")
  cond = events.Conditional(char, check, "successes", {0: lost, 1: won})
  return events.Sequence([prep, check, cond], char)
def Hospital3(char):
  die = events.DiceRoll(char, 1)
  # TODO: On a 1-3 gain that many stamina, on a 4-6 nothing happens.
  return events.Nothing(char)
def Hospital4(char):
  check = events.Check(char, "luck", -1)
  gain = events.Gain(char, {"sanity": 2, "dollars": 3})
  fail1 = events.Lose(char, {"sanity": 2})
  fail2 = events.ForceMove(char, "Uptown")
  fail = events.Sequence([fail1, fail2], char)
  return events.PassFail(char, check, gain, fail)
def Hospital5(char):
  check = events.Check(char, "sneak", -1)
  gain = events.Draw(char, "spells", 1)
  return events.PassFail(char, check, gain, events.Nothing(char))
def Hospital6(char):
  check = events.Check(char, "will", -1)
  item = events.Draw(char, "unique", 1)
  fail1 = events.Lose(char, {"sanity":1})
  fail2 = events.ForceMovement(char, "Uptown")
  fail = events.Sequence([fail1, fail2], char)
  return events.PassFail(char, check, item, fail)
def Hospital7(char):
  check = events.Check(char, "lore", 0)
  clue = events.Gain(char, {"clues": 1})
  return events.PassFail(char, check, clue, events.Nothing(char))

def Woods1(char):
  box = events.Check(char, "luck", 0)
  foot = events.Lose(char, {"sanity": 1})
  common = events.Draw(char, "common", 1)
  unique = events.Draw(char, "unique", 1)
  jewelry = events.Gain(char, {"dollars": 1})
  cond = events.Conditional(char, box, "successes", {0: foot, 1: common, 2: unique, 3: jewelry})
  open_box = events.Sequence([box, cond], char)
  return events.BinaryChoice(char, "Open the locked box?", "Yes", "No", open_box, events.Nothing(char))
def Woods2(char):
  check = events.Check(char, "sneak", -1)
  make_check = events.PassFail(char, check, events.Nothing, events.Loss(char, {"stamina":2}))
  leave = events.ForceMovement(char, "Uptown")
  return events.Sequence([make_check, leave], char)
def Woods3(char):
  check = events.Check(char, "sneak", -2)
  shotgun = events.DrawSpecific(char, "common", "Shotgun")
  fail = events.Sequence([events.Loss(char, {'stamina': 2}), events.ForceMovement(char, "Uptown")], char)
  return events.PassFail(char, check, shotgun, fail)
def Woods4(char):
  check = events.Check(char, "luck", -1)
  bushwhack1a = events.ItemChoice(char, "Choose first item to lose")
  bushwhack1b = events.DiscardSpecific(char, bushwhack1a)
  bushwhack1c = events.ItemChoice(char, "Choose second item to lose")
  bushwhack1d = events.DiscardSpecific(char, bushwhack1d)
  bushwhack2 = events.Loss(char, {"stamina": 2})
  bushwhack = events.Sequence([
    bushwhack1a,
    bushwhack1b,
    bushwhack1c,
    bushwhack1d,
    bushwhack2,
  ], char)
  return events.PassFail(char, check, events.Nothing(char), bushwhack)
def Woods5(char):
  #TODO: Check whether you have food to give to the doggy
  #prereq = events.ItemPrerequisite(char, "Food")
  prereq = events.Nothing(char)
  check = events.Check(char, "speed", -2)
  #TODO: Check whether the ally is available in the deck
  #dog = events.GainAllyIfAvailable(char, "Doggy", otherwise={"dollars": 3})
  dog = events.Nothing(char)
  give_food = events.DiscardSpecific(char, "Food")
  catch = events.PassFail(char, check, dog, events.Nothing(char))
  seq = events.Sequence([give_food, dog], char)
  choose_give_food = events.BinaryChoice(char, "Give food to the dog?", "Yes", "No", seq, catch)
  return events.PassFail(char, prereq, choose_give_food, catch)
def Woods6(char):
  #TODO: A Gate and a Monster appear
  return events.Nothing(char)
def Woods7(char):
  choice = events.MultipleChoice(char, "Which would you like to gain?", ["A skill", "2 spells", "4 clues"])
  skill = events.Draw(char, "skills", 1)
  spells = events.Draw(char, "spells", 2)
  clues = events.Gain(char, {"clues": 4})
  gain = events.Conditional(char, choice, "choice_index", {"A skill": skill, "2 spells": spells, "4 clues": clues})
  gains = events.Sequence([choice, gain], char)
  check = events.Check(char, "lore", -2)
  cond = events.PassFail(char, check, gains, events.Nothing)
  turn = events.LoseTurn(char)
  seq = events.Sequence([turn, cond], char)
  return events.BinaryChoice(char, "Share in the old wise-guy's wisdom?", "Yes", "No", seq, events.Nothing(char))

def MagickShoppe1(char):
  return events.Loss(char, {"sanity": 1})
def MagickShoppe2(char):
  #TODO: Implement "Turn the top card of one location deck face up, next player to have an enounter there draws that encounter"
  return events.Nothing(char)
def MagickShoppe3(char):
  prereq = events.AttributePrerequisite(char, "dollars", 5, "at_least")
  luck = events.Check(char, "luck", 0)
  dice = events.DiceRoll(char, 2)
  coins = events.Gain(char, {"dollars": dice})
  jackpot = events.Draw(char, "unique", 2)
  cond = events.Conditional(char, luck, "successes", {0: events.Nothing(char), 1: coins, 2: jackpot})
  box = events.BinaryChoice(char, "Buy the locked trunk?", "Yes", "No", cond, events.Nothing(char))
  return events.PassFail(prereq, box, events.Nothing(char))
def MagickShoppe4(char):
  check = events.Check(char, "lore", -1)
  curse = events.Curse(char)
  return events.PassFail(char, check, events.Nothing(char), curse)
def MagickShoppe5(char):
  return events.Gain(char, {"clues": 1})
def MagickShoppe6(char):
  check = events.Check(char, "lore", -1)
  # TODO: Implement buying at a discount
  underpriced = events.Nothing(char)
  return events.PassFail(char, check, underpriced, events.Nothing(char))
def MagickShoppe7(char):
  move = events.ForceMovement(char, "Uptown")
  san = events.Loss(char, {"sanity": 1})
  return events.Sequence([move, san], char)


def CreateEncounterCards():
  return {
      "Downtown": [
        EncounterCard("Downtown1", {"Asylum": Asylum1, "Bank": Bank1, "Square": Square1}),
        EncounterCard("Downtown2", {"Asylum": Asylum2, "Bank": Bank2, "Square": Square2}),
        EncounterCard("Downtown3", {"Asylum": Asylum3, "Bank": Bank3, "Square": Square3}),
        EncounterCard("Downtown4", {"Asylum": Asylum4, "Bank": Bank4, "Square": Square4}),
        EncounterCard("Downtown5", {"Asylum": Asylum5, "Bank": Bank5, "Square": Square5}),
        EncounterCard("Donwtown6", {"Asylum": Asylum6, "Bank": Bank6, "Square": Square6}),
        EncounterCard("Donwtown7", {"Asylum": Asylum7, "Bank": Bank7, "Square": Square7})
      ],
      "Easttown": [
        EncounterCard("Easttown1", {"Diner": Diner1, "Roadhouse": Roadhouse1, "Police": Police1}),
        EncounterCard("Easttown2", {"Diner": Diner2, "Roadhouse": Roadhouse2, "Police": Police2}),
        EncounterCard("Easttown3", {"Diner": Diner3, "Roadhouse": Roadhouse3, "Police": Police3}),
        EncounterCard("Easttown4", {"Diner": Diner4, "Roadhouse": Roadhouse4, "Police": Police4}),
        EncounterCard("Easttown5", {"Diner": Diner5, "Roadhouse": Roadhouse5, "Police": Police5}),
        EncounterCard("Easttown6", {"Diner": Diner6, "Roadhouse": Roadhouse6, "Police": Police6}),
        EncounterCard("Easttown7", {"Diner": Diner7, "Roadhouse": Roadhouse7, "Police": Police7}),
      ],
      "FrenchHill": [
        EncounterCard("FrenchHill1", {"Lodge": Lodge1}),
        EncounterCard("FrenchHill2", {"Witch": Witch2}),
      ],
      "Merchant": [
        EncounterCard("Merchant1", {"Docks": Docks1, "Unnamable": Unnamable1, "Isle": Isle1}),
        EncounterCard("Merchant2", {"Docks": Docks2, "Unnamable": Unnamable2, "Isle": Isle2}),
        EncounterCard("Merchant3", {"Docks": Docks3, "Unnamable": Unnamable3, "Isle": Isle3}),
        EncounterCard("Merchant4", {"Docks": Docks4, "Unnamable": Unnamable4, "Isle": Isle4}),
        EncounterCard("Merchant5", {"Docks": Docks5, "Unnamable": Unnamable5, "Isle": Isle5}),
        EncounterCard("Merchant6", {"Docks": Docks6, "Unnamable": Unnamable6, "Isle": Isle6}),
        EncounterCard("Merchant7", {"Docks": Docks7, "Unnamable": Unnamable7, "Isle": Isle7}),
      ],      
      "Northside": [
        EncounterCard("Northside3", {"Train": Train3}),
      ],
      "Rivertown": [
        EncounterCard("Rivertown5", {"Store": Store5}),
      ],
      "Southside": [
        EncounterCard("Southside4", {"Society": Society4}),
      ],
      "University": [
        EncounterCard("University7", {"Administration": Administration7}),
      ],
      "Uptown": [
        EncounterCard("Uptown1", {"Hospital": Hospital1, "Woods": Woods1, "MagickShoppe": MagickShoppe1}),
        EncounterCard("Uptown2", {"Hospital": Hospital2, "Woods": Woods2, "MagickShoppe": MagickShoppe2}),
        EncounterCard("Uptown3", {"Hospital": Hospital3, "Woods": Woods3, "MagickShoppe": MagickShoppe3}),
        EncounterCard("Uptown4", {"Hospital": Hospital4, "Woods": Woods4, "MagickShoppe": MagickShoppe4}),
        EncounterCard("Uptown5", {"Hospital": Hospital5, "Woods": Woods5, "MagickShoppe": MagickShoppe5}),
        EncounterCard("Uptown6", {"Hospital": Hospital6, "Woods": Woods6, "MagickShoppe": MagickShoppe6}),
        EncounterCard("Uptown7", {"Hospital": Hospital7, "Woods": Woods7, "MagickShoppe": MagickShoppe7}),
      ]
  }
