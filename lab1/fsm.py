from typing import List, Dict
from queue import SimpleQueue

START_STATE = '0'
FINAL_STATE = 'f'


def check_brackets(regexp: str) -> bool:
    group_deep = 0
    for i in range(len(regexp)):
        if regexp[i] == '(':
            group_deep += 1
        elif regexp[i] == ')':
            if group_deep == 0:
                return False
            group_deep -= 1

    return group_deep == 0


def remove_brackets(regexp: str) -> str:
    if regexp[0] == '(' and regexp[-1] == ')':
        if check_brackets(regexp[1:-1]):
            return remove_brackets(regexp[1:-1])
    return regexp


def split_concatenations(regexp: str) -> List[str]:
    groups = []
    group_deep = 0
    left_idx = 0

    for i in range(len(regexp)):
        if regexp[i] == '(':
            if group_deep == 0:
                if i - left_idx > 1:
                    groups.extend([x for x in regexp[left_idx + 1:i]])
                left_idx = i
            group_deep += 1
        elif regexp[i] == ')':
            if group_deep == 0:
                raise Exception("Wrong regexp")
            elif group_deep == 1:
                groups.append(regexp[left_idx + 1:i])
                left_idx = i
            group_deep -= 1

    if group_deep != 0:
        raise Exception("Wrong regexp")
    if left_idx == 0:
        groups.extend([x for x in regexp])
    elif left_idx != len(regexp) - 1:
        groups.extend([x for x in regexp[left_idx + 1:len(regexp)]])

    for i in range(len(groups)):
        if groups[i] == '*':
            groups[i-1] = f'({groups[i-1]})*'
            groups[i] = ''

    for i in range(len(groups)):
        if groups[i] == '|':
            j = i - 1
            while groups[j] == '':
                j -= 1
            groups[i] = f'{groups[j]}|{groups[i+1]}'
            groups[j] = ''
            groups[i+1] = ''

    return [remove_brackets(group) for group in groups if len(group) > 0]


def split_unions(regexp: str) -> List[str]:
    groups = []
    group_deep = 0
    left_idx = 0

    for i in range(len(regexp)):
        if regexp[i] == '(':
            group_deep += 1
        elif regexp[i] == ')':
            if group_deep == 0:
                raise Exception("Wrong regexp")
            group_deep -= 1
        elif regexp[i] == '|' and group_deep == 0:
            groups.append(regexp[left_idx:i])
            left_idx = i+1

    if group_deep != 0:
        raise Exception("Wrong regexp")
    if left_idx == 0:
        groups.append(regexp)
    elif left_idx != len(regexp):
        groups.append(regexp[left_idx:len(regexp)])

    for group in groups:
        if group[-1] == '*':
            group = f'({group[0:-1]})*'

    return [remove_brackets(group) for group in groups]


class FiniteState(object):
    def __init__(self, mark_num, is_terminal=False, is_start=False):
        self.mark = f'q{mark_num}'
        self.is_start = is_start
        self.is_terminal = is_terminal

    def __str__(self):
        return self.mark

    def extract_number(self) -> int:
        return int(self.mark.replace('q', ''))


class FiniteStateRule(object):
    def __init__(self, start_state: FiniteState, final_state: FiniteState, rule: str):
        self.start_state = start_state
        self.final_state = final_state
        self.rule = rule

    def __str__(self):
        return f"{self.start_state.mark} -- {self.rule} --> {self.final_state.mark}"

    def __eq__(self, other):
        return self.rule == other.rule and self.final_state == other.final_state

    def is_simple(self):
        return len(self.rule) < 2

    def split_rule(self, last_state_num: int):
        # return new last state and new rules
        new_last_state_num = last_state_num
        new_rules = []
        groups = split_unions(self.rule)
        if len(groups) > 1:
            new_rules = [FiniteStateRule(self.start_state, self.final_state, rule) for rule in groups]
            return new_last_state_num, new_rules
        groups = split_concatenations(self.rule)
        if len(groups) > 1:
            # make chain rules
            start_state = self.start_state
            for group in groups:
                new_last_state_num += 1
                new_last_state_obj = FiniteState(new_last_state_num)
                new_rules.append(FiniteStateRule(start_state, new_last_state_obj, group))
                start_state = new_last_state_obj
            new_rules[-1].final_state = self.final_state
            return new_last_state_num - 1, new_rules
        if self.rule[-1] == '*':
            rule = remove_brackets(self.rule[0:-1])
            # make loop rules
            new_last_state_num += 1
            new_last_state_obj = FiniteState(new_last_state_num)
            new_rules.append(FiniteStateRule(self.start_state, new_last_state_obj, ''))
            new_rules.append(FiniteStateRule(new_last_state_obj, new_last_state_obj, rule))
            new_rules.append(FiniteStateRule(new_last_state_obj, self.final_state, ''))
            return new_last_state_num, new_rules
        raise Exception(f'Can not parse regexp: {self.rule}')


