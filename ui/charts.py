"""Chart creation utilities for WhatsApp Chat Analyzer."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional, Dict, Any


# Chart configuration constants
CHART_HEIGHTS = {
    'pie': 400,
    'bar': 400,
    'line': 500,
    'heatmap': 500,
    'calendar': 300,
    'horizontal_bar': 600
}

COLOR_SCHEMES = {
    'messages': 'Blues',
    'activity': 'Greens',
    'comparison': 'Viridis',
    'sentiment': 'RdYlGn',
    'media': 'Sunset',
    'words': 'Teal',
    'emojis': 'Plasma',
    'participants': 'RdBu',
    'github': ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39', '#0d4429']
}


def create_pie_chart(
    values: List,
    names: List,
    title: str,
    hole: float = 0.4,
    color_scheme: str = 'RdBu',
    show_labels: bool = True
) -> go.Figure:
    """
    Create a pie/donut chart.
    
    Args:
        values: List of values
        names: List of labels
        title: Chart title
        hole: Size of center hole (0 = pie, >0 = donut)
        color_scheme: Plotly color scheme name
        show_labels: Whether to show labels
        
    Returns:
        Plotly Figure
    """
    color_sequence = COLOR_SCHEMES.get(color_scheme, color_scheme)
    if isinstance(color_sequence, str):
        color_sequence = getattr(px.colors.sequential, color_sequence, None)
    
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        hole=hole,
        color_discrete_sequence=color_sequence
    )
    
    if show_labels:
        fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    orientation: str = 'v',
    color_scale: str = 'Blues',
    height: int = 400,
    categorical_order: Optional[List[str]] = None,
    x_title: Optional[str] = None,
    y_title: Optional[str] = None
) -> go.Figure:
    """
    Create a vertical or horizontal bar chart.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        color_scale: Color scale name
        height: Chart height
        categorical_order: Optional list for category ordering
        x_title: X-axis title
        y_title: Y-axis title
        
    Returns:
        Plotly Figure
    """
    color_sequence = COLOR_SCHEMES.get(color_scale, color_scale)
    if isinstance(color_sequence, str):
        color_sequence = getattr(px.colors.sequential, color_sequence, None)
    
    fig = px.bar(
        df,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        title=title,
        color_discrete_sequence=color_sequence,
        orientation=orientation
    )
    
    if categorical_order:
        if orientation == 'v':
            fig.update_xaxes(categoryorder='array', categoryarray=categorical_order)
        else:
            fig.update_yaxes(categoryorder='array', categoryarray=categorical_order)
    
    fig.update_layout(
        height=height,
        xaxis_title=x_title or x_col,
        yaxis_title=y_title or y_col,
        showlegend=False
    )
    
    return fig


def create_horizontal_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_scale: str = 'Blues',
    height: int = 600
) -> go.Figure:
    """
    Create a horizontal bar chart (convenience function).
    
    Args:
        df: Input DataFrame
        x_col: Column for values (horizontal axis)
        y_col: Column for categories (vertical axis)
        title: Chart title
        color_scale: Color scale name
        height: Chart height
        
    Returns:
        Plotly Figure
    """
    return create_bar_chart(
        df, y_col, x_col, title,
        orientation='h',
        color_scale=color_scale,
        height=height
    )


def create_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    height: int = 500,
    fill_area: bool = False,
    color: str = 'lightblue',
    x_title: Optional[str] = None,
    y_title: Optional[str] = None,
    hovermode: str = 'x unified'
) -> go.Figure:
    """
    Create a line chart.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        title: Chart title
        height: Chart height
        fill_area: Whether to fill area under line
        color: Line color
        x_title: X-axis title
        y_title: Y-axis title
        hovermode: Hover mode
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    trace_kwargs = {
        'x': df[x_col],
        'y': df[y_col],
        'mode': 'lines',
        'name': y_col,
        'line': dict(color=color, width=2)
    }
    
    if fill_area:
        trace_kwargs['fill'] = 'tozeroy'
        trace_kwargs['fillcolor'] = f'rgba(173, 216, 230, 0.3)'
    
    fig.add_trace(go.Scatter(**trace_kwargs))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_title or x_col,
        yaxis_title=y_title or y_col,
        height=height,
        hovermode=hovermode
    )
    
    return fig


