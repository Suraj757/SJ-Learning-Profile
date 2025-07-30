import plotly.graph_objects as go
from utils.questions import CATEGORIES

def create_radar_chart(scores):
    """Create a radar chart visualization of the scores."""
    try:
        # Input validation
        if not isinstance(scores, dict) or not scores:
            raise ValueError("Invalid scores provided")

        # Convert scores to numeric values
        score_values = {
            "High": 3,
            "Medium": 2,
            "Low": 1
        }

        # Category colors from the Begin brand
        category_colors = {
            "Communication": "#66B2FF",
            "Collaboration": "#FF9999",
            "Content": "#99FF99",
            "Critical Thinking": "#FFCC99",
            "Creative Innovation": "#FF99CC",
            "Confidence": "#99CCFF"
        }

        # Get categories and values in a consistent order
        categories = list(scores.keys())
        # Convert long category names to have line breaks for better display
        display_categories = []
        for cat in categories:
            if cat == "Critical Thinking":
                display_categories.append("Critical<br>Thinking")
            elif cat == "Communication":
                display_categories.append("Communi-<br>cation")
            elif cat == "Creative Innovation":
                display_categories.append("Creative<br>Innovation")
            else:
                display_categories.append(cat)
                
        values = [score_values[scores[cat]] for cat in categories]
        
        # Create a more vibrant, interactive chart
        fig = go.Figure()

        # Add main trace for scores
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=display_categories + [display_categories[0]],  # Close the polygon, use display_categories
            fill='toself',
            name='Current Profile',
            line=dict(color='rgb(0, 147, 130)', width=3),
            fillcolor='rgba(0, 147, 130, 0.3)',
            hoverinfo='text',
            hovertext=[f"{cat}: {scores[cat]}" for cat in categories] + [f"{categories[0]}: {scores[categories[0]]}"],
            mode='lines+markers',
            marker=dict(
                size=10,
                color='rgb(0, 147, 130)',
                line=dict(width=2, color='white')
            )
        ))
        
        # Add separate traces for each point to enable interactive hovering
        for i, cat in enumerate(categories):
            fig.add_trace(go.Scatterpolar(
                r=[values[i]],
                theta=[display_categories[i]],
                mode='markers',
                marker=dict(
                    size=12,
                    color=category_colors.get(cat, 'rgb(0, 147, 130)'),
                    line=dict(width=2, color='white'),
                    symbol='circle'
                ),
                hoverinfo='text',
                hovertext=f"<b>{cat}</b><br>{scores[cat]}",
                showlegend=False
            ))

        # Update layout with more engaging style
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3.2],  # Slightly larger range to fit labels
                    ticktext=['', 'Emerging', 'Growing', 'Strong'],
                    tickvals=[0, 1, 2, 3],
                    tickfont=dict(size=12, family="Inter, sans-serif"),
                    tickangle=0,
                    linecolor='rgba(0,0,0,0.2)',
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    ticktext=display_categories,
                    tickfont=dict(size=14, family="Inter, sans-serif", color="#2D3142"),
                    linecolor='rgba(0,0,0,0.2)',
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            margin=dict(t=30, b=30, l=80, r=80),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter, sans-serif"
            )
        )

        return fig

    except Exception as e:
        raise ValueError(f"Error creating radar chart: {str(e)}")
        
def create_progress_chart(assessments):
    """Create a chart showing progress across multiple assessments."""
    try:
        # Validate input
        if not assessments or len(assessments) < 2:
            return None
            
        # Convert score labels to numeric values for charting
        score_values = {
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        
        # Prepare data for chart
        dates = []
        progress_data = {}
        
        # Initialize categories based on first assessment
        categories = list(assessments[0]['scores'].keys())
        for category in categories:
            progress_data[category] = []
        
        # Extract dates and scores
        for assessment in assessments:
            dates.append(assessment.get('created_at_formatted', 'Unknown'))
            for category in categories:
                if category in assessment['scores']:
                    score_label = assessment['scores'][category]
                    score_value = score_values.get(score_label, 0)
                    progress_data[category].append(score_value)
                else:
                    progress_data[category].append(0)
                    
        # Create figure
        fig = go.Figure()
        
        # Add a trace for each category
        category_colors = {
            "Communication": "#66B2FF",
            "Collaboration": "#FF9999",
            "Content": "#99FF99",
            "Critical Thinking": "#FFCC99",
            "Creative Innovation": "#FF99CC",
            "Confidence": "#99CCFF"
        }
        
        for category in categories:
            fig.add_trace(go.Scatter(
                x=dates,
                y=progress_data[category],
                mode='lines+markers',
                name=category,
                line=dict(
                    color=category_colors.get(category, 'rgb(0, 147, 130)'),
                    width=3
                ),
                marker=dict(
                    size=8,
                    line=dict(width=2, color='white')
                )
            ))
            
        # Update layout
        fig.update_layout(
            title="Learning Growth Over Time",
            xaxis=dict(
                title="Assessment Date",
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(
                title="Skill Level",
                ticktext=['Emerging', 'Growing', 'Strong'],
                tickvals=[1, 2, 3],
                range=[0.5, 3.5],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=80, b=60, l=60, r=30),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Inter, sans-serif"
            )
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating progress chart: {e}")
        return None