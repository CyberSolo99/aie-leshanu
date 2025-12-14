from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2


def test_has_constant_columns_flag():
    df = pd.DataFrame(
        {
            "age": [10, 20, 30, 40],
            "gender": ["M", "M", "M", "M"],  # константная колонка
        }
    )

    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)

    assert flags["has_constant_columns"] is True


def test_has_high_cardinality_columns_flag():
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u2", "u3", "u4", "u5"],
            "age": [10, 20, 30, 40, 50],
        }
    )

    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    flags = compute_quality_flags(summary, missing_df)

    assert flags["has_high_cardinality_columns"] is True


def test_missing_table_min_share():
    df = pd.DataFrame(
        {
            "a": [1, 2, None, 4],
            "b": [None, None, 3, 4],
            "c": [1, 2, 3, 4],
        }
    )

    # Проверяем без фильтрации
    result_all = missing_table(df)
    assert "a" in result_all.index
    assert "b" in result_all.index
    assert "c" in result_all.index

    # Фильтруем по min_share=0.5
    result_filtered = missing_table(df, min_share=0.5)
    # Только колонка 'b' должна остаться (2 пропуска из 4 = 0.5)
    assert list(result_filtered.index) == ["b"]
    assert result_filtered.loc["b", "missing_share"] == 0.5
