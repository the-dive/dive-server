import graphene

from apps.file import schema as file_schema, mutations as file_mutations
from apps.core import schema as core_schema, mutations as core_mutations


# schemas
class Query(file_schema.Query, core_schema.Query, graphene.ObjectType):
    pass


# mutations
class Mutation(file_mutations.Mutation, core_mutations.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
