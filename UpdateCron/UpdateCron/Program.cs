using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Linq;

namespace UpdateCron
{
    /*
cron:
- description: Daily Backup
  url: /_ah/datastore_admin/backup.create?name=BackupToCloud&kind=CustomerNote&kind=FieldApplicationEntry&kind=FieldApplicationUser&kind=SurveySlotBlock&kind=OfficeLocation&kind=SlotDateException&kind=SurveyBooking&kind=DeletedSurveyBooking&kind=PersonToNotify&kind=Notification&kind=KeyValueStoreItem&kind=Survey&kind=SurveyQuestion&kind=SurveyResponse&kind=PerfectPacketEntry&kind=PerfectPacketSubmission&kind=PerfectPacketApproval&kind=MonetaryTransaction&kind=SheetDataItem&kind=CustomerProgressItem&kind=CustomerProgressArchive&kind=CustomerNote&kind=Message&kind=MessageThread&kind=CustomerProposalInfo&kind=CustomerProgressV2Item&kind=CustomerProgressV2Archive&kind=ContestItem&kind=PanelAssessment&kind=ComposedDocument&kind=LeaderBoardStat&kind=ThirdPartyFolder&kind=AuthKey&kind=CreditCheck&kind=PlanSetDetails&kind=RepGoal&kind=ScheduledSMS&kind=SurveyDetails&kind=TrainingMedia&kind=Quiz&kind=QuizQuestion&kind=PowerUp&kind=PowerUpSignOff&kind=ToDoItem&kind=CalendarEvent&filesystem=gs&gs_bucket_name=devnpfieldapp2_datastore_backups
  schedule: every 48 hours
  target: ah-builtin-python-bundle*/
    class Program
    {
        static void Main(string[] args)
        {
            var path_components = Directory.GetCurrentDirectory().Split(Path.DirectorySeparatorChar).ToList();
            var app_id = path_components.Last();
            app_id = app_id.Replace(Path.DirectorySeparatorChar.ToString(), "");
            var app_id_schedule_mapping = new Dictionary<string, int>
            {
                {"devnpfieldapp", 48},
                {"devnpfieldapp2", 48},
                {"npfieldapp", 24}
            };
            var path = Directory.GetCurrentDirectory();
            if(path[path.Length - 1] == Path.DirectorySeparatorChar)
            {
                path = path.Substring(0, path.Length - 1);
            }
            var post_fix_file_path = path + Path.DirectorySeparatorChar.ToString() + "classes" + Path.DirectorySeparatorChar.ToString() + "postfix.py";

            var sb = new StringBuilder();
            sb.AppendLine("cron:");
            sb.AppendLine("- description: Daily Backup");

            var url = new StringBuilder();
            url.Append("/_ah/datastore_admin/backup.create?name=BackupToCloud");

            var postfix_content = File.ReadAllText(post_fix_file_path);
            postfix_content = postfix_content.Replace("#composition based ndb classes come first", "");
            var subbed = postfix_content.Substring(0, postfix_content.IndexOf("]"));
            subbed = subbed.Replace("ndb_entity_names = [", "");
            subbed = subbed.Replace("\r", "");
            var entities = subbed.Split("\n");
            entities.ToList().ForEach((entity) =>
            {                
                var e = entity.Replace(",", "");
                e = e.Replace("\"", "");
                e = e.Replace("'", "");
                e = e.Trim();
                if(e.Length > 0)
                {
                    url.Append("&kind=" + e);
                }
            });
            url.Append("&filesystem=gs&gs_bucket_name=" + app_id + "_datastore_backups");

            sb.AppendLine("  url: " + url.ToString());
            sb.AppendLine("  schedule: every " + app_id_schedule_mapping[app_id].ToString() + " hours");
            sb.AppendLine("  target: ah-builtin-python-bundle");

            var cron_file_path = path + Path.DirectorySeparatorChar.ToString() + "cron.yaml";
            File.WriteAllText(cron_file_path, sb.ToString());

        }
    }
}
