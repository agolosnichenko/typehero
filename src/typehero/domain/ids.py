"""Domain identifier types.

A `CourseId` is the foreign key tying a profile's active course, its saved
benchmarks, and the loaded course catalogue together. Modelling it as a
`NewType` (not a bare `str`) lets the type checker catch a course id passed
where, say, a lesson id or UI locale is expected, while staying a plain string
at runtime — so persisted JSON is unchanged.
"""

from __future__ import annotations

from typing import NewType

CourseId = NewType("CourseId", str)
