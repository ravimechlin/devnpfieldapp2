@staticmethod
def crunch(keyy, market_key, app_entry, booking, proposal, pricing_structures, funds):    
    d_pace_mapping = {"1":"106.86","2":"106.84","3":"106.83","4":"106.81","5":"106.79","6":"106.77","7":"106.76","8":"106.74","9":"106.72","10":"106.70","11":"106.69","12":"106.67","13":"106.65","14":"106.63","15":"106.62","16":"106.60","17":"106.58","18":"106.57","19":"106.55","20":"106.53","21":"106.51","22":"106.50","23":"106.48","24":"106.46","25":"106.44","26":"106.43","27":"106.41","28":"106.39","29":"106.38","30":"106.36","31":"106.36","32":"106.34","33":"106.32","34":"106.31","35":"106.29","36":"106.27","37":"106.25","38":"106.24","39":"106.22","40":"106.20","41":"106.19","42":"106.17","43":"106.15","44":"106.13","45":"106.12","46":"106.10","47":"106.08","48":"106.07","49":"106.05","50":"106.03","51":"106.01","52":"106.00","53":"105.98","54":"105.96","55":"105.95","56":"105.93","57":"105.91","58":"105.89","59":"105.88","60":"105.86","61":"105.84","62":"105.84","63":"105.83","64":"105.81","65":"105.79","66":"105.77","67":"105.76","68":"105.74","69":"105.72","70":"105.71","71":"105.69","72":"105.67","73":"105.66","74":"105.64","75":"105.62","76":"105.60","77":"105.59","78":"105.57","79":"105.55","80":"105.54","81":"105.52","82":"105.50","83":"105.49","84":"105.47","85":"105.45","86":"105.43","87":"105.42","88":"105.40","89":"105.38","90":"105.37","91":"105.35","92":"105.33","93":"105.32","94":"105.30","95":"105.28","96":"105.27","97":"105.25","98":"105.23","99":"105.21","100":"105.20","101":"105.18","102":"105.16","103":"105.15","104":"105.13","105":"105.11","106":"105.10","107":"105.08","108":"105.06","109":"105.05","110":"105.03","111":"105.01","112":"105.00","113":"104.98","114":"104.96","115":"104.95","116":"104.93","117":"104.91","118":"104.89","119":"104.88","120":"104.86","121":"104.84","122":"104.83","123":"104.83","124":"104.81","125":"104.79","126":"104.78","127":"104.76","128":"104.74","129":"104.73","130":"104.71","131":"104.69","132":"104.68","133":"104.66","134":"104.64","135":"104.63","136":"104.61","137":"104.59","138":"104.58","139":"104.56","140":"104.54","141":"104.53","142":"104.51","143":"104.49","144":"104.48","145":"104.46","146":"104.44","147":"104.43","148":"104.41","149":"104.39","150":"104.38","151":"104.36","152":"104.34","153":"104.33","154":"104.31","155":"104.29","156":"104.28","157":"104.26","158":"104.24","159":"104.23","160":"104.21","161":"104.19","162":"104.18","163":"104.16","164":"104.15","165":"104.13","166":"104.11","167":"104.10","168":"104.08","169":"104.06","170":"104.05","171":"104.03","172":"104.01","173":"104.00","174":"103.98","175":"103.96","176":"103.95","177":"103.93","178":"103.91","179":"103.90","180":"103.88","181":"103.86","182":"103.85","183":"103.83","184":"103.83","185":"103.82","186":"103.80","187":"103.78","188":"103.77","189":"103.75","190":"103.73","191":"103.72","192":"103.70","193":"103.68","194":"103.67","195":"103.65","196":"103.64","197":"103.62","198":"103.60","199":"103.59","200":"103.57","201":"103.55","202":"103.54","203":"103.52","204":"103.50","205":"103.49","206":"103.47","207":"103.46","208":"103.44","209":"103.42","210":"103.41","211":"103.39","212":"103.37","213":"103.36","214":"103.34","215":"103.34","216":"103.32","217":"103.31","218":"103.29","219":"103.28","220":"103.26","221":"103.24","222":"103.23","223":"103.21","224":"103.19","225":"103.18","226":"103.16","227":"103.15","228":"103.13","229":"103.11","230":"103.10","231":"103.08","232":"103.06","233":"103.05","234":"103.03","235":"103.02","236":"103.00","237":"102.98","238":"102.97","239":"102.95","240":"102.94","241":"102.92","242":"102.90","243":"102.85","244":"102.84","245":"102.82","246":"102.81","247":"102.79","248":"102.77","249":"102.76","250":"102.74","251":"102.73","252":"102.71","253":"102.69","254":"102.68","255":"102.66","256":"102.65","257":"102.63","258":"102.61","259":"102.60","260":"102.58","261":"102.57","262":"102.55","263":"102.53","264":"102.52","265":"102.50","266":"102.49","267":"102.47","268":"102.45","269":"102.44","270":"102.42","271":"102.41","272":"102.39","273":"102.37","274":"102.37","275":"102.36","276":"102.34","277":"102.33","278":"102.31","279":"102.29","280":"102.28","281":"102.26","282":"102.25","283":"102.23","284":"102.21","285":"102.20","286":"102.18","287":"102.17","288":"102.15","289":"102.13","290":"102.12","291":"102.10","292":"102.09","293":"102.07","294":"102.05","295":"102.04","296":"102.02","297":"102.01","298":"101.99","299":"101.98","300":"101.96","301":"101.94","302":"101.93","303":"101.91","304":"101.90","305":"101.88","306":"101.86","307":"101.85","308":"101.83","309":"101.82","310":"101.80","311":"101.79","312":"101.77","313":"101.75","314":"101.74","315":"101.72","316":"101.71","317":"101.69","318":"101.67","319":"101.66","320":"101.64","321":"101.63","322":"101.61","323":"101.60","324":"101.58","325":"101.56","326":"101.55","327":"101.53","328":"101.52","329":"101.50","330":"101.49","331":"101.47","332":"101.45","333":"101.44","334":"101.42","335":"101.42","336":"101.41","337":"101.39","338":"101.38","339":"101.36","340":"101.34","341":"101.33","342":"101.31","343":"101.30","344":"101.28","345":"101.27","346":"101.25","347":"101.24","348":"101.22","349":"101.20","350":"101.19","351":"101.17","352":"101.16","353":"101.14","354":"101.13","355":"101.11","356":"101.09","357":"101.08","358":"101.06","359":"101.05","360":"101.03","361":"101.02","362":"101.00","363":"100.99","364":"100.97","365":"100.95"}

    if keyy == "fx_Total_System_Cost":
        price_per_kw = float(0)
        if market_key in pricing_structures.keys():
            if "baseline_price" in pricing_structures[market_key].keys():
                price_per_kw = float(pricing_structures[market_key]["baseline_price"])
            if app_entry.baseline_price > float(0):
                price_per_kw = app_entry.baseline_price

        if booking.fund == "ygrene":
            price_per_kw = float(6000)
                
        
        tier_option = app_entry.tier_option.replace("tier_", "").replace("TIER_", "").lower()
        if not (tier_option == "A"):
            tier_key = "price_tier_" + tier_option
            if tier_key in pricing_structures[market_key].keys():
                price_per_kw += float(pricing_structures[market_key][tier_key])


        system_cost = price_per_kw * float(proposal["system_size"])
        for fund in funds:
            if fund["value"] == booking.fund:
                discount_percentage = float(fund["discount_percentage"].replace("%", "")) / float(100)
                system_cost -= (system_cost * discount_percentage)


        system_cost += float(proposal["additional_amount"])

        if "custom_svcs" in proposal.keys():
            for item in proposal["custom_svcs"]:
                system_cost += float(item["price"])

        #titan
        system_cost += float(2500)
        if booking.fund == "ygrene":
            system_cost -= float(2500)
        #if not booking.fund == "ygrene":
        #    system_cost = system_cost * 1.082

        return system_cost

    elif keyy == "fx_Financier":
        if booking.fund == "ygrene":
            return "Ygrene"
        return "Goodleap"

    elif keyy == "fx_Loan_Term":
        return "25 years"

    elif keyy == "fx_Second_Cash_Payment":
        total = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        already_paid = 2000
        if app_entry.customer_state.lower() == "az":
            already_paid = 3000
        total = total - already_paid

        total = total * 0.5
        total = round(total, 2)
        if not "cash" in booking.fund:
            return 0
        return total

    elif keyy == "fx_Third_Cash_Payment":
        return Helpers.crunch("fx_Second_Cash_Payment", market_key, app_entry, booking, proposal, pricing_structures, funds)

    elif keyy == "fx_Price_Per_Watt":
        total = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        kilowatts = float(proposal["system_size"])
        price_per_watt = total / kilowatts
        price_per_watt = price_per_watt / 1000
        return price_per_watt

    elif keyy == "fx_Dividend_Thirty_Year_Difference":
        utility_cost = Helpers.crunch("fx_30_Year_Utility_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        net_cost = Helpers.crunch("fx_Dividend_Net_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return utility_cost - net_cost

    elif keyy == "fx_Dividend_Pace_Financed_Amount":
        now = Helpers.pacific_now() + timedelta(days=90)
        ninety_days_from_now = Helpers.pacific_now() + timedelta(days=90)
        while True:
            now = now + timedelta(days=-1)
            if now.month == 6 and now.day == 30:
                break

        days_diff = (ninety_days_from_now - now).days
        percentage = d_pace_mapping[str(days_diff)]
        total_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        total_cost *= float(percentage) / float(100)
        return total_cost

    elif keyy == "fx_Dividend_Net_Cost":
        cost_of_pace = Helpers.crunch("fx_Dividend_Pace_Annual_Payment_Times_Twenty", market_key, app_entry, booking, proposal, pricing_structures, funds)
        fed_credit = Helpers.crunch("fx_Federal_Tax_Credit", market_key, app_entry, booking, proposal, pricing_structures, funds)
        tax_benefit = Helpers.crunch("fx_Dividend_Tax_Deduction_Benefit", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return cost_of_pace - fed_credit - tax_benefit

    elif keyy == "fx_Dividend_Pace_Annual_Payment":
        financed_amount = Helpers.crunch("fx_Dividend_Pace_Financed_Amount", market_key, app_entry, booking, proposal, pricing_structures, funds)
        financed_amount *= 0.084944
        return financed_amount

    elif keyy == "fx_Dividend_Pace_Annual_Payment_Times_Twenty":
        annual_payment = Helpers.crunch("fx_Dividend_Pace_Annual_Payment", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return annual_payment * float(20)

    
    elif keyy == "fx_Dividend_Pace_Monthly_Payment":
        annual_amount = Helpers.crunch("fx_Dividend_Pace_Annual_Payment", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return annual_amount / float(12)

    
    elif keyy == "fx_Dividend_Interest_Paid_Over_20_Years":
        financed_amount = Helpers.crunch("fx_Dividend_Pace_Financed_Amount", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return financed_amount * float(0.672198)
    
    elif keyy == "fx_Dividend_Tax_Deduction_Benefit":
        percentage = float(0)
        kv1 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "federal_tax_percentage_" + app_entry.identifier)
        kv2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == "state_tax_percentage_" + app_entry.identifier)
        if not kv1 is None:
            percentage += float(kv1.val.replace("%", ""))
        if not kv2 is None:
            percentage += float(kv2.val.replace("%", ""))

        percentage *= 0.01
        interest_paid_over_twenty_years = Helpers.crunch("fx_Dividend_Interest_Paid_Over_20_Years", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return percentage * interest_paid_over_twenty_years

    elif keyy == "fx_Promo_Length_In_Months":
        months = float(0)
        for fund in funds:
            if fund["value"] == booking.fund:
                months = float(fund["promo_period"])
        return months

    elif keyy == "fx_Promo_Bill":
        sys_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        promo_factor = float(0)
        for fund in funds:
            if fund["value"] == booking.fund:
                promo_factor = float(fund["promo_factor"])
                if fund["tier_enabled"] and (not booking.funding_tier.lower() == "n/a"):
                    for item in fund["tier_data"]:
                        if item["name"] == booking.funding_tier:
                            promo_factor = float(item["promo_factor"])

        return sys_cost * promo_factor

    elif keyy == "fx_Total_System_Cost_After_Rebates":
        sys_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        federal_deduction = Helpers.crunch("fx_Federal_Tax_Credit", market_key, app_entry, booking, proposal, pricing_structures, funds)

        state_tax_credit = float(0)
        if market_key in pricing_structures.keys():
            if "state_tax_credit" in pricing_structures[market_key].keys():
                state_tax_credit = float(pricing_structures[market_key]["state_tax_credit"])
        other_rebates = float(0)
        if market_key in pricing_structures.keys():
            if "other_rebates" in pricing_structures[market_key].keys():
                other_rebates = float(pricing_structures[market_key]["other_rebates"])
        
        float_ss = float(proposal["system_size"])
        if float_ss > float(12.048):
            float_ss = float(12.048)

        return sys_cost - federal_deduction - state_tax_credit - (other_rebates * float_ss)


    elif keyy in ["fx_Solar_Bill_After_Promo", "fx_Bill_With_Credits_And_Rebates_Applied"]:
        after_rebate_amount = Helpers.crunch("fx_Total_System_Cost_After_Rebates", market_key, app_entry, booking, proposal, pricing_structures, funds)
        after_promo_factor = float(0)
        for fund in funds:
            if fund["value"] == booking.fund:
                after_promo_factor = float(fund["after_promo_factor"])
                if fund["tier_enabled"] and (not booking.funding_tier.lower() == "n/a"):
                    for item in fund["tier_data"]:
                        if item["name"] == booking.funding_tier:
                            after_promo_factor = float(item["after_promo_factor"])

        return after_rebate_amount * after_promo_factor

    elif keyy == "fx_Cost_Of_Solar":
        if "cash" in booking.fund.lower():
            total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
            return total_system_cost * 0.9

        promo_months = Helpers.crunch("fx_Promo_Length_In_Months", market_key, app_entry, booking, proposal, pricing_structures, funds)
        promo_bill = Helpers.crunch("fx_Promo_Bill", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return (promo_bill * promo_months) + (float((240 - int(promo_months)) * Helpers.crunch("fx_Solar_Bill_After_Promo", market_key, app_entry, booking, proposal, pricing_structures, funds)))

    elif keyy == "fx_Estimated_Year_One_Production_in_Kwh":
        return float(proposal["year_one_production"].strip())

    elif keyy == "fx_Avg_Cost_Per_Kwh_Over_30_Years":
        sys_production = float(1)
        try:
            sys_production = float(proposal["year_one_production"].lower().replace("kwh", "").strip())
        except:
            sys_production = sys_production
        
        cost_of_solar = Helpers.crunch("fx_Cost_Of_Solar", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return (float(cost_of_solar) / (float(sys_production * float(29)))) * float(100)
        
        # proposals....switch to input offset percentage instead of selecting CA-TOU, UT-70, etc....
        # take year 1 production / last year consumption and show it as a percentage.....
        # ex input 9,900 kwh estimated y1 production...for year one, used 10000 kwh hours (usage). in this case...offset percentage would be 99%.
        # show offset percentage (above) in rep proposals screen
        # calculate offset automatically....
        # will there be a residual utility bill after solar?
        # if yes....
        # prompt for input
        # if no...
        # doesn't.
        # input prompt is same as currently what is...."Partial => Utility Bill After Solar"

        cost = Helpers.crunch("fx_Cost_Of_Solar", market_key, app_entry, booking, proposal, pricing_structures, funds)
        total_kwhs = app_entry.total_kwhs
        usage_months = float(app_entry.usage_months)
        return cost / ((total_kwhs / usage_months) * 360)

    elif keyy == "fx_Average_Bill_W_Utility":
        avg_utility_bill = app_entry.average_utility_bill()

        multiplication_factor = float(1)
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                multiplication_factor = float(pricing_structures[market_key]["utility_rate_hikes"])

        amt = avg_utility_bill * multiplication_factor
        if market_key in pricing_structures.keys():
            if "average_utility_bill_per_month_addon" in pricing_structures[market_key].keys():
                amt += (float(pricing_structures[market_key]["average_utility_bill_per_month_addon"]))

        return amt

    elif keyy == "fx_Utility_Bill_In_30_Years":
        avg_bill = Helpers.crunch("fx_Average_Bill_W_Utility", market_key, app_entry, booking, proposal, pricing_structures, funds)
        multiplication_factor = float(1)
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                multiplication_factor = float(pricing_structures[market_key]["utility_rate_hikes"])
        cnt = 0
        while cnt < 30:
            avg_bill *= multiplication_factor
            cnt += 1

        return avg_bill

    elif keyy == "fx_30_Year_Utility_Cost":
        cost = Helpers.crunch("fx_Average_Bill_W_Utility", market_key, app_entry, booking, proposal, pricing_structures, funds)
        annual_cost = cost * float(12)
        if market_key in pricing_structures.keys():
            if "average_utility_bill_per_month_addon" in pricing_structures[market_key].keys():
                annual_cost += (float(pricing_structures[market_key]["average_utility_bill_per_month_addon"]) * float(11))

        multiplication_factor = float(1)
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                multiplication_factor = float(pricing_structures[market_key]["utility_rate_hikes"])

        payment_total = float(0)
        cnt = 0
        while cnt < 30:
            payment_total += annual_cost
            annual_cost *= multiplication_factor
            cnt += 1

        return payment_total

    elif keyy == "fx_Year_1_Savings":
        if "cash" in booking.fund.lower():
            avg_bill = Helpers.crunch("fx_Average_Bill_W_Utility", market_key, app_entry, booking, proposal, pricing_structures, funds)
            avg_bill *= 12
            residual_bill = float(0)
            if "utility_bill_after_solar" in proposal.keys():
                residual_bill += float(proposal["utility_bill_after_solar"].replace("$", "").strip())

            residual_bill *= float(12)
            return avg_bill - residual_bill
        
        year_cost = float(0)
        avg_bill = Helpers.crunch("fx_Average_Bill_W_Utility", market_key, app_entry, booking, proposal, pricing_structures, funds)
        promo_amount = Helpers.crunch("fx_Promo_Bill", market_key, app_entry, booking, proposal, pricing_structures, funds)
        after_promo_amount = Helpers.crunch("fx_Solar_Bill_After_Promo", market_key, app_entry, booking, proposal, pricing_structures, funds)
        promo_len = int(Helpers.crunch("fx_Promo_Length_In_Months", market_key, app_entry, booking, proposal, pricing_structures, funds))
        promo_len_cpy = int(str(promo_len))
        counter = 0
        while (promo_len > 0) and (counter < 12):
            year_cost += promo_amount
            promo_len -= 1
            counter += 1
        if promo_len_cpy < 12:
            diff = 12 - promo_len_cpy
            cnt = 0
            while cnt < diff:
                year_cost += after_promo_amount
                cnt += 1

        amt = float((avg_bill * float(12)) - year_cost)
        if amt < float(0):
            amt = float(0)

        return amt

    elif keyy == "fx_30_Year_Savings":
        thirty_year_cost = Helpers.crunch("fx_30_Year_Utility_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        cost_of_solar = Helpers.crunch("fx_Cost_Of_Solar", market_key, app_entry, booking, proposal, pricing_structures, funds)
        savings = thirty_year_cost - cost_of_solar
        if savings < float(0):
            savings = float(0)

        return savings

    elif keyy == "fx_Per_Year_Avg_Savings":
        savings = Helpers.crunch("fx_30_Year_Savings", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return savings / float(30)

    elif keyy == "fx_Federal_Tax_Credit":
        cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return cost * 0.26

    elif keyy == "fx_State_Tax_Credit":
        state_tax_credit = float(0)
        if market_key in pricing_structures.keys():
            if "state_tax_credit" in pricing_structures[market_key].keys():
                state_tax_credit = float(pricing_structures[market_key]["state_tax_credit"])
        return state_tax_credit

    elif keyy == "fx_Solar_Bill_W_No_Tax_Credit":
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        multiplication_factor = float(0)
        for fund in funds:
            if fund["value"] == booking.fund:
                multiplication_factor = float(fund["after_promo_factor"])
                if fund["tier_enabled"] and (not booking.funding_tier.lower() == "n/a"):
                    for item in fund["tier_data"]:
                        if item["name"] == booking.funding_tier:
                            multiplication_factor = float(item["after_promo_factor"])

        return total_system_cost * multiplication_factor

    elif keyy in ["fx_Cash_Down_CA", "fx_Cash_Down_UT", "fx_Cash_Down_TX", "fx_Cash_Down_CO", "fx_Cash_Down"]:
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        down = float(0)
        for fund in funds:
            if fund["value"] == booking.fund:
                percentage = float(fund["downpayment_amount"].replace("%", ""))
                percentage /= float(100)
                down = percentage * total_system_cost
        if (app_entry.customer_state.upper() == "CA") and ("cash" in booking.fund.lower()):
            down = float(1000)

        return down

    elif keyy == "fx_Milestone_One":
        if "cash" in booking.fund.lower():
            return float(0)
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return total_system_cost * float(0.2)

    elif keyy == "fx_Milestone_Two":
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        if "cash" in booking.fund.lower():
            down_payment = Helpers.crunch("fx_Cash_Down", market_key, app_entry, booking, proposal, pricing_structures, funds)            
            return total_system_cost - down_payment

        return total_system_cost * 0.8

    elif keyy == "fx_Twenty_Percent_Of_System_Cost":
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return total_system_cost * float(0.2)
    
    elif keyy == "fx_Thirty_Percent_Of_System_Cost":
        if "cash" in booking.fund.lower():
            return float(0)
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return total_system_cost * float(0.3)

    elif keyy == "fx_Seventy_Percent_Of_System_Cost":
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        if "cash" in booking.fund.lower():
            down_payment = Helpers.crunch("fx_Cash_Down", market_key, app_entry, booking, proposal, pricing_structures, funds)            
            return total_system_cost - down_payment

        return total_system_cost * 0.7
    
    elif keyy == "fx_Eighty_Percent_Of_System_Cost":
        total_system_cost = Helpers.crunch("fx_Total_System_Cost", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return total_system_cost * float(0.8)

    elif keyy == "fx_Annual_Escalator_Percentage":
        return "0%"

    elif keyy == "fx_Electricity_Rate_Change_Percentage":
        percentage = float(0)
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                percentage = str(pricing_structures[market_key]["utility_rate_hikes"])
                percentage = float(percentage)
                percentage -= float(1.0)
                percentage *= 100
        return str(round(percentage, 2)) + "%"

    elif keyy == "fx_Annual_Grid_Cost_In_5_Years":
        escalator = 1.0
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                escalator = float(pricing_structures[market_key]["utility_rate_hikes"])

        total_dollars = app_entry.total_dollars
        cnt = 0
        nums = []
        while cnt < 5:
            nums.append(total_dollars)
            total_dollars *= escalator
            cnt += 1

        return nums[len(nums) - 1]

    elif keyy == "fx_Annual_Grid_Cost_In_10_Years":
        escalator = 1.0
        if market_key in pricing_structures.keys():
            if "utility_rate_hikes" in pricing_structures[market_key].keys():
                escalator = float(pricing_structures[market_key]["utility_rate_hikes"])

        total_dollars = app_entry.total_dollars
        cnt = 0
        nums = []
        while cnt < 10:
            nums.append(total_dollars)
            total_dollars *= escalator
            cnt += 1

        return nums[len(nums) - 1]

    elif keyy == "fx_Highest_Monthly_Bill":
        return app_entry.highest_amount

    elif keyy == "fx_Promotional_Bill_Label":
        months = Helpers.crunch("fx_Promo_Length_In_Months", market_key, app_entry, booking, proposal, pricing_structures, funds)
        return "First " + str(months) + " months promotional bill"

    elif keyy == "fx_Contractor_Name":
        if market_key in pricing_structures.keys():
            if "contractor_name" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_name"]

        return ""

    elif keyy == "fx_Contractor_Street_Address":
        if market_key in pricing_structures.keys():
            if "contractor_street_address" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_street_address"]
        return ""

    elif keyy == "fx_Contractor_City":
        if market_key in pricing_structures.keys():
            if "contractor_city" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_city"]
        return ""

    elif keyy == "fx_Contractor_State":
        if market_key in pricing_structures.keys():
            if "contractor_state" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_state"]
        return ""

    elif keyy == "fx_Contractor_Zip":
        if market_key in pricing_structures.keys():
            if "contractor_zip" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_zip"]
        return ""

    elif keyy == "fx_Contractor_City_State":
        city = ""
        state = ""
        if market_key in pricing_structures.keys():
            if "contractor_city" in pricing_structures[market_key].keys():
                city = pricing_structures[market_key]["contractor_city"]
            if "contractor_state" in pricing_structures[market_key].keys():
                state = pricing_structures[market_key]["contractor_state"]

        return city + ", " + state

    elif keyy == "fx_Contractor_City_State_Zip":
        city = ""
        state = ""
        zip = ""
        if market_key in pricing_structures.keys():
            if "contractor_city" in pricing_structures[market_key].keys():
                city = pricing_structures[market_key]["contractor_city"]
            if "contractor_state" in pricing_structures[market_key].keys():
                state = pricing_structures[market_key]["contractor_state"]
            if "contractor_zip" in pricing_structures[market_key].keys():
                zip = pricing_structures[market_key]["contractor_zip"]            

        return city + ", " + state + " " + zip

    elif keyy == "fx_Contractor_Address_City_State_Zip":
        city = ""
        state = ""
        zip = ""
        address = ""

        if market_key in pricing_structures.keys():
            if "contractor_city" in pricing_structures[market_key].keys():
                city = pricing_structures[market_key]["contractor_city"]
            if "contractor_state" in pricing_structures[market_key].keys():
                state = pricing_structures[market_key]["contractor_state"]
            if "contractor_zip" in pricing_structures[market_key].keys():
                zip = pricing_structures[market_key]["contractor_zip"]
            if "contractor_street_address" in pricing_structures[market_key].keys():
                address = pricing_structures[market_key]["contractor_street_address"]

        return address + " " + city + ", " + state + " " + zip

    elif keyy == "fx_Contractor_Phone_Number":
        if market_key in pricing_structures.keys():
            if "contractor_phone_number" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_phone_number"]
        return ""

    elif keyy == "fx_Contractor_License_Number":
        if market_key in pricing_structures.keys():
            if "contractor_license_number" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_license_number"]
        return ""

    elif keyy == "fx_Contractor_Email":
        if market_key in pricing_structures.keys():
            if "contractor_email" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_email"]
        return ""

    elif keyy == "fx_Contractor_Insurance_Company":
        if market_key in pricing_structures.keys():
            if "contractor_insurance_company" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_insurance_company"]
        return ""

    elif keyy == "fx_Contractor_Insurance_Company_Phone_Number":
        if market_key in pricing_structures.keys():
            if "contractor_insurance_company_phone_number" in pricing_structures[market_key].keys():
                return pricing_structures[market_key]["contractor_insurance_company_phone_number"]
        return ""

    elif keyy == "fx_Commission_Deduction":
        price_per_kw = float(0)
        if market_key in pricing_structures.keys():
            if "baseline_price" in pricing_structures[market_key].keys():
                price_per_kw = float(pricing_structures[market_key]["baseline_price"])
            if app_entry.baseline_price > float(0):
                price_per_kw = app_entry.baseline_price
        
        actual_price_per_kw = price_per_kw
        tier_option = app_entry.tier_option.replace("tier_", "").replace("TIER_", "").lower()
        if not (tier_option == "A"):
            tier_key = "price_tier_" + tier_option
            if tier_key in pricing_structures[market_key].keys():
                actual_price_per_kw += float(pricing_structures[market_key][tier_key])

        return price_per_kw - actual_price_per_kw

    elif keyy == "fx_Commission_Price_Per_Kw_Leaase_PPA":
        price_per_kw = float(0)
        if market_key in pricing_structures.keys():
            if "ppa_commission" in pricing_structures[market_key].keys():
                price_per_kw = float(pricing_structures[market_key]["ppa_commission"])

        return price_per_kw

    elif keyy == "fx_Additional_Incentives":
        state_tax_credit = float(0)
        if market_key in pricing_structures.keys():
            if "state_tax_credit" in pricing_structures[market_key].keys():
                state_tax_credit = float(pricing_structures[market_key]["state_tax_credit"])

        other_rebates = float(0)
        if market_key in pricing_structures.keys():
            if "other_rebates" in pricing_structures[market_key].keys():
                other_rebates = float(pricing_structures[market_key]["other_rebates"])
        
        float_ss = float(proposal["system_size"])
        if float_ss > float(12.048):
            float_ss = float(12.048)

        return state_tax_credit + (other_rebates * float_ss)

    elif keyy == "fx_Commission_Price_Per_Kw":
        price = float(0)
        if market_key in pricing_structures.keys():
            if "baseline_commission" in pricing_structures[market_key].keys():
                price = float(pricing_structures[market_key]["baseline_commission"])

                tier_option = app_entry.tier_option.replace("tier_", "").replace("TIER_", "").upper()
                if not (tier_option == "A"):
                    tier_key = "commission_tier_" + tier_option.lower()
                    price += float(pricing_structures[market_key][tier_key])

        return price

    elif keyy == "fx_Market_Name":
        name = ""
        market = OfficeLocation.first(OfficeLocation.identifier == market_key)
        if not market is None:
            name = market.name
        return name

    elif keyy == "fx_State_Tax_Credit_Label":
        name = "State Tax Credit"
        if market_key in pricing_structures.keys():
            if "label_for_state_tax_credit" in pricing_structures[market_key].keys():
                name = pricing_structures[market_key]["label_for_state_tax_credit"]
        return name

    elif keyy == "fx_Utility_Provider":
        ret = "Your Utility Provider"
        utility_providers = Helpers.list_utility_providers()
        for provider in utility_providers:
            if provider["value"] == app_entry.utility_provider:
                ret = provider["value_friendly"]
        return ret

    elif keyy == "fx_Points_Used":
        ret = str(0)
        if "all_points" in proposal.keys():
            ret = str(proposal["all_points"])
        return ret

    else:
        return float(0)
