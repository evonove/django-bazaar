from __future__ import absolute_import
from __future__ import unicode_literals

from ..compat import post_migrate
from .stores.config import create_stores


post_migrate.connect(create_stores)
