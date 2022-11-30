class DisableIntrospectionSchemaMiddleware:
    """
    This middleware should use for production mode. This class hide the
    introspection.
    """

    def resolve(self, next, root, info, **args):
        if info.field_name == "__schema":
            return None
        return next(root, info, **args)
