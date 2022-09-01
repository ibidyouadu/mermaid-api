from typing import Any, Dict, Type

from django.db.models import NOT_PROVIDED, Manager  #, Model, QuerySet  # type: ignore
from django.db.models.constants import LOOKUP_SEP  # type: ignore
from .djangobase.model_22 import Model
from .djangobase.datastructures_22 import BaseTable, MultiJoin
from .djangobase.expressions_22 import SimpleCol, F
from .djangobase.queryset_22 import QuerySet
from .djangobase.where_22 import WhereNode
from .query_22 import Query, JoinPromoter
# from django.db.models.sql import Query  # type: ignore
# from django.db.models.sql.datastructures import BaseTable  # type: ignore
# from django.db.models.sql.datastructures import MultiJoin
from django.core.exceptions import FieldError
from django.db.models.fields.related_lookups import MultiColSource
from django.db.models.sql.constants import LOUTER
from django.db.models.sql.where import AND
from django.db import NotSupportedError
from collections.abc import Iterator
from django.utils.tree import Node
# from django.db.models.sql.where import WhereNode  # type: ignore

from .datastructures import SQLTable, SQLTableParams


def _get_col(target, field, alias, simple_col):
    if simple_col:
        return SimpleCol(target, field)
    return target.get_col(alias, field)


