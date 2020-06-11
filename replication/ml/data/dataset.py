import _bisect

import torch
import torch.utils.data
from typing import List, Tuple

from replication.preprocess.cursor import CursorEntry
from replication.preprocess.moves import TrackPadEntry
from replication.preprocess.user import User


class TouchDataset(torch.utils.data.Dataset):
    valid_user_tasks: List[Tuple[int]]
    total_combinations: int

    def __init__(self, users: List[User]):
        self.valid_user_tasks = []
        self.valid_user_combinations = []
        self.total_combinations = 0
        for user in users:
            stressed_count = len(user.stressed_condition.tasks)
            unstressed_count = len(user.unstressed_condition.tasks)
            self.valid_user_tasks += [(stressed_count, unstressed_count)]
            self.total_combinations += stressed_count + unstressed_count
        self.users = users

    @staticmethod
    def cursor_to_list(entries: List[CursorEntry]):
        x = []
        y = []
        t = []
        for entry in entries:
            x += [entry.x]
            y += [entry.y]
            t += [1.0 if entry.valid else 0.0]
        return x, y, t

    def __getitem__(self, index):
        found = False
        for user_id, user in enumerate(self.users):
            for label, condition in zip([1, 0], [user.stressed_condition, user.unstressed_condition]):
                task_count = len(condition.tasks)
                if index < task_count:
                    found = True
                    break
                else:
                    index -= task_count
            if found:
                break
        tensor = torch.Tensor(condition.tasks[index].data_list)
        return (self.users[user_id].name, condition.tasks[index].per), (label, tensor)

    def __len__(self):
        return self.total_combinations
