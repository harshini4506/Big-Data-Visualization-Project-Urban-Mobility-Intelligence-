import plotly.express as px

COLORS = ["#07599f", "#f4c542", "#23a26d", "#e05d44", "#7c5cff"]

def line(frame, x, y, title):
    figure = px.line(frame, x=x, y=y, title=title, template="plotly_white", color_discrete_sequence=COLORS)
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", hoverlabel=dict(bgcolor="#172033", font_color="#ffffff"))
    figure.update_xaxes(showgrid=False, linecolor="#d6e0eb")
    figure.update_yaxes(gridcolor="#e8eef5", linecolor="#d6e0eb")
    return figure

def bar(frame, x, y, title):
    figure = px.bar(frame, x=x, y=y, title=title, template="plotly_white", color_discrete_sequence=COLORS)
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", hoverlabel=dict(bgcolor="#172033", font_color="#ffffff"))
    figure.update_xaxes(showgrid=False, linecolor="#d6e0eb")
    figure.update_yaxes(gridcolor="#e8eef5", linecolor="#d6e0eb")
    return figure

def histogram(frame, x, title):
    figure = px.histogram(frame, x=x, title=title, template="plotly_white", color_discrete_sequence=COLORS)
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", hoverlabel=dict(bgcolor="#172033", font_color="#ffffff"))
    figure.update_xaxes(showgrid=False, linecolor="#d6e0eb")
    figure.update_yaxes(gridcolor="#e8eef5", linecolor="#d6e0eb")
    return figure

def donut(frame, names, values, title):
    figure = px.pie(frame, names=names, values=values, title=title, hole=.58, template="plotly_white", color_discrete_sequence=COLORS)
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", showlegend=True)
    return figure

def scatter(frame, x, y, title, size=None):
    figure = px.scatter(frame, x=x, y=y, size=size, title=title, opacity=.55, template="plotly_white", color_discrete_sequence=[COLORS[0]])
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
    figure.update_xaxes(showgrid=False, linecolor="#d6e0eb")
    figure.update_yaxes(gridcolor="#e8eef5", linecolor="#d6e0eb")
    return figure

def box(frame, x, y, title):
    figure = px.box(frame, x=x, y=y, title=title, points=False, template="plotly_white", color_discrete_sequence=COLORS)
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
    return figure

def heatmap(frame, x, y, z, title):
    figure = px.density_heatmap(frame, x=x, y=y, z=z, histfunc="avg", text_auto=".0f", title=title, template="plotly_white", color_continuous_scale=["#eef6ff", "#07599f", "#172033"])
    figure.update_layout(font=dict(color="#172033"), title_font=dict(color="#172033"), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
    return figure
