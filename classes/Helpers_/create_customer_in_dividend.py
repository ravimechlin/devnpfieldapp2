@staticmethod
def create_customer_in_dividend(app_entry, annual_income, monthly_mortgage, last_four):
    info = {}
    info["FirstName"] = app_entry.customer_first_name.strip().title()
    info["LastName"] = app_entry.customer_last_name.strip().title()
    info["Address"] = app_entry.customer_address
    info["City"] = app_entry.customer_city
    info["State"] = app_entry.customer_state
    info["Zip"] = app_entry.customer_postal
    info["Email"] = app_entry.customer_email
    info["Phone"] = Helpers.format_phone_number(app_entry.customer_phone)
    info["AnnualIncome"] = annual_income
    info["MonthlyMortgage"] = monthly_mortgage
    info["LastFour"] = last_four

    resp = urlfetch.fetch(
        url="http://35.185.228.87:8084/api/dividend",
        method=urlfetch.POST,
        payload=json.dumps(info),
        deadline=45,
        headers={},
        follow_redirects=True
    )
