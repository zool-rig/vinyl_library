from copy import copy
from random import choice
from typing import List, Optional

from frontend.lib.vinyl import Vinyl


class FavoriteVinylGenerator(object):
    def __init__(self, vinyls):
        self.vinyls = vinyls
        self.chosen_vinyls = [None, None]
        self.round_count = len(self.vinyls) - 1
        self.round = 0

    def next(self, next_round: bool = True) -> List[Optional[Vinyl]]:
        if len(self.vinyls) <= 2:
            self.chosen_vinyls = copy(self.vinyls)
        else:
            first = choice(self.vinyls)
            while first in self.chosen_vinyls:
                first = choice(self.vinyls)
            self.chosen_vinyls[0] = first
            second = choice(self.vinyls)
            while second in self.chosen_vinyls:
                second = choice(self.vinyls)
            self.chosen_vinyls[1] = second
        if next_round:
            self.round += 1
        return self.chosen_vinyls

    def select(self, vinyl: Vinyl) -> None:
        for chosen_vinyl in self.chosen_vinyls:
            if chosen_vinyl != vinyl:
                self.vinyls.remove(chosen_vinyl)

    def is_last_round(self) -> bool:
        return len(self.vinyls) == 1

    @property
    def favorite_vinyl(self) -> Optional[Vinyl]:
        return self.vinyls[0] if self.is_last_round() else None
