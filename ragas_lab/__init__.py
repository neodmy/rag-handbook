"""Shared, reusable infrastructure for the handbook's lessons.

Cross-cutting helpers (settings, evaluator clients, dataset loaders) live here so
lessons import them instead of duplicating setup. Lesson-specific code stays in
each lesson folder under ``lessons/``.
"""
