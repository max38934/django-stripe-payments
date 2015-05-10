import datetime
import decimal

from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib, timezone
from django.apps import apps as django_apps
from django.conf import settings


def convert_tstamp(response, field_name=None):
    try:
        if field_name and response[field_name]:
            return datetime.datetime.fromtimestamp(
                response[field_name],
                timezone.utc
            )
        if not field_name:
            return datetime.datetime.fromtimestamp(
                response,
                timezone.utc
            )
    except KeyError:
        pass
    return None


def get_user_model():  # pragma: no cover
    try:
        # pylint: disable=E0611
        from django.contrib.auth import get_user_model as django_get_user_model
        return django_get_user_model()
    except ImportError:
        from django.contrib.auth.models import User
        return User


def load_path_attr(path):  # pragma: no cover
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = importlib.import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing {0}: '{1}'".format(module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            "Module '{0}' does not define a '{1}'".format(
                module,
                attr
            )
        )
    return attr


# currencies those amount=1 means 100 cents
# https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
ZERO_DECIMAL_CURRENCIES = [
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw",
    "mga", "pyg", "rwf", "vuv", "xaf", "xof", "xpf",
]


def convert_amount_for_db(amount, currency="usd"):
    return (amount / decimal.Decimal("100")) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else decimal.Decimal(amount)


def convert_amount_for_api(amount, currency="usd"):
    return int(amount * 100) if currency.lower() not in ZERO_DECIMAL_CURRENCIES else int(amount)


def get_plan_model():
    """
    Returns the Plan model that is active in this project.
    """
    try:
        return django_apps.get_model(getattr(settings, "STRIPE_PLAN_MODEL", "payments.Plan"))
    except ValueError:
        raise ImproperlyConfigured("AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured("AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.STRIPE_PLAN_MODEL)