def check_and_add_keys(data_dict, keys_to_check):
    """
    Checks if the specified keys are present in the given dictionary.
    If any key is missing, it adds the key with a default value of None.

    Parameters:
    - data_dict (dict): The dictionary to check.
    - keys_to_check (list): A list of keys to check in the dictionary.

    Returns:
    - dict: The updated dictionary with missing keys added with default value None.
    """
    for key in keys_to_check:
        if key not in data_dict:
            data_dict[key] = None
            print(f"Key '{key}' was missing and has been added with default value None.")
    return data_dict