class FiniteStateMachine(object):
    def __init__(self, regexp: str):
        self.last_state = 0
        start_state = FiniteState(START_STATE, is_start=True)
        final_state = FiniteState(FINAL_STATE, is_terminal=True)
        self.states = [start_state, final_state]
        self.rules = [FiniteStateRule(start_state, final_state, regexp)]

    def sort_rules(self):
        self.rules = sorted(self.rules, key=lambda x: x.start_state.mark)

    def split_rules(self):
        """Method split rules into simple one, turn regexp into NFA with eps moves"""
        complete = False
        while not complete:
            complete = True
            new_rules = []
            for rule in self.rules:
                if not rule.is_simple():
                    complete = False
                    self.last_state, splitted_rules = rule.split_rule(self.last_state)
                    new_rules.extend(splitted_rules)
                else:
                    new_rules.extend([rule])
            self.rules = new_rules

    def get_rules_for_state_start(self, state):
        return [rule for rule in self.rules if rule.start_state == state]

    def get_rules_for_state_finish(self, state):
        return [rule for rule in self.rules if rule.final_state == state]

    def get_input_states(self, state):
        return [rule.start_state for rule in self.get_rules_for_state_start(state)]

    def get_output_states(self, state):
        return [rule.final_state for rule in self.get_rules_for_state_finish(state)]

    def check_state_eq(self, state1, state2):
        return self.get_rules_for_state_start(state1) == self.get_rules_for_state_start(state2)

    def delete_state(self, state):
        self.states.remove(state)
        self.rules = [rule for rule in self.rules if rule.start_state != state]

    def merge_states(self, state1, state2):
        for rule in self.rules:
            if rule.final_state == state2:
                rule.final_state = state1
        self.delete_state(state2)

    def delete_duplicated_state(self):
        out_rules = [[rule for rule in self.get_rules_for_state_start(state)] for state in self.states]
        not_deleted = [1 for state in self.states]

        for i in range(len(self.states)-1):
            if not_deleted[i]:
                for j in range(i+1, len(self.states)):
                    if not_deleted[j] and out_rules[i] == out_rules[j]:
                        self.merge_states(self.states[i], self.states[j])
                        not_deleted[j] = 0

    def fill_states(self):
        for rule in self.rules:
            if rule.start_state not in self.states:
                self.states.append(rule.start_state)
            if rule.final_state not in self.states:
                self.states.append(rule.final_state)

    def skip_eps_moves(self, state):
        states_queue = SimpleQueue()
        states_queue.put(state)
        rules_to_add = []
        while not states_queue.empty():
            next_state = states_queue.get()
            next_rules = self.get_rules_for_state_start(next_state)
            for rule in next_rules:
                if rule.rule:
                    rules_to_add.append(rule)
                else:
                    rules_to_add.extend(self.skip_eps_moves(rule.final_state))
                    if rule.final_state.is_terminal:
                        state.is_terminal = True
        return [FiniteStateRule(state, rule.final_state, rule.rule) for rule in rules_to_add]

    def remove_eps_moves(self):
        new_rules = []
        for state in self.states:
            new_rules.extend(self.skip_eps_moves(state))
        self.rules = new_rules
