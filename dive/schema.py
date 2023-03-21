import graphene
import sentry_sdk

from django.conf import settings
from apps.file import schema as file_schema
from apps.core import schema as core_schema, mutations as core_mutations
from graphql.execution import ExecutionResult


# schemas
class Query(file_schema.Query, core_schema.Query, graphene.ObjectType):
    pass


# mutations
class Mutation(core_mutations.Mutation, graphene.ObjectType):
    pass


class Schema(graphene.Schema):
    def _scope_with_sentry(self, execute_func, *args, **kwargs) -> ExecutionResult:
        if not settings.SENTRY_ENABLED:
            return execute_func(*args, **kwargs)
        operation_name = kwargs.get("operation_name")
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("kind", operation_name)
            scope.transaction.name = operation_name
            return execute_func(*args, **kwargs)

    def execute_sync(self, *args, **kwargs) -> ExecutionResult:
        return self._scope_with_sentry(super().execute_sync, *args, **kwargs)

    def execute(self, *args, **kwargs) -> ExecutionResult:
        return self._scope_with_sentry(super().execute, *args, **kwargs)


schema = Schema(query=Query, mutation=Mutation)
