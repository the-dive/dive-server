import graphene

from apps.file import schema as file_schema, mutation as file_mutation


# schemas
class Query(file_schema.Query, graphene.ObjectType):
    pass


# mutations
class Mutation(file_mutation.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
