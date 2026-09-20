from django.core.management.base import BaseCommand
from insight.models import Report
from insight.services.quality_grader import grade_and_reward_report

class Command(BaseCommand):
    help = 'Process all RAW reports, grade them, and award points'

    def handle(self, *args, **options):
        raw_reports = Report.objects.filter(status='RAW')
        count = raw_reports.count()
        self.stdout.write(f"🔍 Found {count} RAW reports to process...")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No RAW reports found. All good!"))
            return
        
        success_count = 0
        for report in raw_reports:
            try:
                # Set safe defaults if AI didn't run
                if not report.ai_urgency_level:
                    report.ai_urgency_level = 'MODERATE'
                if not report.ai_confidence_score:
                    report.ai_confidence_score = 0.5
                report.save(update_fields=['ai_urgency_level', 'ai_confidence_score'])
                
                # Run the grading function
                score, points = grade_and_reward_report(report)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ Processed report {str(report.id)[:8]}... | Score: {score} | Points: {points}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Failed to process {str(report.id)[:8]}...: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 MISSION ACCOMPLISHED! Successfully processed {success_count}/{count} reports!"))
