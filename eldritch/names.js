// TODO
assetPrefix = "eldritch";
characterNames = ["Nun", "Doctor", "Archaeologist", "Gangster"];
commonNames = [
  ".38 Revolver",
  "Bullwhip",
  "Cross",
  "Dynamite",
  "Food",
  "Tommy Gun",
  "Research Materials",
];
uniqueNames = [
  "Enchanted Knife",
  "Holy Water",
  "Magic Lamp",
];
spellNames = [
  "Dread Curse",
  "Find Gate",
  "Shrivelling",
  "Voice",
  "Wither",
];
skillNames = [
  "Speed",
  "Sneak",
  "Fight",
  "Will",
  "Lore",
  "Luck",
  "Stealth",
  "Marksman",
  "Bravery",
  "Expert Occultist",
];
allyNames = [
  "Fortune Teller",
  "Traveling Salesman",
  "Police Detective",
  "Thief",
  "Brave Guy",
  "Police Inspector",
  "Arm Wrestler",
  "Visiting Painter",
  "Tough Guy",
  "Old Professor",
  "Dog",
];
abilityNames = [
  "Medicine",
];
monsterNames = [
  "Giant Insect",
  "Land Squid",
  "Cultist",
  "Tentacle Tree",
  "Dimensional Shambler",
  "Giant Worm",
  "Elder Thing",
  "Flame Matrix",
  "Subterranean Flier",
  "Formless Spawn",
  "Ghost",
  "Ghoul",
  "Furry Beast",
  "Haunter",
  "High Priest",
  "Hound",
  "Maniac",
  "Pinata",
  "Dream Flier",
  "Giant Amoeba",
  "Octopoid",
  "Vampire",
  "Warlock",
  "Witch",
  "Zombie",
];
otherWorlds = [
  "Abyss",
  "Another Dimension",
  "City",
  "Great Hall",
  "Plateau",
  "Sunken City",
  "Dreamlands",
  "Pluto",
];
gateNames = [];
for (let world of otherWorlds) {
  gateNames.push("Gate " + world);
}
extraNames = ["Clue"];
assetNames = ["board"].concat(characterNames).concat(commonNames).concat(uniqueNames).concat(spellNames).concat(skillNames).concat(allyNames).concat(abilityNames).concat(monsterNames).concat(otherWorlds).concat(gateNames).concat(extraNames);
serverNames = {};
for (let name of assetNames) {
  if (name == "board") {
    continue;
  }
  serverNames[name] = name;
}
gateCards = [];
for (let i = 1; i <= 50; i++) {
  gateCards.push("gate" + i);
}
mythosCards = [];
for (let i = 1; i <= 67; i++) {
  gateCards.push("mythos" + i);
}
neighborhoodNames = [
  "Northside",
  "Downtown",
  "Easttown",
  "Rivertown",
  "FrenchHill",
  "Southside",
  "Uptown",
  "University",
  "Merchant",
];
encounterCardNames = [];
for (let n of neighborhoodNames) {
  for (let i = 1; i <= 7; i++) {
    encounterCardNames.push(n + i);
  }
}
assetNames = assetNames.concat(encounterCardNames).concat(gateCards).concat(mythosCards);
