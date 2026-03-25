valid_tsf_schemas = ["1", "2.0"]
valid_sbl_schemas = ["1.0"]

print_file = False

class InvalidSchemaException(Exception):
  pass

class MalformedFileException(Exception):
  pass

def decode_tsf(tsf: str):
  schema = tsf.split(";%")[0]
  if not schema in valid_tsf_schemas:
    raise InvalidSchemaException(f"Schema {schema} isn't supported")
  if schema == "1":
    return decode_tsf_1(tsf)
  if schema == "2.0":
    return decode_tsf_2_0(tsf)

def decode_tsf_1(tsf: str):
  tsf = tsf.split(";%")
  print(len(tsf))
  if len(tsf) != 20:
    raise MalformedFileException("File is not the correct arg length")
  
  prefixes = tsf[9].split(",%")
  prefixes_split = []
  if prefixes != ['']:
    for prefix in prefixes:
      temp_list = []
      temp_list.append(prefix.split("|%")[0])
      temp_list.append(float(prefix.split("|%")[1]))
      prefixes_split.append(temp_list)
  suffixes = tsf[11].split(",%")
  suffixes_split = []
  if suffixes != ['']:
    for suffix in suffixes:
      temp_list = []
      temp_list.append(suffix.split("|%")[0])
      temp_list.append(float(suffix.split("|%")[1]))
      suffixes_split.append(temp_list)
  sprinkles = tsf[13].split(",%")
  sprinkles_split = []
  if sprinkles != ['']:
    for sprinkle in sprinkles:
      temp_list = []
      temp_list.append(sprinkle.split("|%")[0])
      temp_list.append(float(sprinkle.split("|%")[1]))
      sprinkles_split.append(temp_list)
  muffles = tsf[15].split(",%")
  muffles_split = []
  if muffles != ['']:
    for muffle in muffles:
      temp_list = []
      temp_list.append(muffle.split("|%")[0])
      temp_list.append(float(muffle.split("|%")[1]))
      muffles_split.append(temp_list)
  alt_muffles = tsf[17].split(",%")
  alt_muffles_split = []
  if alt_muffles != ['']:
    for alt_muffle in alt_muffles:
      temp_list = []
      temp_list.append(alt_muffle.split("|%")[0])
      temp_list.append(float(alt_muffle.split("|%")[1]))
      alt_muffles_split.append(temp_list)
  censors = tsf[19].split(",%")
  censors_split = []
  if censors != ['\n']:
    for censor in censors:
      temp_list = []
      temp_list.append(censor.split("|%")[0])
      temp_list.append(censor.split("|%")[1])
      censors_split.append(temp_list)
  
  if print_file:
    print(f"Schema: '{tsf[0]}'")
    print(f"Name: '{tsf[1]}'")
    print(f"Avatar: '{tsf[2]}'")
    print(f"Text Flags: '{tsf[3]}'")
    print(f"Stutter Chance: '{float(tsf[4])}'")
    print(f"Biography: '{tsf[7]}'")
    print(f"Prefixes: '{str(prefixes_split)}'")
    print(f"Suffixes: '{str(suffixes_split)}'")
    print(f"Sprinkles: '{str(sprinkles_split)}'")
    print(f"Muffles: '{str(muffles_split)}'")
    print(f"Alt Muffles: '{str(alt_muffles_split)}'")
    print(f"Censors: '{str(censors_split)}'")

  return tsf[1], tsf[2], tsf[3], tsf[4], None, tsf[7], None, None, None, None, None, str(prefixes_split), str(suffixes_split), str(sprinkles_split), str(muffles_split), str(alt_muffles_split), str(censors_split), '[]', '[]'

def decode_tsf_2_0(tsf: str):
  tsf = tsf.split(";%")
  if len(tsf) != 12:
    raise MalformedFileException("File is not the correct arg length")
  prefixes = tsf[6].split(",%")
  prefixes_split = []
  if prefixes != ['']:
    for prefix in prefixes:
      temp_list = []
      temp_list.append(prefix.split("|%")[0])
      temp_list.append(float(prefix.split("|%")[1]))
      prefixes_split.append(temp_list)
  suffixes = tsf[7].split(",%")
  suffixes_split = []
  if suffixes != ['']:
    for suffix in suffixes:
      temp_list = []
      temp_list.append(suffix.split("|%")[0])
      temp_list.append(float(suffix.split("|%")[1]))
      suffixes_split.append(temp_list)
  sprinkles = tsf[8].split(",%")
  sprinkles_split = []
  if sprinkles != ['']:
    for sprinkle in sprinkles:
      temp_list = []
      temp_list.append(sprinkle.split("|%")[0])
      temp_list.append(float(sprinkle.split("|%")[1]))
      sprinkles_split.append(temp_list)
  muffles = tsf[9].split(",%")
  muffles_split = []
  if muffles != ['']:
    for muffle in muffles:
      temp_list = []
      temp_list.append(muffle.split("|%")[0])
      temp_list.append(float(muffle.split("|%")[1]))
      muffles_split.append(temp_list)
  alt_muffles = tsf[10].split(",%")
  alt_muffles_split = []
  if alt_muffles != ['']:
    for alt_muffle in alt_muffles:
      temp_list = []
      temp_list.append(alt_muffle.split("|%")[0])
      temp_list.append(float(alt_muffle.split("|%")[1]))
      alt_muffles_split.append(temp_list)
  censors = tsf[11].split(",%")
  censors_split = []
  if censors != ['\n']:
    for censor in censors:
      temp_list = []
      temp_list.append(censor.split("|%")[0])
      temp_list.append(censor.split("|%")[1])
      censors_split.append(temp_list)
  
  if print_file:
    print(f"Schema: '{tsf[0]}'")
    print(f"Name: '{tsf[1]}'")
    print(f"Avatar: '{tsf[2]}'")
    print(f"Text Flags: '{tsf[3]}'")
    print(f"Stutter Chance: '{float(tsf[4])}'")
    print(f"Biography: '{tsf[5]}'")
    print(f"Prefixes: '{str(prefixes_split)}'")
    print(f"Suffixes: '{str(suffixes_split)}'")
    print(f"Sprinkles: '{str(sprinkles_split)}'")
    print(f"Muffles: '{str(muffles_split)}'")
    print(f"Alt Muffles: '{str(alt_muffles_split)}'")
    print(f"Censors: '{str(censors_split)}'")

  return tsf[1], tsf[2], tsf[3], tsf[4], None, tsf[5], None, None, None, None, None, str(prefixes_split), str(suffixes_split), str(sprinkles_split), str(muffles_split), str(alt_muffles_split), str(censors_split), '[]', '[]'

