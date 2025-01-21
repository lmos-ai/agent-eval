import re

def match_entity_in_line(entity: str, line: str) -> bool:
    """
    Checks whether `entity` matches in a single line of text (`line`),
    ignoring case differences but accounting for numeric equivalences,
    optional trailing unit text, currency mismatch scenarios, etc.

    :param entity: The extracted entity (string) from a response, e.g. "23.00", "ram", "$23"
    :param line: A single line from the source text in which we want to verify the entity exists
    :return: True if matched in this line under the defined rules, otherwise False.
    """

    # Normalize case
    ent = entity.strip().lower()
    src_line = line.lower()

    # 1) If entity has no digits, do a direct substring check (case-insensitive).
    if not re.search(r'\d', ent):
        return ent in src_line

    # 2) Check if the entity looks like a currency (leading $/£/€/¥ etc.).
    currency_symbols_pattern = r'^[\$€£¥]+'
    has_currency_symbol = re.match(currency_symbols_pattern, ent) is not None

    # If the entity has a currency symbol, ensure the same symbol is present somewhere in line.
    # (This is a naive check—depending on strictness, you might want to look near the numeric.)
    if has_currency_symbol:
        symbol = re.match(currency_symbols_pattern, ent).group(0)  # e.g. '$'
        if symbol not in src_line:
            return False

    # 3) Extract the numeric part, removing leading currency symbols and trailing unit text.
    #    e.g. "$23.00" -> "23.00"; "45.7 kg" -> "45.7"
    ent_stripped = re.sub(r'^[^\d]+', '', ent)        # remove leading non-digit chars
    ent_stripped = re.sub(r'[^0-9.]+$', '', ent_stripped)  # remove trailing non-numeric chars

    # Try to parse this as float
    try:
        ent_value = float(ent_stripped)
    except ValueError:
        # fallback: if can't parse, do direct substring check
        return ent in src_line

    # 4) Look for numeric substrings in the line. Compare each to `ent_value`.
    numeric_pattern = re.compile(r'\d+(\.\d+)?')  # e.g. 12, 12.3, etc.
    for match in numeric_pattern.finditer(src_line):
        num_str = match.group(0)
        try:
            src_num_val = float(num_str)
        except ValueError:
            continue

        # Compare floats (account for "23" vs "23.0" etc.)
        if abs(ent_value - src_num_val) < 1e-9:
            # If the entity had a currency symbol, check that symbol is nearby (optional strictness).
            if has_currency_symbol:
                start_idx = match.start()
                # e.g., look a few chars before the matched number
                snippet_before = src_line[max(0, start_idx-3):start_idx]
                if symbol in snippet_before:
                    return True
                else:
                    continue
            else:
                return True

    return False


def check_entity_in_source(entity: str, source_lines: list[str]) -> bool:
    """
    Given an entity (string) and a list of source lines (strings), returns
    True if the entity matches in ANY of those lines, else False.
    """
    for line in source_lines:
        if match_entity_in_line(entity, line):
            return True
    return False