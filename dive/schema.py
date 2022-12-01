import graphene

from apps.file import schema as file_schema, mutations as file_mutation
from apps.core import schema as core_schema


# schemas
class Query(file_schema.Query, core_schema.Query, graphene.ObjectType):
    pass


# mutations
class Mutation(file_mutation.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
