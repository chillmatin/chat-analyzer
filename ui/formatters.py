"""Data formatting utilities for WhatsApp Chat Analyzer."""

import pandas as pd
from typing import Dict, List, Optional, Any, Callable


def dict_to_dataframe(
    data_dict: Dict,
    key_name: str,
    value_name: str,
    sort_by: Optional[str] = None,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Convert a dictionary to a DataFrame with named columns.
    
    Args:
        data_dict: Dictionary to convert
        key_name: Name for the keys column
        value_name: Name for the values column
        sort_by: Column name to sort by
        ascending: Sort direction
        
    Returns:
        DataFrame with named columns
    """
    df = pd.DataFrame({
        key_name: list(data_dict.keys()),
        value_name: list(data_dict.values())
    })
    
    if sort_by:
        df = df.sort_values(sort_by, ascending=ascending)
    
    return df


def add_percentage_column(
    df: pd.DataFrame,
    column_name: str,
    new_col_name: str = 'Percentage',
    decimals: int = 1
) -> pd.DataFrame:
    """
    Add a percentage column based on another column.
    
    Args:
        df: Input DataFrame
        column_name: Column to calculate percentages from
        new_col_name: Name for the new percentage column
        decimals: Number of decimal places
        
    Returns:
        DataFrame with added percentage column
    """
    df = df.copy()
    df[new_col_name] = (df[column_name] / df[column_name].sum() * 100).round(decimals)
    return df


def format_datetime_df(
    df: pd.DataFrame,
    date_col: str,
    extract_components: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Convert a column to datetime and optionally extract components.
    
    Args:
        df: Input DataFrame
        date_col: Name of the date column
        extract_components: List of components to extract: 
                          ['week', 'year', 'weekday', 'month', 'day', 'hour']
        
    Returns:
        DataFrame with datetime conversion and extracted components
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    if extract_components:
        for component in extract_components:
            match component:
                case 'week':
                    df['Week'] = df[date_col].dt.isocalendar().week  # type: ignore
                case 'year':
                    df['Year'] = df[date_col].dt.year  # type: ignore
                case 'weekday':
                    df['Weekday'] = df[date_col].dt.dayofweek  # type: ignore
                case 'month':
                    df['Month'] = df[date_col].dt.month  # type: ignore
                case 'day':
                    df['Day'] = df[date_col].dt.day  # type: ignore
                case 'hour':
                    df['Hour'] = df[date_col].dt.hour  # type: ignore
    
    return df


def apply_categorical_order(
    df: pd.DataFrame,
    column: str,
    categories: List[str]
) -> pd.DataFrame:
    """
    Apply categorical ordering to a column.
    
    Args:
        df: Input DataFrame
        column: Column name to apply ordering to
        categories: Ordered list of categories
        
    Returns:
        DataFrame with categorical column
    """
    df = df.copy()
    df[column] = pd.Categorical(df[column], categories=categories, ordered=True)
    return df.sort_values(column)


def create_pivot_heatmap(
    df: pd.DataFrame,
    index_col: str,
    columns_col: str,
    values_col: str,
    fill_value: Any = 0,
    reindex: Optional[List] = None
) -> pd.DataFrame:
    """
    Create a pivot table for heatmap visualization.
    
    Args:
        df: Input DataFrame
        index_col: Column to use for index
        columns_col: Column to use for columns
        values_col: Column to use for values
        fill_value: Value to use for missing data
        reindex: Optional list to reindex rows
        
    Returns:
        Pivoted DataFrame
    """
    pivot = df.pivot_table(
        index=index_col,
        columns=columns_col,
        values=values_col,
        fill_value=fill_value
    )
    
    if reindex:
        pivot = pivot.reindex(reindex, fill_value=fill_value)
    
    return pivot


def add_rolling_average(
    df: pd.DataFrame,
    column: str,
    window: int = 7,
    center: bool = True,
    new_col_suffix: str = ' MA'
) -> pd.DataFrame:
    """
    Add a rolling average column.
    
    Args:
        df: Input DataFrame
        column: Column to calculate rolling average on
        window: Window size for rolling average
        center: Whether to center the window
        new_col_suffix: Suffix for the new column name
        
    Returns:
        DataFrame with added rolling average column
    """
    df = df.copy()
    new_col_name = f"{window}-day{new_col_suffix}"
    df[new_col_name] = df[column].rolling(window=window, center=center).mean()
    return df


def format_hour_labels(hours: List[int]) -> List[str]:
    """
    Format hour numbers as HH:00 strings.
    
    Args:
        hours: List of hour integers (0-23)
        
    Returns:
        List of formatted hour strings
    """
    return [f"{h:02d}:00" for h in hours]


def aggregate_by_period(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    period: str = 'week',
    agg_func: str = 'sum'
) -> pd.DataFrame:
    """
    Aggregate data by time period.
    
    Args:
        df: Input DataFrame
        date_col: Date column name
        value_col: Value column to aggregate
        period: Period to aggregate by ('week', 'month', 'year')
        agg_func: Aggregation function ('sum', 'mean', 'count')
        
    Returns:
        Aggregated DataFrame
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    if period == 'week':
        df['Period'] = df[date_col].dt.to_period('W').astype(str)  # type: ignore
    elif period == 'month':
        df['Period'] = df[date_col].dt.to_period('M').astype(str)  # type: ignore
    elif period == 'year':
        df['Period'] = df[date_col].dt.to_period('Y').astype(str)  # type: ignore
    
    agg_method = getattr(df.groupby('Period')[value_col], agg_func)
    result = agg_method().reset_index()
    result.columns = [period.capitalize(), value_col]
    
    return result


def prepare_bar_data(
    data_dict: Dict,
    key_name: str = 'Category',
    value_name: str = 'Value',
    key_formatter: Optional[Callable] = None,
    top_n: Optional[int] = None,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Prepare dictionary data for bar chart visualization.
    
    Args:
        data_dict: Dictionary with data
        key_name: Name for keys column
        value_name: Name for values column
        key_formatter: Optional function to format keys
        top_n: Optional limit to top N items
        ascending: Sort direction
        
    Returns:
        DataFrame ready for bar chart
    """
    df = dict_to_dataframe(data_dict, key_name, value_name, sort_by=value_name, ascending=ascending)
    
    if key_formatter:
        df[key_name] = df[key_name].apply(key_formatter)
    
    if top_n:
        df = df.head(top_n)
    
    return df


def prepare_comparison_data(
    participants_dict: Dict[str, Dict],
    metrics: List[str],
    participant_col: str = 'Participant'
) -> pd.DataFrame:
    """
    Prepare data for participant comparison charts.
    
    Args:
        participants_dict: Dictionary mapping participant names to their metrics
        metrics: List of metric names to include
        participant_col: Name for the participant column
        
    Returns:
        DataFrame with participants and their metrics
    """
    data = {participant_col: list(participants_dict.keys())}
    
    for metric in metrics:
        data[metric] = [participants_dict[p].get(metric, 0) for p in participants_dict.keys()]
    
    return pd.DataFrame(data)


# Standard day of week ordering
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAY_ORDER_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
