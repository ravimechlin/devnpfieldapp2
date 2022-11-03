@staticmethod
def create_to_do_payroll_address_update(rep):
    from google.appengine.api import app_identity
    val = memcache.get("address_update_" + rep.identifier)
    if val is None:
        memcache.set(key="address_update_" + rep.identifier, value="1", time=60 * 10)
        owners = ["38655a8a3e258861c88e0bb74ba206af08970f499c355ee9739c95c2b39ff5f7f9ecb7adfef8756f33868e7385a2a951190ad97b332a247e2817fc70253f235c"]
        assignerr = "38655a8a3e258861c88e0bb74ba206af08970f499c355ee9739c95c2b39ff5f7f9ecb7adfef8756f33868e7385a2a951190ad97b332a247e2817fc70253f235c"
        if app_identity.get_application_id() == "npfieldapp":
            owners = ["18d1b56e40b4e54421cf0815f62a18ba47f3c3f63f350014f1ee8ef5ec3ed9b91bed5b0b27976f992b69e37bbd580ae701db787778519b823dcc61f0c18213df", "1bcc5aa68b2ca8548f81e6020276c2bded9770805f943a13a4d1cb55be840f9846a78117a6f9cd2ffff6334c5a36b7d32551d81e085a02a65895fbe381ea3d27", "fc0a96d841debfa61191d0cacf4f1f80414719a918ea33f3e8bcb70c94301a04509b280a6c952ff323d3e13c8bc062c128a23e50da52c787c1efd9abd41ffd85"]
            assignerr = "3e9226f571e6bde4aab097e9df3aedb1046a358a31165cb0b21bf082f2153c8cd1b64d1ebdf6754fba5e0ac956aa367e1b5592402064371cebf86965a2f18808"
        new_identifiers = []
        for owner in owners:
            new_identifiers.append(Helpers.guid())

        linked_identifiers = new_identifiers
        cnt = 0
        for o in owners:
            item = ToDoItem(
                identifier=new_identifiers[cnt],
                owner=o,
                assigner=assignerr,
                field_app_identifier="-1",
                name="Update " + rep.first_name.strip().title() + " " + rep.last_name.strip().title() + "'s address for payroll.",
                completed=False,
                notes="See address in employee directory (but be sure to refresh).",
                completed_dt=datetime(1970, 1, 1),
                reminder_sent=False,
                daily_reminder=True,
                weekly_reminder=False,
                monthly_reminder=False,
                linked_identifiers=json.dumps(linked_identifiers)
            )

            item.reminder_dt = Helpers.pacific_now() + timedelta(hours=2)
            item.due_dt = Helpers.pacific_now() + timedelta(days=1)

            item.put()

            if not item.owner == item.assigner:
                owner = FieldApplicationUser.first(FieldApplicationUser.identifier == item.owner)
                assigner = FieldApplicationUser.first(FieldApplicationUser.identifier == item.assigner)
                if (not owner is None) and (not assigner is None):
                    subj = "New To-Do Item from " + assigner.first_name.strip().title() + " " + assigner.last_name.strip().title()
                    msg = item.name + "\r\n\r\n" + item.notes + "\r\n\r\n" + "Due: " + item.due_dt.strftime("%m/%d/%Y %I:%M %p")
                    Helpers.send_email(owner.rep_email, subj, msg)

            cnt += 1

