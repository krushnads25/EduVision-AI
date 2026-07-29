from .base import Base

# Import models so they are registered with SQLAlchemy metadata
from . import college  # noqa: F401
from . import course  # noqa: F401
from . import candidate  # noqa: F401
from . import district  # noqa: F401
from . import seat_matrix  # noqa: F401
from . import cutoff  # noqa: F401
from . import vacancy  # noqa: F401
from . import recommendation  # noqa: F401
from . import prediction  # noqa: F401
from . import analytics_cache  # noqa: F401

__all__ = [
	"Base",
	"college",
	"course",
	"candidate",
	"district",
	"seat_matrix",
	"cutoff",
	"vacancy",
	"recommendation",
	"prediction",
	"analytics_cache",
]