def create_dual_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y1_col: str,
    y2_col: str,
    y1_name: str,
    y2_name: str,
    title: str,
    height: int = 500,
    fill_y1: bool = True,
    y1_color: str = 'lightblue',
    y2_color: str = 'darkblue'
) -> go.Figure:
    """
    Create a line chart with two Y-axis traces.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y1_col: First y-axis column
        y2_col: Second y-axis column
        y1_name: Name for first trace
        y2_name: Name for second trace
        title: Chart title
        height: Chart height
        fill_y1: Whether to fill area under first trace
        y1_color: Color for first trace
        y2_color: Color for second trace
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # First trace
    trace1_kwargs = {
        'x': df[x_col],
        'y': df[y1_col],
        'mode': 'lines',
        'name': y1_name,
        'line': dict(color=y1_color, width=1)
    }
    
    if fill_y1:
        trace1_kwargs['fill'] = 'tozeroy'
        trace1_kwargs['fillcolor'] = f'rgba(173, 216, 230, 0.3)'
    
    fig.add_trace(go.Scatter(**trace1_kwargs))
    
    # Second trace
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        mode='lines',
        name=y2_name,
        line=dict(color=y2_color, width=3)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title='Number of Messages',
        hovermode='x unified',
        height=height
    )
    
    return fig


def create_grouped_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    y_names: List[str],
    colors: List[str],
    title: str,
    height: int = 400,
    barmode: str = 'group'
) -> go.Figure:
    """
    Create a grouped bar chart with multiple traces.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_cols: List of columns for y-axis
        y_names: Names for each trace
        colors: Colors for each trace
        title: Chart title
        height: Chart height
        barmode: Bar mode ('group', 'stack', 'overlay')
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    for y_col, name, color in zip(y_cols, y_names, colors):
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=name,
            marker_color=color
        ))
    
    fig.update_layout(
        title=title,
        barmode=barmode,
        height=height,
        xaxis_title=x_col,
        yaxis_title='Time (minutes)'
    )
    
    return fig


def create_area_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color: str = '#636EFA',
    height: int = 400
) -> go.Figure:
    """
    Create an area chart.
    
    Args:
        df: Input DataFrame
        x_col: Column for x-axis
        y_col: Column for y-axis
        title: Chart title
        color: Fill color
        height: Chart height
        
    Returns:
        Plotly Figure
    """
    fig = px.area(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        height=height,
        xaxis_title=x_col,
        yaxis_title='Messages',
        showlegend=False
    )
    
    return fig


def create_heatmap(
    matrix: pd.DataFrame,
    x_labels: Optional[List] = None,
    y_labels: Optional[List] = None,
    title: str = 'Heatmap',
    colorscale: str = 'YlOrRd',
    show_text: bool = False,
    height: int = 500,
    reverse_y: bool = False
) -> go.Figure:
    """
    Create a heatmap.
    
    Args:
        matrix: Data matrix (pandas DataFrame or 2D array)
        x_labels: Labels for x-axis
        y_labels: Labels for y-axis
        title: Chart title
        colorscale: Color scale name
        show_text: Whether to show values as text
        height: Chart height
        reverse_y: Whether to reverse y-axis
        
    Returns:
        Plotly Figure
    """
    if colorscale in COLOR_SCHEMES:
        colorscale = COLOR_SCHEMES[colorscale]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values if isinstance(matrix, pd.DataFrame) else matrix,
        x=x_labels or (matrix.columns if isinstance(matrix, pd.DataFrame) else None),
        y=y_labels or (matrix.index if isinstance(matrix, pd.DataFrame) else None),
        colorscale=colorscale,
        showscale=True
    ))
    
    if show_text:
        fig.update_traces(
            text=matrix.values if isinstance(matrix, pd.DataFrame) else matrix,
            texttemplate='%{text}',
            textfont=dict(size=10)
        )
    
    layout_kwargs = {
        'title': title,
        'height': height
    }
    
    if reverse_y:
        layout_kwargs['yaxis'] = dict(autorange='reversed')
    
    fig.update_layout(**layout_kwargs)
    
    return fig


def create_calendar_heatmap(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    title: str = 'Activity Calendar',
    height: int = 300
) -> go.Figure:
    """
    Create a GitHub-style calendar heatmap.
    
    Args:
        df: DataFrame with dates and values
        date_col: Column containing dates
        value_col: Column containing values
        title: Chart title
        height: Chart height
        
    Returns:
        Plotly Figure
    """
    # Prepare data
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['Week'] = df[date_col].dt.isocalendar().week  # type: ignore
    df['Year'] = df[date_col].dt.year  # type: ignore
    df['Weekday'] = df[date_col].dt.dayofweek  # type: ignore
    df['YearWeek'] = df['Year'].astype(str) + '-W' + df['Week'].astype(str).str.zfill(2)
    
    # Create pivot
    calendar_pivot = df.pivot_table(
        index='Weekday',
        columns='YearWeek',
        values=value_col,
        fill_value=0
    )
    
    # Create hover text
    hover_text = []
    for weekday in range(7):
        row_text = []
        for yearweek in calendar_pivot.columns:
            matching = df[(df['YearWeek'] == yearweek) & (df['Weekday'] == weekday)]
            if not matching.empty:
                date = matching.iloc[0][date_col].strftime('%Y-%m-%d')
                count = int(matching.iloc[0][value_col])
                row_text.append(f"{date}<br>{count} messages")
            else:
                row_text.append("")
        hover_text.append(row_text)
    
    fig = go.Figure(data=go.Heatmap(
        z=calendar_pivot.values,
        x=calendar_pivot.columns,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=COLOR_SCHEMES['github'],
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=hover_text,
        showscale=True,
        colorbar=dict(title="Messages")
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Week",
        yaxis_title="Day of Week",
        height=height,
        xaxis=dict(
            tickangle=-45,
            tickmode='linear',
            tick0=0,
            dtick=max(1, len(calendar_pivot.columns) // 20)
        ),
        yaxis=dict(autorange='reversed')
    )
    
    return fig
