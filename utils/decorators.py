from django.utils.translation import gettext
from utils.graphene.mutation import DiveMutationMixin


def lift_mutate_with_instance(ModelClass):
    """
    This is a decorator for mutate static methods which handles Model.objects.get()
    and returns appropriate error.
    NOTE: The decorated function will have the model instance as the first argument
    and the rest arguments are similar to the original mutate function
    """
    def wrapper(f):
        def mutate(root, info, id, *args, **kwargs):
            try:
                instance = ModelClass.objects.get(id=id)
            except ModelClass.DoesNotExist:
                return DiveMutationMixin(
                    errors=[
                        dict(
                            field="nonFieldErrors",
                            messages=gettext("Table does not exist."),
                        )
                    ]
                )
            else:
                return f(instance, root, info, id, *args, **kwargs)
        return mutate
    return wrapper
