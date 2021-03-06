"""Definitions of the contents of the central registry."""
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from proof_of_concept.definitions.identifier import Identifier


class RegisteredObject:
    """Base class for objects in the registry."""
    pass


class PartyDescription(RegisteredObject):
    """Describes a Party to the rest of the DDM.

    Attributes:
        id: Id of the party.
        public_key: The party's public key for signing rules.

    """
    def __init__(self, party_id: Identifier, public_key: RSAPublicKey) -> None:
        """Create a PartyDescription.

        Args:
            party_id: ID of the party.
            public_key: The party's public key for signing rules.
        """
        self.id = party_id
        self.public_key = public_key

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f'PartyDescription({self.id})'


class SiteDescription(RegisteredObject):
    """Describes a site to the rest of the DDM.

    Attributes:
        id: ID of the site.
        owner_id: The party which owns this site.
        admin_id: The party which administrates this site.
        endpoint: This site's REST endpoint.
        runner: Whether the site has a runner.
        store: Whether the site has a store.
        namespace: The namespace managed by this site's policy server,
            if any.

    """
    def __init__(
            self,
            site_id: Identifier,
            owner_id: Identifier,
            admin_id: Identifier,
            endpoint: str,
            runner: bool,
            store: bool,
            namespace: Optional[str]
            ) -> None:
        """Create a SiteDescription.

        Args:
            site_id: Identifier of the site.
            owner_id: Identifier of the party which owns this site.
            admin_id: Identifier of the party which administrates this
                site.
            endpoint: URL of the REST endpoint of this site.
            runner: Whether the site has a runner.
            store: Whether the site has a store.
            namespace: The namespace managed by this site's policy
                server, if any.

        """
        self.id = site_id
        self.owner_id = owner_id
        self.admin_id = admin_id
        self.endpoint = endpoint
        self.runner = runner
        self.store = store
        self.namespace = namespace

        if runner and not store:
            raise RuntimeError('Site with runner needs a store')

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f'SiteDescription({self.id})'
