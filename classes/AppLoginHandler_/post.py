def post(self):
    import json
    import base64
    
    post_body = str(self.request.body)
    logging.info("The post body...")
    parsed_info = json.loads(post_body)
    logging.info(parsed_info)

    user = FieldApplicationUser.first(
        ndb.AND
        (
            FieldApplicationUser.rep_email == parsed_info["username"],
            FieldApplicationUser.password == Helpers.hash_pass(parsed_info["password"]),
            FieldApplicationUser.current_status == 0
        )
    )
    if not user is None:
        user_fields = {
        "user_id" : user.identifier,
        "user_type" : user.user_type,
        "user_first" : user.first_name.strip().title(),
        "user_last" : user.last_name.strip().title(),
        "user_phone" : user.rep_phone,
        "user_rep_email" : user.rep_email,
        "user_rep_id" : user.rep_id,
        "user_office" : user.main_office,
        "user_manager": user.is_manager
        }
    
        self.response.out.write(json.dumps(user_fields))
        self.response.set_status(200) 
    else:
        self.response.out.write("0")
        self.response.set_status(200)
    #LOGIN AUTH END