def decode_sbl(sbl: str):
  sbl = sbl.split(";%")
  if not sbl[0] in valid_sbl_schemas:
    raise InvalidSchemaException(f"Schema {sbl[0]} isn't supported")
  if len(sbl) != 20:
    raise MalformedFileException("File is not the correct arg length")
  try:
    prefixes = sbl[12].split(",%")
    prefixes_split = []
    if prefixes != ['']:
      for prefix in prefixes:
        temp_list = []
        temp_list.append(prefix.split("|%")[0])
        temp_list.append(float(prefix.split("|%")[1]))
        prefixes_split.append(temp_list)
    suffixes = sbl[13].split(",%")
    suffixes_split = []
    if suffixes != ['']:
      for suffix in suffixes:
        temp_list = []
        temp_list.append(suffix.split("|%")[0])
        temp_list.append(float(suffix.split("|%")[1]))
        suffixes_split.append(temp_list)
    sprinkles = sbl[14].split(",%")
    sprinkles_split = []
    if sprinkles != ['']:
      for sprinkle in sprinkles:
        temp_list = []
        temp_list.append(sprinkle.split("|%")[0])
        temp_list.append(float(sprinkle.split("|%")[1]))
        sprinkles_split.append(temp_list)
    muffles = sbl[15].split(",%")
    muffles_split = []
    if muffles != ['']:
      for muffle in muffles:
        temp_list = []
        temp_list.append(muffle.split("|%")[0])
        temp_list.append(float(muffle.split("|%")[1]))
        muffles_split.append(temp_list)
    alt_muffles = sbl[16].split(",%")
    alt_muffles_split = []
    if alt_muffles != ['']:
      for alt_muffle in alt_muffles:
        temp_list = []
        temp_list.append(alt_muffle.split("|%")[0])
        temp_list.append(float(alt_muffle.split("|%")[1]))
        alt_muffles_split.append(temp_list)
    censors = sbl[17].split(",%")
    censors_split = []
    if censors != ['']:
      for censor in censors:
        temp_list = []
        temp_list.append(censor.split("|%")[0])
        temp_list.append(censor.split("|%")[1])
        censors_split.append(temp_list)
    triggers = sbl[18].split(",%")
    triggers_split = []
    if triggers != ['']:
      for trigger in triggers:
        temp_list = []
        temp_list.append(trigger.split("|%")[0])
        temp_list.append(trigger.split("|%")[1])
        triggers_split.append(temp_list)
    alt_triggers = sbl[19].split(",%")
    alt_triggers_split = []
    if alt_triggers != ['\n']:
      for alt_trigger in alt_triggers:
        temp_list = []
        temp_list.append(alt_trigger.split("|%")[0])
        temp_list.append(alt_trigger.split("|%")[1])
        alt_triggers_split.append(temp_list)
  except Exception as e:
    raise Exception("Something went wrong")
  
  if print_file:
    print(f"Schema: {sbl[0]}")
    print(f"Name: {sbl[1]}")
    print(f"Avatar: {sbl[2]}")
    print(f"Text Flags: {sbl[3]}")
    print(f"Stutter Chance: {float(sbl[4])}")
    print(f"Pronouns: '{sbl[5]}'")
    print(f"Biography: {sbl[6]}")
    print(f"Story : {sbl[7]}")
    print(f"Fallback Prefix: {sbl[8]}")
    print(f"Fallback Suffix: {sbl[9]}")
    print(f"Fallback Muffle: {sbl[10]}")
    print(f"Fallback Alt Muffle: {sbl[11]}")
    print(f"Prefixes: {prefixes_split}")
    print(f"Suffixes: {suffixes_split}")
    print(f"Sprinkles: {sprinkles_split}")
    print(f"Muffles: {muffles_split}")
    print(f"Alt Muffles: {alt_muffles_split}")
    print(f"Censors: {censors_split}")
    print(f"Triggers: {triggers_split}")
    print(f"Alt Triggers: {alt_triggers_split}")
  return sbl[1], sbl[2], sbl[3], sbl[4], sbl[5], sbl[6], sbl[7], sbl[8], sbl[9], sbl[10], sbl[11], str(prefixes_split), str(suffixes_split), str(sprinkles_split), str(muffles_split), str(alt_muffles_split), str(censors_split), str(triggers_split), str(alt_triggers_split)

#decode_tsf(open("tfs/tsf1/Cirno_Fumo.tsf", 'r').read()) # print()
#decode_sbl(open("readable.sbl", 'r').read()) # print()