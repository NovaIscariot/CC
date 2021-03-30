from typing import List, Dict

SPACES = [' ', '\t']


def delete_spaces(regexp: str) -> str:
    return ''.join([x for x in regexp if x not in SPACES])


def check_ka_is_complete(ka: Dict) -> bool:
    for item in ka:
        if len(ka["rule"]) > 1:
            return False
    return True


# ex for ka: (xy*|ab|(x|a*))(x|y*)
def regexp_to_ka(regexp: str) -> Dict:
    nka = {"q0": {"dest": "qf", "rule": regexp}}
    while not check_ka_is_complete(nka):
        pass
    return nka
