"""This package is used for a bot logic implementation."""
from .help import help_router
from .start import start_router
from .order import order_router

routers = (start_router, help_router, order_router)
