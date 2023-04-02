import abc
from eldritch import events
from eldritch import assets
from eldritch import characters
from eldritch import values


class StoryResult(assets.Card, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def __init__(self, name, passive_bonuses=None):
    super().__init__(
        name, None, "specials", active_bonuses={}, passive_bonuses=passive_bonuses or {}
    )

  def get_trigger(self, event, owner, state):
    if isinstance(event, events.KeepDrawn) and event.drawn == [self]:
      return self.get_in_play_event(owner)
    return None

  def get_in_play_event(self, owner: characters.Character):
    return events.Nothing()


class Story(assets.Card, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def __init__(self, name, pass_result, fail_result):
    super().__init__(name, None, "specials", active_bonuses={}, passive_bonuses={})
    self.results = {True: pass_result, False: fail_result}

  def advance_story(self, character, pass_story):
    return events.Sequence([
        events.DiscardSpecific(character, [self]),
        events.DrawSpecific(character, "specials", self.results[pass_story])
    ])


class DrifterStoryPass(StoryResult):
  def __init__(self):
    super().__init__("Sweet Dreams", passive_bonuses={"speed": 1, "luck": 1})


class DrifterStoryFail(StoryResult):
  def __init__(self):
    super().__init__("Living Nightmare")

  def get_in_play_event(self, owner: characters.Character):
    allies = [
        ally
        for ally in owner.possessions
        if getattr(ally, "deck", None) == "allies" and ally.name != "Dog"
    ]
    return events.DiscardSpecific(owner, allies)

  def get_interrupt(self, event, owner, state):
    if not getattr(event, "character", None) == owner:
      return
    if (
        (isinstance(event, events.KeepDrawn)
         and (getattr(event.drawn, "deck", None) == "allies"))
        or (isinstance(event, (events.DrawNamed, events.DrawItems)) and event.deck == "allies")
    ):
      return events.CancelEvent(event)
    return


class DrifterStory(Story):
  def __init__(self):
    super().__init__(
        "Powerful Nightmares", "Sweet Dreams", "Living Nightmare"
    )

  def get_trigger(self, event, owner, state):
    if (
        isinstance(event, events.TakeGateTrophy)
        and (event.character == owner)
        and (event.gate.name == "Dreamlands")
    ):
      return self.advance_story(owner, True)
    elif (
        isinstance(event, events.AddDoom)
        and state.ancient_one.doom >= 5
    ):
      return self.advance_story(owner, False)
    return super().get_trigger(event, owner, state)

  def get_pass_asset(self) -> StoryResult:
    return DrifterStoryPass()

  def get_fail_asset(self) -> StoryResult:
    return DrifterStoryFail()


class NunStoryPass(StoryResult):
  def __init__(self):
    super().__init__("Fear No Evil")

  def get_interrupt(self, event, owner, state):
    if isinstance(event, events.Curse) and event.character == owner:
      return events.CancelEvent(event)

  def get_usable_trigger(self, event, owner, state):
    if isinstance(event, events.DiceRoll):
      # TODO: Allow user to select a die to reroll
      to_reroll = events.Nothing()
      return events.Sequence([
          events.Nothing(),
          events.ExhaustAsset(owner, self),
          events.RerollSpecific(state.event_stack[-2].character, state.event_stack[-2], to_reroll),
      ], owner)

  def get_in_play_event(self, owner: characters.Character):
    return events.Bless(owner)


class NunStoryFail(StoryResult):
  def __init__(self):
    super().__init__("I Shall Not Want")

  def get_in_play_event(self, owner: characters.Character):
    return events.Sequence([
        events.DiscardNamed(owner, "Curse"),
        events.Bless(owner)
    ], owner)


class NunStory(Story):
  def __init__(self):
    super().__init__("He Is My Shepherd", "Fear No Evil", "I Shall Not Want")
    self.max_tokens["clue"] = 2

  def get_max_token_event(self, token_type, owner):
    if token_type == "clue":
      return self.advance_story(owner, True)
    return events.Nothing()

  def get_trigger(self, event, owner, state):
    if isinstance(event, events.Bless):
      return events.AddToken(self, "clue")
    if (
        isinstance(event, events.KeepDrawn)
        and (event.character == owner)
        and values.ItemNameCount(owner, "Curse").value(state)
    ):
      return self.advance_story(owner, False)
    return super().get_trigger(event, owner, state)


def CreateStories():
  return [
      DrifterStoryPass(), DrifterStoryFail(), DrifterStory()
  ]
