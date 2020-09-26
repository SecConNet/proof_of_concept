"""Central registry of remote-accessible things."""
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from proof_of_concept.definitions import (
        IAssetStore, ILocalWorkflowRunner, IPolicyServer, PartyDescription,
        RegisteredObject, RegistryUpdate, SiteDescription)
from proof_of_concept.replication import (
        CanonicalStore, ReplicableArchive, ReplicationServer, ReplicaUpdate)


_ReplicatedClass = TypeVar('_ReplicatedClass', bound=RegisteredObject)


class Registry:
    """Global registry of remote-accessible things.

    Registers runners, stores, and assets. In a real system, runners
    and stores would be identified by a URL, and use the DNS to
    resolve. For now the registry helps with this.
    """
    def __init__(self) -> None:
        """Create a new registry."""
        self._asset_locations = dict()           # type: Dict[str, str]

        archive = ReplicableArchive[RegisteredObject]()
        self._store = CanonicalStore[RegisteredObject](archive)
        self.replication_server = ReplicationServer[RegisteredObject](
                archive, 1.0)

    def register_party(
            self, description: PartyDescription) -> None:
        """Register a party with the DDM.

        Args:
            description: A description of the party
        """
        if self._in_store(PartyDescription, 'name', description.name):
            raise RuntimeError(
                    f'There is already a party called {description.name}')

        self._store.insert(description)

    def register_site(self, description: SiteDescription) -> None:
        """Register a Site with the Registry.

        Args:
            description: Description of the site.

        """
        if self._in_store(SiteDescription, 'name', description.name):
            raise RuntimeError(
                    f'There is already a site called {description.name}')

        owner = self._get_object(
                PartyDescription, 'name', description.owner_name)
        if owner is None:
            raise RuntimeError(f'Party {description.owner_name} not found')

        admin = self._get_object(
                PartyDescription, 'name', description.admin_name)
        if admin is None:
            raise RuntimeError(f'Party {description.admin_name} not found')

        self._store.insert(description)

    def register_asset(self, asset_id: str, site_name: str) -> None:
        """Register an Asset with the Registry.

        Args:
            asset_id: The id of the asset to register.
            site_name: Name of the site where it can be found.
        """
        if asset_id in self._asset_locations:
            raise RuntimeError('There is already an asset with this name')
        self._asset_locations[asset_id] = site_name

    def get_asset_location(self, asset_id: str) -> str:
        """Returns the name of the site this asset is in.

        Args:
            asset_id: ID of the asset to find.

        Return:
            The site it can be found at.

        Raises:
            KeyError: If no asset with the given id is registered.
        """
        return self._asset_locations[asset_id]

    def _get_object(
            self, typ: Type[_ReplicatedClass], attr_name: str, value: Any
            ) -> Optional[_ReplicatedClass]:
        """Returns an object from the store.

        Searches the store for an object of type `typ` that has value
        `value` for its attribute named `attr_name`. If there are
        multiple such objects, one is returned at random.

        Args:
            typ: Type of object to consider, subclass of
                RegisteredObject.
            attr_name: Name of the attribute on that object to check.
            value: Value that the attribute must have.

        Returns:
            The object, if found, or None if no object was found.

        Raises:
            AttributeError if an object of type `typ` is encountered
                in the store which does not have an attribute named
                `attr_name`.
        """
        for o in self._store.objects():
            if isinstance(o, typ):
                if getattr(o, attr_name) == value:
                    return o
        return None

    def _in_store(
            self, typ: Type[_ReplicatedClass], attr_name: str, value: Any
            ) -> bool:
        """Returns True iff a matching object is in the store.

        Searches the store for an object of type `typ` that has value
        `value` for its attribute named `attr_name`, and returns True
        if there is at least one of those in the store.

        Args:
            typ: Type of object to consider, subclass of
                RegisteredObject.
            attr_name: Name of the attribute on that object to check.
            value: Value that the attribute must have.

        Returns:
            True if a matching object was found, False otherwise.

        Raises:
            AttributeError if an object of type `typ` is encountered
                in the store which does not have an attribute named
                `attr_name`.
        """
        return self._get_object(typ, attr_name, value) is not None


global_registry = Registry()
