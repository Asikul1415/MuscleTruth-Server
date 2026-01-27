from .auth import auth_router
from .weightings import weightings_router
from .meals import meals_router
from .products import products_router
from .servings import servings_router
from .users import users_router

__all__ = ["auth_router", "weightings_router", "meals_router", "products_router", "servings_router", "users_router"]