from services.analytics_service import AnalyticsService

class InsightsService:
    @staticmethod
    def generate_ai_insights():
        insights_text = []
        
        # Risk Insights
        risks = AnalyticsService.identify_at_risk_students()
        high_risk = [r for r in risks if r['risk'] == 'High Risk']
        if len(high_risk) > 0:
            insights_text.append(f"⚠️ {len(high_risk)} students are at high risk of academic probation due to poor SGPA or multiple arrears.")
        else:
            insights_text.append("✅ The class shows healthy academic retention with 0 high-risk students.")
            
        # Subject Insights
        diff = AnalyticsService.calculate_subject_difficulty()
        if diff:
            hardest = max(diff.items(), key=lambda x: x[1]['difficulty_score'])
            insights_text.append(f"📚 '{hardest[0]}' shows the highest failure rate and may require academic intervention (Pass %: {hardest[1]['pass_percent']}%).")
            
        # Faculty Insights
        fac = AnalyticsService.evaluate_faculty_performance()
        if fac:
            top_fac = max(fac.items(), key=lambda x: x[1]['pass_percent'])
            insights_text.append(f"🏆 Faculty '{top_fac[0]}' holds the highest pass percentage ({top_fac[1]['pass_percent']}%) across their subjects.")
            
        if not insights_text:
            return ["No data available to generate insights yet. Please import data."]
            
        return insights_text