class SQLTableQuery(Query):
    def __init__(self, model, where=WhereNode):
        super().__init__(model, where)
        self.sql_table_params = {}
        self.model_sql = model.sql
        self.external_aliases = {}

    def get_initial_alias(self):
        # print("get_initial_alias")
        if self.alias_map:
            alias = self.base_table
            self.ref_alias(alias)
        else:

            if hasattr(self.model, "sql_args"):
                try:
                    params = dict(
                        next(
                            filter(lambda x: x.level == 0, self.sql_table_params)
                        ).params.items()
                    )
                except StopIteration:
                    # no parameters were passed from user
                    # so try to call the sql without parameters
                    # in case that they are optional
                    params = {}

                alias = self.join(
                    SQLTable(self.get_meta().db_table, None, params, self.model_sql)
                )
            else:
                alias = self.join(BaseTable(self.get_meta().db_table, None))
        print(alias)
        return alias

    def sql_table(self, **sql_table_params: Dict[str, Any]):
        """
        Take user's passed params and store them in `self.sql_table_params`
        to be prepared for joining.
        """
        _sql_table_params = []
        for table_lookup, param_dict in self._sql_table_params_to_groups(
            sql_table_params
        ).items():
            if not table_lookup:
                level = 0
                join_field = None
                model = self.model
            else:
                level = len(table_lookup.split(LOOKUP_SEP))
                lookup_parts, field_parts, _ = self.solve_lookup_type(table_lookup)
                path, final_field, targets, rest = self.names_to_path(
                    field_parts, self.get_meta(), allow_many=False, fail_on_missing=True
                )
                join_field = path[-1].join_field
                model = final_field.related_model

            _sql_table_params.append(
                SQLTableParams(
                    level=level,
                    join_field=join_field,
                    params=self._reorder_sql_table_params(model, param_dict),
                )
            )

        # TODO: merge with existing?
        self.sql_table_params = _sql_table_params

    def _sql_table_params_to_groups(
        self, sql_table_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transfer user specified lookups into groups
        to have all parameters for each table function prepared for joining.

        {id: 1, parent__id: 2, parent__code=3, parent__parent__id=4, root__id=5}
            =>
        {
            '': {'id': 1},
            'parent': {'id': 2, 'code': 3},
            'parent__parent': {'id': 4},
            'root': {'id: 5}
        }
        """
        param_groups: Dict[str, Any] = {}
        for lookup, val in sql_table_params.items():
            parts = lookup.split(LOOKUP_SEP)
            prefix = LOOKUP_SEP.join(parts[:-1])
            field = parts[-1]
            if prefix not in param_groups:
                param_groups[prefix] = {}
            param_groups[prefix][field] = val
        return param_groups

    def _reorder_sql_table_params(  # noqa: C901
        self, model: Type[Model], sql_table_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make sure that parameters will be passed into function in correct order.
        Also check required and set defaults.
        """
        ordered_sql_params = dict()
        for key, arg in getattr(model, "sql_args").items():
            if key in sql_table_params:
                ordered_sql_params[key] = sql_table_params[key]
            elif arg.default != NOT_PROVIDED:
                ordered_sql_params[key] = arg.default
            elif arg.required:
                raise ValueError(f"Required function arg `{key}` not specified")

        remaining = set(sql_table_params.keys()) - set(ordered_sql_params.keys())
        if remaining:
            raise ValueError(f"SQL arg `{remaining.pop()}` not found")

        return ordered_sql_params

    def can_filter(self):
        """
        Return True if adding filters to this instance is still possible.

        Typically, this means no limits or offsets have been put on the results.
        """
        return not self.low_mark and self.high_mark is None

    def resolve_lookup_value(self, value, can_reuse, allow_joins, simple_col):
        if hasattr(value, 'resolve_expression'):
            kwargs = {'reuse': can_reuse, 'allow_joins': allow_joins}
            if isinstance(value, F):
                kwargs['simple_col'] = simple_col
            value = value.resolve_expression(self, **kwargs)
        elif isinstance(value, (list, tuple)):
            # The items of the iterable may be expressions and therefore need
            # to be resolved independently.
            for sub_value in value:
                if hasattr(sub_value, 'resolve_expression'):
                    if isinstance(sub_value, F):
                        sub_value.resolve_expression(
                            self, reuse=can_reuse, allow_joins=allow_joins,
                            simple_col=simple_col,
                        )
                    else:
                        sub_value.resolve_expression(self, reuse=can_reuse, allow_joins=allow_joins)
        return value

    def build_filter(self, filter_expr, branch_negated=False, current_negated=False,
                     can_reuse=None, allow_joins=True, split_subq=True,
                     reuse_with_filtered_relation=False, simple_col=False):
        """
        Build a WhereNode for a single filter clause but don't add it
        to this Query. Query.add_q() will then add this filter to the where
        Node.

        The 'branch_negated' tells us if the current branch contains any
        negations. This will be used to determine if subqueries are needed.

        The 'current_negated' is used to determine if the current filter is
        negated or not and this will be used to determine if IS NULL filtering
        is needed.

        The difference between current_negated and branch_negated is that
        branch_negated is set on first negation, but current_negated is
        flipped for each negation.

        Note that add_filter will not do any negating itself, that is done
        upper in the code by add_q().

        The 'can_reuse' is a set of reusable joins for multijoins.

        If 'reuse_with_filtered_relation' is True, then only joins in can_reuse
        will be reused.

        The method will create a filter clause that can be added to the current
        query. However, if the filter isn't added to the query then the caller
        is responsible for unreffing the joins used.
        """
        if isinstance(filter_expr, dict):
            raise FieldError("Cannot parse keyword query as dict")
        arg, value = filter_expr
        if not arg:
            raise FieldError("Cannot parse keyword query %r" % arg)
        lookups, parts, reffed_expression = self.solve_lookup_type(arg)

        if not getattr(reffed_expression, 'filterable', True):
            raise NotSupportedError(
                reffed_expression.__class__.__name__ + ' is disallowed in '
                'the filter clause.'
            )

        if not allow_joins and len(parts) > 1:
            raise FieldError("Joined field references are not permitted in this query")

        pre_joins = self.alias_refcount.copy()
        value = self.resolve_lookup_value(value, can_reuse, allow_joins, simple_col)
        used_joins = {k for k, v in self.alias_refcount.items() if v > pre_joins.get(k, 0)}

        clause = self.where_class()
        if reffed_expression:
            condition = self.build_lookup(lookups, reffed_expression, value)
            clause.add(condition, AND)
            return clause, []

        opts = self.get_meta()
        alias = self.get_initial_alias()
        allow_many = not branch_negated or not split_subq

        try:
            join_info = self.setup_joins(
                parts, opts, alias, can_reuse=can_reuse, allow_many=allow_many,
                reuse_with_filtered_relation=reuse_with_filtered_relation,
            )

            # Prevent iterator from being consumed by check_related_objects()
            if isinstance(value, Iterator):
                value = list(value)
            self.check_related_objects(join_info.final_field, value, join_info.opts)

            # split_exclude() needs to know which joins were generated for the
            # lookup parts
            self._lookup_joins = join_info.joins
        except MultiJoin as e:
            print("multijoin")
            return self.split_exclude(filter_expr, can_reuse, e.names_with_path)

        # Update used_joins before trimming since they are reused to determine
        # which joins could be later promoted to INNER.
        used_joins.update(join_info.joins)
        targets, alias, join_list = self.trim_joins(join_info.targets, join_info.joins, join_info.path)
        if can_reuse is not None:
            can_reuse.update(join_list)

        if join_info.final_field.is_relation:
            # No support for transforms for relational fields
            num_lookups = len(lookups)
            if num_lookups > 1:
                raise FieldError('Related Field got invalid lookup: {}'.format(lookups[0]))
            if len(targets) == 1:
                col = _get_col(targets[0], join_info.final_field, alias, simple_col)
            else:
                col = MultiColSource(alias, targets, join_info.targets, join_info.final_field)
        else:
            col = _get_col(targets[0], join_info.final_field, alias, simple_col)

        condition = self.build_lookup(lookups, col, value)
        lookup_type = condition.lookup_name
        clause.add(condition, AND)

        require_outer = lookup_type == 'isnull' and condition.rhs is True and not current_negated
        if current_negated and (lookup_type != 'isnull' or condition.rhs is False) and condition.rhs is not None:
            require_outer = True
            if (lookup_type != 'isnull' and (
                    self.is_nullable(targets[0]) or
                    self.alias_map[join_list[-1]].join_type == LOUTER)):
                # The condition added here will be SQL like this:
                # NOT (col IS NOT NULL), where the first NOT is added in
                # upper layers of code. The reason for addition is that if col
                # is null, then col != someval will result in SQL "unknown"
                # which isn't the same as in Python. The Python None handling
                # is wanted, and it can be gotten by
                # (col IS NULL OR col != someval)
                #   <=>
                # NOT (col IS NOT NULL AND col = someval).
                lookup_class = targets[0].get_lookup('isnull')
                col = _get_col(targets[0], join_info.targets[0], alias, simple_col)
                clause.add(lookup_class(col, False), AND)
        return clause, used_joins if not require_outer else ()

    # def build_where(self, q_object):
    #     return self._add_q(q_object, used_aliases=set(), allow_joins=False, simple_col=True)[0]

    def _add_q(self, q_object, used_aliases, branch_negated=False,
               current_negated=False, allow_joins=True, split_subq=True,
               simple_col=False):
        """Add a Q-object to the current filter."""
        connector = q_object.connector
        current_negated = current_negated ^ q_object.negated
        branch_negated = branch_negated or q_object.negated
        target_clause = self.where_class(connector=connector,
                                         negated=q_object.negated)
        joinpromoter = JoinPromoter(q_object.connector, len(q_object.children), current_negated)
        for child in q_object.children:
            if isinstance(child, Node):
                child_clause, needed_inner = self._add_q(
                    child, used_aliases, branch_negated,
                    current_negated, allow_joins, split_subq, simple_col)
                joinpromoter.add_votes(needed_inner)
            else:
                child_clause, needed_inner = self.build_filter(
                    child, can_reuse=used_aliases, branch_negated=branch_negated,
                    current_negated=current_negated, allow_joins=allow_joins,
                    split_subq=split_subq, simple_col=simple_col,
                )
                joinpromoter.add_votes(needed_inner)
            if child_clause:
                target_clause.add(child_clause, connector)
        needed_inner = joinpromoter.update_join_types(self)
        return target_clause, needed_inner


class SQLTableQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or SQLTableQuery(self.model)

    def sql_table(self, **sql_table_params: Dict[str, Any]) -> "SQLTableQuerySet":
        self.query.sql_table(**sql_table_params)
        return self


class SQLTableManager(Manager):
    def get_queryset(self) -> SQLTableQuerySet:
        return SQLTableQuerySet(model=self.model, using=self._db, hints=self._hints)
