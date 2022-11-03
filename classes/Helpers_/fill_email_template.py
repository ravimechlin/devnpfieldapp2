@staticmethod
def fill_email_template(pp_sub, app_entry, html, extension="n/a", installation_link="n/a", solar_warranty_link="n/a", inverter_warranty_link="n/a"):
    #html = unicode(html)
    info = json.loads(pp_sub.extra_info)
    installation_date = "n/a"
    pm_first_name = "n/a"
    pm_last_name = "n/a"
    pm_email = "noreply@newpower.net"
    pm_extension = extension
    customer_first_name = ""
    customer_last_name = ""


    keys = info.keys()
    if "project_management_checkoffs" in info.keys():
        if "install" in info["project_management_checkoffs"].keys():
            if "date" in info["project_management_checkoffs"]["install"].keys():
                if not info["project_management_checkoffs"]["install"]["date"] is None:
                    dt_vals = info["project_management_checkoffs"]["install"]["date"].split("-")
                    installation_date = dt_vals[1] + "/" + dt_vals[2] + "/" + dt_vals[0]

    if "project_manager" in info.keys():
        if(isinstance(info["project_manager"], dict)):
            pm_first_name = info["project_manager"]["name"].split(" ")[0]
            pm_last_name = info["project_manager"]["name"].split(" ")[1]
            pm_email = info["project_manager"]["email"]
        else:
            usr = FieldApplicationUser.first(FieldApplicationUser.identifier == info["project_manager"])
            if not usr is None:
                pm_first_name= usr.first_name.strip().title()
                pm_last_name = usr.last_name.strip().title()
                pm_email = usr.rep_email

    html = html.replace("{{ installation_date }}", str(installation_date))
    html = html.replace("{{ pm_first_name }}", str(pm_first_name))
    html = html.replace("{{ pm_last_name }}", str(pm_last_name))
    html = html.replace("{{ pm_email }}", str(pm_email))
    html = html.replace("{{ pm_extension }}", str(pm_extension))
    html = html.replace("{{ installation_link }}", installation_link)
    html = html.replace("{{ panel_warranty_link }}", solar_warranty_link)
    html = html.replace("{{ inverter_warranty_link }}", inverter_warranty_link)
    html = html.replace("{{ customer_first_name }}", str(app_entry.customer_first_name).strip().title())
    html = html.replace("{{ customer_last_name }}", str(app_entry.customer_last_name).strip().title())
    html = html.replace("\r", "")
    html = html.replace("\n", "<br />")
    return html
