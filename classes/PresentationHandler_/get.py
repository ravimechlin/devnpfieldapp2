def get(self, slide_identifier, entity_type, entity_identifier):
    if entity_type == "customer":
        slide = Slide.first(Slide.identifier == slide_identifier)
        if not slide is None:
            app_entry = FieldApplicationEntry.first(FieldApplicationEntry.identifier == entity_identifier)
            if not app_entry is None:
                booking = SurveyBooking.first(SurveyBooking.identifier == app_entry.booking_identifier)
                if not booking is None:
                    ol = OfficeLocation.first(OfficeLocation.identifier == app_entry.office_identifier)
                    if not ol is None:
                        market_key = ol.parent_identifier
                        pricing_structes = Helpers.get_pricing_structures()

                        import base64
                        template_data = {}
                        template_data["opts"] = slide.options
                        template_data["doc_title"] = "Presenting to " + app_entry.customer_first_name.strip().title() + " " + app_entry.customer_last_name.strip().title()
                        template_data["slides"] = json.dumps(slide.children(True))
                        template_data["slide_identifier"] = slide.identifier
                        template_data["entity_identifier"] = app_entry.identifier
                        template_data["entity_type"] = entity_type
                        template_data["customer_vars"] = json.dumps(Helpers.get_customer_presentation_variables(app_entry))
                        chart_data = {}
                        chart_data["customer"] = {}
                        chart_data["customer"]["usage_dollars"] = []
                        chart_data["customer"]["usage_kwhs"] = []
                        chart_data["customer"]["usage"] = json.loads(app_entry.usage_data)
                        for key in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
                            chart_data["customer"]["usage_dollars"].append(chart_data["customer"]["usage"][key]["dollars"])
                            chart_data["customer"]["usage_kwhs"].append(chart_data["customer"]["usage"][key]["kwhs"])

                        chart_data["customer"]["rate_percentage"] = Helpers.crunch("fx_Electricity_Rate_Change_Percentage", market_key, app_entry, booking, None, pricing_structes, [])

                        proposal = CustomerProposalInfo.first(CustomerProposalInfo.field_app_identifier == app_entry.identifier)
                        if not proposal is None:
                            proposal.fix_system_size()
                            proposal.fix_additional_amount()
                            chart_data["customer"]["proposal"] = json.loads(proposal.info)
                            chart_data["customer"]["total_kwhs"] = str(app_entry.total_kwhs)
                            chart_data["customer"]["total_dollars"] = str(app_entry.total_dollars)


                        template_data["chart_rendering_object"] = json.dumps(chart_data)
                        
                        path = Helpers.get_html_path("present.html")
                        self.response.out.write(template.render(path, template_data))
