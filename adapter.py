from casbin import persist
from typing import Tuple, List

class ArrayAdapter(persist.Adapter):
    """Read-Only Array adapter for Cabsin.
    It can load policy from an array of tuples

    example:
    [
        ('p', 'alice', 'data1', 'read'),
        ('g', 'alice', 'data1_admin')
    ]
    """
    def __init__(self, policy_rules: List[Tuple]):
        self.rules = policy_rules

    def load_policy(self, model):
        for rule in self.rules:
            persist.load_policy_line(', '.join(rule), model)
