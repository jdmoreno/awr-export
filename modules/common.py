import pandas as pd


none_type = type(None)


def str_to_float(str_num):
    tmp_str_num = str_num.replace(" (mins)", "")  # Remove '(mins)'
    tmp_str_num = tmp_str_num.replace(",", "")  # Remove ','
    return float(tmp_str_num)


def populate_kv_lists(df, key_list, value_list, index):
    # print(f"Key {df[index]} - type {df[index]}")
    # print(f"Value {df[index+1]} - type {df[index+1]}")
    key = df[index].replace(":", "").replace("%", "").strip()
    if type(df[index + 1]) is float:
        value = df[index + 1]
    else:
        value = float(df[index + 1][0:6])
    # print(f"Key {key} - Value {value}")
    key_list.append(key)
    value_list.append(value)


def at(index: str, column: str, dataframe: pd.DataFrame) -> object:
    try:
        item = dataframe.at[index, column]
    except (KeyError, ValueError):
        item = None
    return item
