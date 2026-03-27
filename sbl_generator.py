name = input("Name: ")
avatar = input("Avatar: ")
biography = input("Biography: ")
story = input("Story: ")
stutter_chance = input("Stutter Chance (float 0-100, max 10 decimal spaces):\n")

do_pronouns = input("Set pronouns? [y/N]: ")
if do_pronouns.lower().startswith("y"):
  do_pronouns = True
else:
  do_pronouns = False

if do_pronouns:
  prounoun1 = input("Pronouns (subject) (ie \"i\", \"it\", \"pup\"):\n")
  prounoun2 = input("Pronouns (object) (ie \"me\", \"it\", \"pup\"):\n")
  prounoun3 = input("Pronouns (possessive adjective) (ie \"my\", \"its\", \"pups\"):\n")
  prounoun4 = input("Pronouns (possessive pronount) (ie \"mine\", \"its\", \"pups\"):\n")
  prounoun5 = input("Pronouns (reflexive) (ie \"myself\", \"itself\", \"pupself\"):\n")
  prounoun6 = input("Pronouns (perspective) (0 = first person (\"I am me\"), 1 = third person (\"It is itself\"), 2 = first person plural (\"We are ourselves\")):\n")
  pronouns = f"{prounoun1},%{prounoun2},%{prounoun3},%{prounoun4},%{prounoun5},%{prounoun6}"
else:
  pronouns = ""

fallback_prefix = input("Fallback Prefix: ")
fallback_suffix = input("Fallback Suffix: ")
fallback_muffle = input("Fallback Muffle: ")
fallback_alt_muffle = input("Fallback Alt Muffle: ")

prefixes = ""
first_prefix = True
while True:
  add_prefix = input("Add Prefix? [y/N]: ")
  if add_prefix.lower().startswith("y"):
    add_prefix = True
  else:
    add_prefix = False
    break
  prefix = input("Prefix: ")
  chance = input("Chance (float 0-100, max 10 decimal spaces): ")
  if first_prefix:
    prefixes += f"{prefix}|%{chance}"
    first_prefix = False
  else:
    prefixes += f",%{prefix}|%{chance}"

suffixes = ""
first_suffix = True
while True:
  add_suffix = input("Add Suffix? [y/N]: ")
  if add_suffix.lower().startswith("y"):
    add_suffix = True
  else:
    add_suffix = False
    break
  suffix = input("Suffix: ")
  chance = input("Chance (float 0-100, max 10 decimal spaces): ")
  if first_suffix:
    suffixes += f"{suffix}|%{chance}"
    first_suffix = False
  else:
    suffixes += f",%{suffix}|%{chance}"

sprinkles = ""
first_sprinkle = True
while True:
  add_sprinkle = input("Add Sprinkle? [y/N]: ")
  if add_sprinkle.lower().startswith("y"):
    add_sprinkle = True
  else:
    add_sprinkle = False
    break
  sprinkle = input("Sprinkle: ")
  chance = input("Chance (float 0-100, max 10 decimal spaces): ")
  if first_sprinkle:
    sprinkles += f"{sprinkle}|%{chance}"
    first_sprinkle = False
  else:
    sprinkles += f",%{sprinkle}|%{chance}"

muffles = ""
first_muffle = True
while True:
  add_muffle = input("Add Muffle? [y/N]: ")
  if add_muffle.lower().startswith("y"):
    add_muffle = True
  else:
    add_muffle = False
    break
  muffle = input("Muffle: ")
  chance = input("Chance (float 0-100, max 10 decimal spaces): ")
  if first_muffle:
    muffles += f"{muffle}|%{chance}"
    first_muffle = False
  else:
    muffles += f",%{muffle}|%{chance}"

alt_muffles = ""
first_alt_muffle = True
while True:
  add_alt_muffle = input("Add Alt Muffle? [y/N]: ")
  if add_alt_muffle.lower().startswith("y"):
    add_alt_muffle = True
  else:
    add_alt_muffle = False
    break
  alt_muffle = input("Alt Muffle: ")
  chance = input("Chance (float 0-100, max 10 decimal spaces): ")
  if first_alt_muffle:
    alt_muffles += f"{alt_muffle}|%{chance}"
    first_alt_muffle = False
  else:
    alt_muffles += f",%{alt_muffle}|%{chance}"

censors = ""
first_censor = True
while True:
  add_censor = input("Add Censor? [y/N]: ")
  if add_censor.lower().startswith("y"):
    add_censor = True
  else:
    add_censor = False
    break
  censor = input("Censor: ")
  chance = input("Replacement: ")
  if first_censor:
    censors += f"{censor}|%{chance}"
    first_censor = False
  else:
    censors += f",%{censor}|%{chance}"

triggers = ""
first_trigger = True
while True:
  add_trigger = input("Add Trigger? [y/N]: ")
  if add_trigger.lower().startswith("y"):
    add_trigger = True
  else:
    add_trigger = False
    break
  trigger = input("Trigger: ")
  chance = input("Replacement: ")
  if first_trigger:
    triggers += f"{trigger}|%{chance}"
    first_trigger = False
  else:
    triggers += f",%{trigger}|%{chance}"

alt_triggers = ""
first_alt_trigger = True
while True:
  add_alt_trigger = input("Add Alt Trigger? [y/N]: ")
  if add_alt_trigger.lower().startswith("y"):
    add_alt_trigger = True
  else:
    add_alt_trigger = False
    break
  alt_trigger = input("Alt Trigger: ")
  chance = input("Replacement: ")
  if first_alt_trigger:
    alt_triggers += f"{alt_trigger}|%{chance}"
    first_alt_trigger = False
  else:
    alt_triggers += f",%{alt_trigger}|%{chance}"

with open(f"{name}.sbl", 'w') as f:
  f.write(f"""1.0;%{name};%{avatar};%0;%{stutter_chance};%{pronouns};%{biography};%{story};%{fallback_prefix};%{fallback_suffix};%{fallback_muffle};%{fallback_alt_muffle};%{prefixes};%{suffixes};%{sprinkles};%{muffles};%{alt_muffles};%{censors};%{triggers};%{alt_triggers}""")