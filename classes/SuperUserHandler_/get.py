def get(self):
    self.session = get_current_session()
    try:
        if str(self.session["user_name"]) == "" or str(self.session["user_type"]) != "super":
            self.session.non_existent_method("foo", "bar")

        template_values = {}
        template_values["user_name"] = str(self.session["user_name"])
        template_values["user_identifier"] = self.session["user_identifier"]
        template_values["app_bucket"] = app_identity.get_default_gcs_bucket_name()
        path = Helpers.get_html_path('super.html')

        office_data = {}
        office_data["offices"] = []
        office_locations = OfficeLocation.query(OfficeLocation.is_parent == False)
        for item in office_locations:
            office_item = {}
            office_item["name"] = item.name
            office_item["identifier"] = item.identifier
            office_item["slot_data"] = {}

            office_data["offices"].append(office_item)

        notifications = Notification.query(Notification.identifier != "")
        office_data["notifications"] = []
        for notification in notifications:
            notification_item = {}
            notification_item["identifier"] = notification.identifier
            notification_item["action_name"] = notification.action_name
            notification_item["notification_list"] = []

            for list_item in notification.notification_list:
                person = {}
                person["identifier"] = list_item.identifier
                person["email_address"] = list_item.email_address
                notification_item["notification_list"].append(person)

            office_data["notifications"].append(notification_item)

        admins = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.user_type == "super",
                FieldApplicationUser.current_status == 0
            )
        )
        admin_data = []
        for admin in admins:
            obj = {"identifier": admin.identifier, "name": admin.first_name.strip().title() + " " + admin.last_name.strip().title()}
            obj["lowered"] = obj["name"].lower()
            admin_data.append(obj)
        admin_data = Helpers.bubble_sort(admin_data, "lowered")
        template_values["admins"] = json.dumps(admin_data)

        project_managers = []
        pms = FieldApplicationUser.query(
            ndb.AND
            (
                FieldApplicationUser.current_status == 0,
                FieldApplicationUser.is_project_manager == True
            )
        )
        for pm in pms:
            project_managers.append({"identifier": pm.identifier, "name": pm.first_name.strip().title() + " " + pm.last_name.strip().title()})

        template_values["project_managers"] = json.dumps(project_managers)
        template_values["office_json"] = json.dumps(office_data)
        menu_item_click_handlers = [
            {
                "id": "manage_offices",
                "fn": "manageOffices",
                "name": "Offices & Markets"
            },
            {
                "id": "surveys",
                "fn": "showSurveyScreen",
                "name": "Legacy Surveys Screen"
            },
            {
                "id": "manage_third_party_creds",
                "fn": "manageThirdPartyCredentials",
                "name": "Manage Third Party Credentials"
            },
            {
                "id": "customer_notes",
                "fn": "customerNotesSearch",
                "name": "Customer Notes"
            },
            {
                "id": "customer_progress",
                "fn": "showCustomerProgress",
                "name": "Customer Progress"
            },
            {
                "id": "add_survey_appt",
                "fn": "showSurveyScheduler",
                "name": "Show Survey Scheduler"
            },
            {
                "id": "kill_survey_btn",
                "fn": "showCancelAppointment",
                "name": "Show Cancelled Appointments"
            },
            {
                "id": "manage_notifications_and_settings",
                "fn": "manageNotificationsAndSettings",
                "name": "Manage Notifications & Settings"
            },
            {
                "id": "upcoming_view",
                "fn": "showRecentCustomers",
                "name": "Credits"
            },
            {
                "id": "qual_card_search",
                "fn": "showQualCardSearch",
                "name": "Qual Card/Document Search"
            },
            {
                "id": "ledger",
                "fn": "showLedger",
                "name": "Ledger"
            },
            {
                "id": "perfect_packet",
                "fn": "showPerfectPacket",
                "name": "Perfect Packets"
            },
            {
                "id": "apps_script_settings",
                "fn": "loadAppsScriptSettingsScreen",
                "name": "Apps Script Settings"
            },
            {
                "id": "rep_assist",
                "fn": "repAssist",
                "name": "Rep Assist"
            },
            {
                "id": "checklist_builder",
                "fn": "manageChecklists",
                "name": "Checklist Builder"
            },
            {
                "id": "payscale_editor",
                "fn": "editPayscales",
                "name": "Payscale Editor"
            },
            {
                "id": "edit_funding_sources",
                "fn": "editFundingSources",
                "name": "Edit Funding Sources"
            },
            {
                "id": "employee_directory",
                "fn": "showEmployeeDirectory",
                "name": "Employee Directory"
            },
            {
                "id": "inbox",
                "fn": "loadInbox",
                "name": "Messaging"
            },
            {
                "id": "assume_session",
                "fn": "promptForSessionAssumption",
                "name": "Assume User's Credentials"
            },
            {
                "id": "leaderboard",
                "fn": "showLeaderBoard",
                "name": "Leaderboard"
            },
            {
                "id": "proposal_gen",
                "fn": "showProposalSearchBox",
                "name": "Legacy Proposal Search Box"
            },
            {
                "id": "missing_packets",
                "fn": "missingPacketTool",
                "name": "Missing Packet Tool"
            },
            {
                "id": "customer_progress_v2",
                "fn": "showCustomerProgressV2",
                "name": "Customer Progress V2"
            },
            {
                "id": "manage_contests",
                "fn": "manageContests",
                "name": "Manage Contests"
            },
            {
                "id": "recent_customers",
                "fn": "showRecentCustomers",
                "name": "Recent Customers"
            },
            {
                "id": "swap_customer_office",
                "fn": "swapCustomerOffice",
                "name": "Swap Customer Offices"
            },
            {
                "id": "swap_customers",
                "fn": "reassignCustomers",
                "name": "Reassign Customer Ownership"
            },
            {
                "id": "view_proposals",
                "fn": "loadPendingProposals",
                "name": "Proposals"
            },
            {
                "id": "panel_assessment_tab",
                "fn": "showPanelAssessments",
                "name": "Panel Assessments"
            },
            {
                "id": "new_perfect_packet",
                "fn": "perfectPacketV2",
                "name": "Perfect Packet V2"
            },
            {
                "id": "solar_ready",
                "fn": "showSolarReadyTab",
                "name": "Surveys"
            },
            {
                "id": "permit_design",
                "fn": "permitDesignTab",
                "name": "Legacy Permit Design"
            },
            {
                "id": "permit_design_v2",
                "fn": "permitDesignTabV2",
                "name": "Permit Design"
            },
            {
                "id": "titan_management",
                "fn": "manageTitan",
                "name": "Titan Status"
            },
            {
                "id": "docs_composer",
                "fn": "loadDocsComposer",
                "name": "Docs Composer"
            },
            {
                "id": "team_btn",
                "fn": "loadTeamView",
                "name": "Legacy Team View"
            },
            {
                "id": "incomplete_proposals_view",
                "fn": "showIncompleteProposals",
                "name": "Incomplete Proposals"
            },
            {
                "id": "pwork_btn",
                "fn": "showPanelWorkView",
                "name": "Legacy Panel Work"
            },
            {
                "id": "slides_maker",
                "fn": "slideMaker",
                "name": "Presentation Tools"
            },            
            {
                "id": "project_management_v2",
                "fn": "showProjectManagementTabV2",
                "name": "Project Management V2"
            },
            {
                "id": "payroll_tab",
                "fn": "showPayrollTab",
                "name": "Payroll"
            },
            {
                "id": "data_to_go",
                "fn": "dataToGo",
                "name": "Data to Go"
            },
            {
                "id": "archived_customers",
                "fn": "showArchivedCustomers",
                "name": "Archived Customers"
            },
            {
                "id": "save_me_view",
                "fn": "showSaveMes",
                "name": "Save Me Customers"
            },
            {
                "id": "admin_accounts_and_provisioning",
                "fn": "provisionAdminAccounts",
                "name": "Admin Accounts Provisioning"
            },
            {
                "id": "bulk_sms",
                "fn": "bulkSMSTool",
                "name": "Bulk SMS Tool"
            },
            {
                "id": "training_media",
                "fn": "editTrainingMedia",
                "name": "Rep Training Media"
            },
            {
                "id": "power_up_sign_off",
                "fn": "powerUpSignOff",
                "name": "Power-Up Signoff"
            },
            {
                "id": "to_do_trigger",
                "fn": "loadToDoList",
                "name": "To-Do List"
            },
            {
                "id": "pm_calendar",
                "fn": "loadPMCalendar",
                "name": "Ops Calendar"
            },
            {
                "id": "breadcrumbs",
                "fn": "BreadCrumbIframe",
                "name": "Canvassing App Breadcrumbs"
            },
            {
                "id": "leads",
                "fn": "loadLeads",
                "name": "Leads"
            },
            {
                "id": "rep_sp2_schedule",
                "fn": "viewRepSP2Schedule",
                "name": "Rep SP2 Calendar"
            },
            {
                "id": "pending_registrations",
                "fn": "viewPendingRegistrations",
                "name": "Pending Registrations"
            },
            {
                "id": "marketing_media",
                "fn": "marketingMedia",
                "name": "Marketing Media"
            },
            {
                "id": "grid_area_management",
                "fn": "gridRegionAdministration",
                "name": "Area Management"
            },
            {
                "id": "payroll_v3",
                "fn": "showPayrollTabV3",
                "name": "Payroll V3"
            },
            {
                "id": "accounts_receivable",
                "fn": "accountsReceivable",
                "name": "Accounts Receivable"
            },
            {
                "id": "true_hks",
                "fn": "trueHKS",
                "name": "True HKs"
            },
            {
                "id": "solar_reader_management",
                "fn": "manageSolarReaders",
                "name": "Solar Reader Inventory"
            },
            {
                "id": "runway",
                "fn": "runWay",
                "name": "Runway"
            },
            {
                "id": "ak_pay",
                "fn": "pendingAKs",
                "name": "AK Pay"
            },
            {
                "id": "carve_out",
                "fn": "carveOut",
                "name": "Carve Out"
            },
            {
                "id": "cd_pay",
                "fn": "cdPay",
                "name": "Solar Pro CD Pay"
            }
        ]
        template_values["menu_item_click_handlers"] = json.dumps(menu_item_click_handlers)
        template_values["allowed_functions"] = "[]"

        user = FieldApplicationUser.first(FieldApplicationUser.identifier == self.session["user_identifier"])
        if not user is None:
            template_values["allowed_functions"] = user.allowed_functions

        to_do_users = FieldApplicationUser.query(
            ndb.AND(
                FieldApplicationUser.user_type == "super",
                FieldApplicationUser.current_status == 0
            )
        )
        t_d_users = []
        for t in to_do_users:
            allowed_fns = json.loads(t.allowed_functions)
            if "to_do_trigger" in allowed_fns:
                t_d_users.append({"name": t.first_name.strip().title() + " " + t.last_name.strip().title(), "identifier": t.identifier})
        template_values["to_do_users"] = json.dumps(t_d_users)

        self.response.out.write(template.render(path, template_values))
    except:
        self.response.out.write("**")

