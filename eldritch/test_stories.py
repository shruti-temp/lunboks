from unittest import mock

from eldritch.test_events import EventTest
from eldritch import assets
from eldritch import characters
from eldritch import events
from eldritch import gates
from eldritch import stories

from eldritch.test_specials import mock_randint


class StoryTest(EventTest):
  def setUp(self):
    super().setUp()
    self.state.specials.extend(stories.CreateStories())
    self.state.allies.extend(assets.CreateAllies())


class DrifterStoryTest(StoryTest):
  def setUp(self):
    super().setUp()
    self.story = next(story for story in self.state.specials if story.name == "Powerful Nightmares")
    self.state.specials.remove(self.story)
    self.char.possessions.append(self.story)

  def testDontPassStory(self):
    self.state.gates.appendleft(gates.Gate("Dummy", 0, 0, "star"))
    self.state.event_stack.append(events.TakeGateTrophy(self.char, "draw"))
    self.resolve_until_done()
    self.assertListEqual(self.char.possessions, [self.story])

  def testPassStory(self):
    dreamlands = next(gate for gate in self.state.gates if gate.name == "Dreamlands")
    self.state.gates.remove(dreamlands)
    self.state.gates.appendleft(dreamlands)
    self.state.event_stack.append(events.TakeGateTrophy(self.char, "draw"))
    self.resolve_until_done()
    self.assertListEqual([p.name for p in self.char.possessions], ["Sweet Dreams"])

  def testFailStory(self):
    for target_ally in ["Dog", "Arm Wrestler", "Old Professor"]:
      for ally in self.state.allies:
        if ally.name == target_ally:
          self.char.possessions.append(ally)
          self.state.allies.remove(ally)
          break

    self.assertListEqual(
        [p.name for p in self.char.possessions],
        ["Powerful Nightmares", "Dog", "Arm Wrestler", "Old Professor"])
    self.state.event_stack.append(events.AddDoom(count=5))
    self.resolve_until_done()
    self.assertListEqual([p.name for p in self.char.possessions], ["Dog", "Living Nightmare"])

    # Discarding allies should return them to the deck, right?
    self.assertIn("Old Professor", [ally.name for ally in self.state.allies])

    self.state.event_stack.append(events.DrawSpecific(self.char, "allies", "Police Inspector"))
    self.resolve_until_done()
    self.assertListEqual([p.name for p in self.char.possessions], ["Dog", "Living Nightmare"])

    self.state.event_stack.append(events.Draw(self.char, "allies", 1))
    self.resolve_until_done()
    self.assertListEqual([p.name for p in self.char.possessions], ["Dog", "Living Nightmare"])

  def testDontFail(self):
    for target_ally in ["Dog", "Arm Wrestler", "Old Professor"]:
      for ally in self.state.allies:
        if ally.name == target_ally:
          self.char.possessions.append(ally)
          self.state.allies.remove(ally)
          break

    self.assertListEqual(
        [p.name for p in self.char.possessions],
        ["Powerful Nightmares", "Dog", "Arm Wrestler", "Old Professor"])
    self.state.event_stack.append(events.AddDoom())
    self.resolve_until_done()
    self.assertListEqual(
        [p.name for p in self.char.possessions],
        ["Powerful Nightmares", "Dog", "Arm Wrestler", "Old Professor"])
    self.state.event_stack.append(events.AddDoom(count=3))
    self.resolve_until_done()
    self.assertListEqual(
        [p.name for p in self.char.possessions],
        ["Powerful Nightmares", "Dog", "Arm Wrestler", "Old Professor"])


class NunStoryTest(StoryTest):
  def setUp(self):
    super().setUp()
    self.state.event_stack.append(events.Bless(self.char))
    self.resolve_until_done()

    self.story = next(story for story in self.state.specials if isinstance(story, stories.NunStory))
    self.state.specials.remove(self.story)
    self.char.possessions.append(self.story)
    self.gangster = characters.Gangster()
    self.gangster.place = self.state.places["Woods"]
    self.state.characters.append(self.gangster)

    self.assertEqual(self.story.tokens["clue"], 0)
    self.state.event_stack.append(events.Bless(self.gangster))
    self.resolve_until_done()
    self.assertEqual(self.story.tokens["clue"], 1)

  def testPassFromSelfBless(self):
    with mock_randint(return_value=2):
      self.advance_turn(1, "encounter")
      self.resolve_until_done()

    self.state.event_stack.append(events.Bless(self.char))
    self.resolve_until_done()
    self.assertNotIn(self.story, self.char.possessions)
    self.assertIn(self.story.results[True], [p.name for p in self.char.possessions])
    self.assertIn("Blessing", [p.name for p in self.char.possessions])
    self.assertListEqual(
        [p.name for p in self.char.possessions], ["Blessing", self.story.results[True]]
    )
    self.assertFalse(self.char.possessions[0].tokens["elder_sign"])

    self.advance_turn(2, "movement")
    with mock.patch.object(events.random, "randint", new=mock.MagicMock(return_value=1)):
      self.resolve_to_usable(0, self.story.results[True])
      self.assertEqual(self.state.turn_phase, "upkeep")
      self.assertIsInstance(self.state.event_stack[-1], events.DiceRoll)
      self.assertEqual(self.state.event_stack[-1].roll, [1])
      self.state.done_using[0] = True
      self.advance_turn(2, "movement")
      self.assertFalse(self.gangster.possessions)

  def testFail(self):
    self.state.event_stack.append(events.Curse(self.char))
    self.resolve_until_done()
    self.assertEqual(self.char.bless_curse, 0)
    self.assertIn(self.story, self.char.possessions)
    self.state.event_stack.append(events.Curse(self.char))
    self.resolve_until_done()
    self.assertEqual(self.char.bless_curse, 1)
    self.assertNotIn(self.story, self.char.possessions)
    self.assertIn(self.story.results[False], [p.name for p in self.char.possessions])
