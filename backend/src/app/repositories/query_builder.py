"""Fluent Query Builder pattern for OtakuHub backend repositories."""

from typing import TypeVar, Generic, List, Optional
from sqlmodel import SQLModel, select, func, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType", bound=SQLModel)


class QueryBuilder(Generic[ModelType]):
    """Fluent Query Builder for database operations."""

    def __init__(self, model: ModelType, db_session: AsyncSession):
        self.model = model
        self.db_session = db_session
        self._statement = select(model)
        self._where_conditions = []
        self._order_by_clauses = []
        self._limit = None
        self._offset = None
        self._joins = []
        self._group_by = []
        self._having_conditions = []
        # Soft‑delete handling: include only non‑deleted rows by default
        self._include_deleted = False
        # Detect if the model defines a ``deleted_at`` column
        self._has_deleted_at = hasattr(model, "deleted_at")

    def filter(self, condition) -> 'QueryBuilder[ModelType]':
        """Add a filter condition."""
        self._where_conditions.append(condition)
        return self

    def where(self, condition) -> 'QueryBuilder[ModelType]':
        """Add a where condition (alias for filter)."""
        return self.filter(condition)

    def and_(self, condition) -> 'QueryBuilder[ModelType]':
        """Add an AND condition."""
        self._where_conditions.append(condition)
        return self

    def or_(self, condition) -> 'QueryBuilder[ModelType]':
        """Add an OR condition.

        This combines the existing where conditions with the new ``condition`` using
        SQLAlchemy's ``or_`` function. If there are already multiple conditions, they
        are wrapped in an ``or_`` together with the new one. This mirrors the behaviour
        of ``and_`` but uses logical OR.
        """
        from sqlalchemy import or_ as sql_or
        if self._where_conditions:
            # Combine existing conditions into a single expression then OR with new
            existing = and_(*self._where_conditions)
            self._where_conditions = [sql_or(existing, condition)]
        else:
            self._where_conditions.append(condition)
        return self

    def order_by(self, *fields) -> 'QueryBuilder[ModelType]':
        """Add order by clauses."""
        self._order_by_clauses.extend(fields)
        return self

    def nulls_last(self) -> 'QueryBuilder[ModelType]':
        """Apply nulls_last to the last order_by clause."""
        if self._order_by_clauses:
            self._order_by_clauses[-1] = self._order_by_clauses[-1].nulls_last()
        return self

    def desc(self, field) -> 'QueryBuilder[ModelType]':
        """Add descending order by clause."""
        self._order_by_clauses.append(desc(field))
        return self

    def asc(self, field) -> 'QueryBuilder[ModelType]':
        """Add ascending order by clause."""
        self._order_by_clauses.append(asc(field))
        return self

    def limit(self, limit: int) -> 'QueryBuilder[ModelType]':
        """Add limit clause."""
        self._limit = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder[ModelType]':
        """Add offset clause."""
        self._offset = offset
        return self

    def join(self, target_model, onclause=None, isouter=False) -> 'QueryBuilder[ModelType]':
        """Add a join clause."""
        self._joins.append((target_model, onclause, isouter))
        return self

    def options(self, *opts) -> 'QueryBuilder[ModelType]':
        """Add eager-loading options (e.g. joinedload, selectinload)."""
        self._statement = self._statement.options(*opts)
        return self

    def group_by(self, *fields) -> 'QueryBuilder[ModelType]':
        """Add group by clause."""
        self._group_by.extend(fields)
        return self

    def having(self, condition) -> 'QueryBuilder[ModelType]':
        """Add having condition."""
        self._having_conditions.append(condition)
        return self

    def _apply_conditions(self):
        """Apply all conditions to the statement, including the default soft‑delete filter."""
        # ------------------------------------------------------------------
        # Soft‑delete filter (global, unless overridden)
        # ------------------------------------------------------------------
        if self._has_deleted_at and not self._include_deleted:
            # ``deleted_at`` is NULL for active rows
            self._where_conditions.insert(0, self.model.deleted_at.is_(None))

        # Apply where conditions (including the soft‑delete clause if present)
        if self._where_conditions:
            self._statement = self._statement.where(
                and_(*self._where_conditions)
            )

        # Apply joins if any
        for join_info in self._joins:
            target_model, onclause, isouter = join_info
            if isouter:
                self._statement = self._statement.outerjoin(target_model, onclause)
            else:
                self._statement = self._statement.join(target_model, onclause)

        # Apply order by if any
        if self._order_by_clauses:
            self._statement = self._statement.order_by(*self._order_by_clauses)

        # Apply limit and offset
        if self._limit is not None:
            self._statement = self._statement.limit(self._limit)

        if self._offset is not None:
            self._statement = self._statement.offset(self._offset)

        # Apply group by if any
        if self._group_by:
            self._statement = self._statement.group_by(*self._group_by)

        # Apply having conditions if any
        if self._having_conditions:
            self._statement = self._statement.having(*self._having_conditions)

    async def all(self) -> List[ModelType]:
        """Execute query and return all results."""
        self._apply_conditions()
        result = await self.db_session.exec(self._statement)
        return result.all()

    async def first(self) -> Optional[ModelType]:
        """Execute query and return first result."""
        self._apply_conditions()
        # Add limit 1 for better performance
        limit_statement = self._statement.limit(1)
        result = await self.db_session.exec(limit_statement)
        return result.one_or_none()

    async def count(self) -> int:
        """Execute query and return count."""
        self._apply_conditions()
        # Create a count query by replacing the columns with count
        count_statement = select(func.count(self.model.id))

        # Apply all conditions to count statement
        if self._where_conditions:
            count_statement = count_statement.where(
                and_(*self._where_conditions)
            )

        # Apply joins to count statement
        for join_info in self._joins:
            target_model, onclause, isouter = join_info
            if isouter:
                count_statement = count_statement.outerjoin(target_model, onclause)
            else:
                count_statement = count_statement.join(target_model, onclause)

        if self._group_by:
            count_statement = count_statement.group_by(*self._group_by)

        if self._having_conditions:
            count_statement = count_statement.having(*self._having_conditions)

        result = await self.db_session.exec(count_statement)
        return result.one_or_none() or 0

    async def exists(self) -> bool:
        """Check if any records match the query."""
        self._apply_conditions()
        # Use .exists() on the select statement for cross-dialect compatibility
        # (func.exists() wraps in scalar subquery which fails on SQLite)
        exists_statement = select(self._statement.exists())
        result = await self.db_session.execute(exists_statement)
        return result.scalar() or False

    def with_deleted(self) -> 'QueryBuilder[ModelType]':
        """Return a clone that includes soft‑deleted rows.

        By default the builder excludes rows where ``deleted_at`` is not ``NULL``.
        Call ``with_deleted()`` when an admin view needs to see all rows.
        """
        cloned = self.clone()
        cloned._include_deleted = True
        return cloned

    def clone(self) -> 'QueryBuilder[ModelType]':
        """Create a clone of this query builder."""
        cloned = QueryBuilder(self.model, self.db_session)
        cloned._where_conditions = self._where_conditions.copy()
        cloned._order_by_clauses = self._order_by_clauses.copy()
        cloned._limit = self._limit
        cloned._offset = self._offset
        cloned._joins = self._joins.copy()
        cloned._group_by = self._group_by.copy()
        cloned._having_conditions = self._having_conditions.copy()
        return cloned


class QueryBuilderPattern:
    """Provides static factory methods for creating query builders."""

    @staticmethod
    def build(model: ModelType, db_session: AsyncSession) -> QueryBuilder[ModelType]:
        """Create a new QueryBuilder instance."""
        return QueryBuilder(model, db_session)
