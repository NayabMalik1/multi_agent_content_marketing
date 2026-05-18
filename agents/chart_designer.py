import matplotlib.pyplot as plt
import io
import base64
from llm_helper import ask_llm

class ChartDesignerAgent:
    name = "Chart Designer"

    def run(self, research: dict) -> dict:
        """
        Generate charts/graphs based on topic instead of stock images
        """
        topic = research.get("outline", "")[:100]
        
        # Ask LLM for chart suggestions
        prompt = f"""
        For this blog topic: "{topic}"
        
        Suggest 2 types of charts/graphs that would be relevant:
        - Chart 1: (e.g., bar chart showing growth, pie chart for distribution)
        - Chart 2: (e.g., line chart for trends, comparison chart)
        
        Return ONLY valid JSON:
        {{
            "chart1": {{"title": "...", "type": "bar/pie/line", "data": {{"labels": ["A","B"], "values": [10,20]}}}},
            "chart2": {{"title": "...", "type": "bar/pie/line", "data": {{"labels": ["X","Y"], "values": [30,40]}}}}
        }}
        """
        
        raw = ask_llm(prompt)
        charts_data = self._parse_chart_data(raw)
        
        # Generate actual charts
        chart_htmls = []
        for i, chart in enumerate(charts_data, 1):
            img_base64 = self._generate_chart(chart)
            if img_base64:
                chart_htmls.append(f"""
                <figure style="margin:2rem 0;text-align:center;">
                    <img src="data:image/png;base64,{img_base64}" 
                         alt="{chart.get('title', 'Chart')}"
                         style="max-width:100%;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.12);" />
                    <figcaption style="color:#666;font-size:0.875rem;margin-top:0.5rem;">
                        {chart.get('title', f'Figure {i}')}
                    </figcaption>
                </figure>
                """)
        
        return {
            "html_embeds": "\n".join(chart_htmls),
            "charts_count": len(chart_htmls)
        }
    
    def _parse_chart_data(self, raw: str) -> list:
        import json
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(clean)
            return [data.get("chart1", {}), data.get("chart2", {})]
        except:
            # Fallback mock data
            return [
                {"title": "Market Growth Trend", "type": "line", "data": {"labels": ["2022", "2023", "2024", "2025"], "values": [100, 150, 225, 340]}},
                {"title": "Category Distribution", "type": "pie", "data": {"labels": ["Category A", "Category B", "Category C"], "values": [45, 35, 20]}}
            ]
    
    def _generate_chart(self, chart: dict) -> str:
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            chart_type = chart.get("type", "bar").lower()
            data = chart.get("data", {})
            labels = data.get("labels", ["A", "B", "C"])
            values = data.get("values", [30, 50, 20])
            
            if chart_type == "bar":
                ax.bar(labels, values, color='#4f46e5')
                ax.set_ylabel('Value')
            elif chart_type == "pie":
                ax.pie(values, labels=labels, autopct='%1.1f%%', colors=['#4f46e5', '#7c3aed', '#a855f7'])
            else:  # line
                ax.plot(labels, values, marker='o', color='#4f46e5', linewidth=2)
                ax.fill_between(range(len(labels)), values, alpha=0.3, color='#4f46e5')
                ax.set_ylabel('Value')
            
            ax.set_title(chart.get("title", "Chart"), fontsize=12, fontweight='bold')
            ax.set_facecolor('#fafaf8')
            fig.patch.set_facecolor('#fafaf8')
            
            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return img_base64
        except Exception as e:
            print(f"Chart generation error: {e}")
            return ""