"""Identifier for various things in the DDM."""
import re
from typing import Any, cast, List, Type


class Identifier(str):
    """An identifier.

    An Identifier is a string of any of the following forms:

    1. party:<namespace>:<name>
    2. party_collection:<namespace>:<name>
    3. site:<namespace>:<name>
    4. asset:<namespace>:<name>:<site_namespace>:<site_name>
    5. asset_collection:<namespace>:<name>
    6. result:<id_hash>

    This class also accepts a single asterisk an an identifier, as it
    is used as a wildcard in rules.

    See the Terminology section of the documentation for details.
    """
    def __new__(cls: Type['Identifier'], seq: Any) -> 'Identifier':
        """Create an Identifier.

        Args:
            seq: Contents, will be converted to a string using str(),
            then used as the identifier.

        Raises:
            ValueError: If str(seq) is not a valid identifier.
        """
        data = str(seq)

        if data != '*':
            parts = data.split(':')
            if parts[0] not in cls._kinds:
                raise ValueError(f'Invalid identifier kind {parts[0]}')

            if len(parts) != cls._lengths[parts[0]]:
                raise ValueError(f'Too few or too many parts in {data}')

            for part in parts:
                if not cls._part_regex.match(part):
                    raise ValueError(f'Invalid identifier part {part}')

        return str.__new__(cls, seq)        # type: ignore

    @classmethod
    def from_id_hash(cls, id_hash: str) -> 'Identifier':
        """Creates an Identifier from an id hash.

        Args:
            id_hash: A hash of a workflow that created this result.

        Returns:
            The Identifier for the workflow result.
        """
        return cls(f'result:{id_hash}')

    @property
    def parts(self) -> List[str]:
        """Return the list of parts of this identifier."""
        return self.split(':')

    def namespace(self) -> str:
        """Returns the namespace this asset is in.

        Returns:
            The namespace.

        Raises:
            RuntimeError: If this is not a primary asset.
        """
        if self.parts[0] == 'result':
            raise RuntimeError('Results do not have a namespace')
        return self.parts[1]

    def location(self) -> 'Identifier':
        """Returns the d of the site storing this asset.

        Returns:
            A site name.

        Raises:
            RuntimeError: If this is not a concrete asset.
        """
        if self.parts[0] != 'asset':
            raise RuntimeError(
                    'Location requested of non-concrete asset {self}')
        return Identifier(f'site:{self.parts[3]}:{self.parts[4]}')

    _kinds = (
        'party', 'party_collection', 'site', 'asset', 'asset_collection',
        'result')

    _lengths = {
            'party': 3, 'party_collection': 3, 'site': 3, 'asset': 5,
            'asset_collection': 3, 'result': 2}

    _part_regex = re.compile('[a-zA-Z0-9_.-]*')
