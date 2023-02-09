from typing import List, Optional

from apps.core.models import Table, Action
from .base import get_action_class, BaseAction


def parse_raw_action(
    action_name: str, params: List[str], table: Table
) -> Optional[BaseAction]:
    Action = get_action_class(action_name)
    return Action and Action(params, table)


def get_composed_action_for_action_object(action_obj: Action) -> BaseAction:
    """
    Given an unapplied action object for a table, fetch all unapplied actions
    before it and create a composed action and return it.
    """
    # Fetch all actions which are not associated to snapshot
    action_objs_qs = Action.objects.filter(
        table=action_obj.table,
        order__lte=action_obj.order,
        snapshot__isnull=True,
    ).order_by("order")

    actions = [
        act
        for obj in action_objs_qs
        if (act := parse_raw_action(obj.action_name, obj.parameters, action_obj.table))
        is not None
    ]
    ComposedAction = BaseAction.compose(actions)
    # NOTE: "ComposedAction" below: passing params and table leaves a hole that constituent actions can
    # be associated with one table while we can pass different table in
    # ComposedAction constructor
    return ComposedAction(params=[], table=action_obj.table)
