@staticmethod
def get_county_from_city_and_state_and_zip(city, state, postal):
    city = city.lower()
    state = state.lower()
    keyy = "county_for_" + city + "_" + state

    val = memcache.get(keyy)

    if val is None:
        try:

            resp = urlfetch.fetch(
                url="https://maps.googleapis.com/maps/api/geocode/json?address=" + city + ",%20" + state,
                deadline=10
            )

            if resp.status_code == 200:
                result = json.loads(resp.content)


                for component in result["results"][0]["address_components"]:

                    if component["types"][0] == "administrative_area_level_2":

                        county = component["long_name"].replace("County", "").replace("county", "").strip()
                        memcache.set(key=keyy, value=county, time=(60 * 60 * 24 * 14))
                        return county

        except:
            try:

                resp = urlfetch.fetch(
                    url="http://www.uscounties.org/cffiles_web/counties/zip_res.cfm?zip=" + postal + "&websource=naco",
                    deadline=10
                )

                county_page_dom = BeautifulSoup(resp.content)

                tds = county_page_dom.find_all("td")
                count = 0
                for td in tds:
                    count += 1
                    if count == 3:
                        logging.info(str(td.string))

            except:
                state = state

        return ""

    else:
        return val

