import webapp2
import copy

configuration = {}
configuration["customer_progress_v2"] = True
configuration["operation_mode"] = "DEV"
configuration["compute_engine_ip"] = "35.185.228.87"
setattr(webapp2.RequestHandler, "configuration", configuration)
from classes import *

#tacking on the .first method to ndb.Model.
#returns the first item in the list or None if no results are found...

@classmethod
def first(self, params, throw_exception=False):
    query = self.query(params)
    for item in query:
        return item
    if throw_exception:
        raise ValueError("No such chicken nugget could be found hehe")
    return None

ndb.Model.first = first

def to_list(self):
    ret_list = []
    for item in self:
        atts = item.__dict__
        logging.info(atts)
        row = {}
        for k in atts.keys():
            if hasattr(item, k):
                prop = getattr(item, k)
                row[k] = getattr(item, k)
                #if not callable(prop):
            else:
                logging.info("item has no attribute of '" + k + "'")


        ret_list.append(row)

    return ret_list

ndb.Query.to_list = to_list


saltstr2 = Salt.default()

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': saltstr2,
}

app = webapp2.WSGIApplication(
    [
        ('/', IndexHandler),
#        ('/admin', AdminHandler),
        ('/API/(.*?)', APIHandler),
        ('/appt_confirmation/(.*?)/(.*?)', AppointmentConfirmationHandler),
        ('/AppWhitePages', AppWhitePagesHandler),
        ('/AppLogin',AppLoginHandler),
        ('/AppData',AppDataHandler),
        ('/AKR/(.*?)', AKRecorderHandler),
        ('/approve_user/(.*?)', ApproveRegistrationHandler),
        ('/auth/(.*?)', AuthHandler),
        ('/breadcrumbs/identifier/(.*?)/date/(.*?)/hour/(.*?)', BreadCrumbsHandler),
        ('/changepass', ChangePasswordHandler),
        ('/check_session', CheckSessionHandler),
        ('/comm/(.*?)', CustomerCommHandler),
        ('/commpeek/(.*?)/(.*?)/(.*?)', CCommViewer),
        ('/continue', ContinueFieldFormPostHandler),
        ('/continue_registration/(.*?)/(.*?)', RegistrationContinuationHandler),
        ('/creep', CreepHandler),
        ('/ct', CustomerTwilioCommunicationHandler),
        ('/data', JsonDataHandler),
        ('/data2', JsonDataHandlerV2),
        ('/DLWatch', DataLoggerWatchHandler),
        ('/doc_frame/(.*?)/(.*?)/(.*?)', DocFrameHandler),
        ('/emails/pause/(.*?)', EmailPauseHandler),
        ('/field', FieldHandlerV2),
        ('/gme/(.*?)/width/(.*?)/height/(.*?)', GMEmbedHandler),
        ('/ios', IOSInstallHandler),
        ('/ios_plist.plist', IOSPlistHandler),
        ('/ip_info', IPInformationHandler),
        ('/Kiosk/(.*?)', KioskHandler),
        ('/kv/(.*?)', KeyValueStoreHandler),
        ('/forgotpassword', ForgotPasswordHandler),
        ('/localstoragetest', LocalStorageTestHandler),
        ('/logout', LogoutHandler),
        ('/m_success', FieldFormMosaicSuccessHandler),
        ('/poll_form_workers', PollFormWorkersHandler),
        ('/PostalCampaignThread/(.*?)/(.*?)', PostalCampaignThreadHandler),
        ('/ppframe/(.*?)/width/(.*?)/height/(.*?)', ProfilePictureFrameHandler),
        ('/present/(.*?)/(.*?)/(.*?)/', PresentationHandler),
        ('/preview_survey', PreviewSurveyHandler),
        ('/reader_chart_gen', ChartGeneratorHandler),
        ('/registration', RegistrationHandler),
        ('/rep', RepPortalHandler),
        ('/sales', FieldHandlerV2),
        ('/sdocs', SearchDocsHandler),
        ('/seed_leaderboard', SeedLeaderboardHandler),
        ('/sheetsdata', SheetsDataHandler),
        ('/success', FieldFormSuccessHandler),
        ('/super', SuperUserHandler),
        ('/surveyor', SurveyorHandler),
        ('/tell_us/(.*?)', TellUsHandler),
        ('/tq/(.*?)', TaskQueueHandler),
        ('/continue', ContinueFieldFormPostHandler),
        ('/continue2', ContinueFieldFormPost2Handler),
        ('/continue3', ContinueFieldFormPost3Handler),
        ('/continue4', ContinueFieldFormPost4Handler),
        ('/continue5', ContinueFieldFormPost5Handler),
        ('/continue6', ContinueFieldFormPost6Handler),
        ('/sign/(.*?)', SignHandler),
        ('/success', FieldFormSuccessHandler),
        ('/success2', FieldFormSuccess2Handler),
        ('/talent', TalentHandler),
        ('/twilio/incoming', TwilioIncomingHandler),
        ('/videotest', BrowserVideoTestHandler)
    ]
)

