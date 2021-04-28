import random as rnd
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

import attr

from headfake.field import Field


@attr.s(kw_only=True)
class IdGenerator(ABC):
    """
    Base IdGenerator class which handles the generation of zero-padded values for ID fields. The key function is 'select_id'
    which returns a zero-filled ID number to the specified length.

    Args:
        length (int): Length of zero-padded ID value
        min_value (int): Minimum value/start point for ID value (default=1)
    """
    length: int = attr.ib()
    min_value: int = attr.ib(default=1)
    name: Optional[str] = attr.ib(default=uuid.uuid4())

    def select_id(self):
        val = self._select_number()
        return str(val).zfill(self.length)

    @abstractmethod
    def _select_number(self):
        """
        Generates the integer value used to create the ID in the 'select_id' function.
        :return:
        """
        pass


@attr.s(kw_only=True)
class IncrementIdGenerator(IdGenerator):
    """
    Incremental ID generator, increments by 1 each time an ID is generated.
    """
    current_no: int = attr.ib()

    @current_no.default
    def _default_current_no(self):
        return self.min_value

    def _select_number(self):
        if len(str(self.current_no)) > self.length:
            raise ValueError("next number is greater than length")

        val = self.current_no
        self.current_no += 1

        return val


@attr.s
class RandomIdGenerator(IdGenerator):
    """
    Base random ID generator. Sets up a maximum value.
    """
    max_value: int = attr.ib()

    @max_value.default
    def _default_max_value(self):
        return int("9" * self.length)


@attr.s
class RandomNoReuseIdGenerator(RandomIdGenerator):
    """
    Random unique ID generator which retains the used IDs so it does not reuse them.
    """
    _used_values: List[id] = attr.ib(factory=list)

    def _select_number(self):
        val = rnd.randrange(self.min_value, self.max_value)
        if val in self._used_values:
            return self._select_number()

        self._used_values.append(val)

        return val


@attr.s
class RandomReuseIdGenerator(RandomIdGenerator):
    """
    Random non-unique ID generator. Simply generates a random number between the min_value and max_value.
    """

    def _select_number(self):
        val = rnd.randrange(self.min_value, self.max_value)
        return str(val).zfill(self.length)


@attr.s(kw_only=True)
class IdField(Field):
    """
    Field which generates ID values using a provided IdGenerator class.

    Args:
        prefix: Prefix prepended to generated ID
        suffix: Suffix appended to generated ID
        generator: IdGenerator class name to use (defaults to [IncrementIdGenerator](#headfakefieldcoreincrementidgenerator)
    """
    prefix: str = attr.ib(default="")
    suffix: str = attr.ib(default="")
    generator: IdGenerator = attr.ib(default=IncrementIdGenerator(length=3))

    def _next_value(self, row):
        val = self.generator.select_id()

        return self.prefix + val + self.suffix