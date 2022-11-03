@staticmethod
def progress(step_qi=None, substep_qi=None, updated_dt=None, app_entry_reference=None, booking_reference=None):
    app_entry_type_str = str(type(app_entry_reference))

    if booking_reference is None and (not app_entry_type_str == "<type 'unicode'>") and (not app_entry_type_str == "<type 'str'>"):
        booking_reference = SurveyBooking.first(SurveyBooking.identifier == app_entry_reference.booking_identifier)

    if (step_qi is None) or (substep_qi is None):
        raise ValueError("A step key and substep key are required")

    if updated_dt is None:
        raise ValueError("A ")

    if app_entry_reference is None:
        raise ValueError("A field application entry object or it's identifier are required")

    if booking_reference is None:
        raise ValueError("A survey booking object or it's identifier are required")

    booking_type_str = str(type(booking_reference))

    e_id = None
    f_id = None
    b_id = None

    try:
        if app_entry_type_str == "<type 'unicode'>" or app_entry_type_str == "<type 'str'>":
            e_id = app_entry_reference
            f_id = app_entry_reference
        else:
            e_id = app_entry_reference.booking_identifier
            f_id = app_entry_reference.booking_identifier

        if booking_type_str == "<type 'unicode'>" or booking_type_str == "<type 'str'>":
            b_id = booking_reference
        else:
            b_id = booking_reference.identifier
    except:
        logging.error("Trouble getting the customer progress identifiers in CustomerProgressManager.progress")


    try:
        cpi = CustomerProgressV2Item.first(
            ndb.AND
            (
                CustomerProgressV2Item.entity_identifier == e_id,
                CustomerProgressV2Item.field_app_identifier == f_id,
                CustomerProgressV2Item.booking_identifier == b_id
            )
        )
        if cpi is None:
            cpi = CustomerProgressV2Item(
                identifier=Helpers.guid(),
                entity_identifier=e_id,
                field_app_identifier=f_id,
                booking_identifier=b_id,
                step_key=step_qi,
                substep_key=substep_qi,
                updated=updated_dt,
                extra_info="{}",
                archived=False,
                save_me=False
            )

        else:
            cpi.step_key=step_qi,
            cpi.substep_key=substep_qi,
            cpi.updated=updated_dt

        cpa = CustomerProgressV2Archive(
            identifier=cpi.identifier,
            entity_identifier=cpi.entity_identifier,
            field_app_identifier=cpi.field_app_identifier,
            booking_identifier=cpi.booking_identifier,
            step_key=cpi.step_key,
            substep_key=cpi.substep_key,
            updated=cpi.updated,
            extra_info=cpi.extra_info
        )

    except:
        logging.error("There was an error in creating the CustomerProgressV2Item and CustomerProgressV2Archive entities")

    try:
        cpi.put()
        cpa.put()
    except:
        logging.error("There was an error in saving the CustomerProgressV2Item and CustomerProgressV2Archive entities. This is SERIOUS!")

