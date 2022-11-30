from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

PERMISSION_DENIED_MESSAGE = _("You do not have permission to perform this action.")


class WhiteListMiddleware:
    def resolve(self, next, root, info, **args):
        # if user is not authenticated and user is not accessing
        # whitelisted nodes, then raise permission denied error

        # furthermore, this check must only happen in the root node, and not in deeper nodes
        if root is None:
            if (
                not info.context.user.is_authenticated
                and info.field_name not in settings.GRAPHENE_NODES_WHITELIST
            ):
                raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
        return next(root, info, **args)
