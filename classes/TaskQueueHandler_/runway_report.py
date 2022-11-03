def runway_report(self):
    user_ids_to_query = ["-1"]
    user_identifier_name_dict = {}
    users = FieldApplicationUser.query(
        ndb.AND(
            FieldApplicationUser.registration_date >= date(2019, 3, 1),
            FieldApplicationUser.registration_date <= date(2019, 12, 31)
        )
    )
    for user in users:
        if user.user_type in ["solar_pro", "solar_pro_manager"]:
            user_ids_to_query.append(user.identifier)
            user_identifier_name_dict[user.identifier] = user.first_name.strip().title() + " " + user.last_name.strip().title()

    data = []
    for user_id in user_ids_to_query:
        if not user_id == "-1":            
            obj = {}
            obj["name"] = user_identifier_name_dict[user_id]
            obj["runway_level_two_doc_link"] = "n/a"
            obj["runway_level_three_doc_link"] = "n/a"

            if Helpers.gcs_file_exists("/Images/RunwayDocs/LevelTwo/" + user_id + ".jpg"):
                obj["runway_level_two_doc_link"] = "https://storage.googleapis.com/npfieldapp.appspot.com/Images/RunwayDocs/LevelTwo/" + user_id + ".jpg"
            
            if Helpers.gcs_file_exists("/Images/RunwayDocs/LevelThree/" + user_id + ".jpg"):
                obj["runway_level_three_doc_link"] = "https://storage.googleapis.com/npfieldapp.appspot.com/Images/RunwayDocs/LevelThree/" + user_id + ".jpg"
                        
            cnt = 1
            while cnt < 11:
                obj["runway_level_two_selfie_image_" + str(cnt)] = "n/a"
                idx = cnt - 1
                if Helpers.gcs_file_exists("/Images/RunwaySelfies/level_two/" + user_id + "/" + str(idx) + ".jpg"):
                    obj["runway_level_two_selfie_image_" + str(cnt)] = "https://storage.googleapis.com/npfieldapp.appspot.com/Images/RunwaySelfies/level_two/" + user_id + "/" + str(idx) + ".jpg"
                cnt += 1

            data.append(obj)

    f = GCSLockedFile("/Temp/RunwayReport.json")
    f.write(json.dumps(data), "text/plain", "public-read")
    f.unlock()

