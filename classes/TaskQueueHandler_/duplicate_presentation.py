def duplicate_presentation(self):
    import time
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    from google.appengine.api import app_identity
    import StringIO
    import base64
    import cloudstorage as gcs
    import tablib
    from google.appengine.api import taskqueue
    
    slide_identifier = self.request.get("identifier")
    slide = Slide.first(Slide.identifier == slide_identifier)
    if not slide is None:
        slide_cpy = Slide(
            identifier=Helpers.guid(),
            name="Duplicated " + slide.name,
            options=slide.options,
            slide_count=slide.slide_count,
            applicable_offices=slide.applicable_offices
        )

        # copy the image assets
        image_assets = json.loads(slide.image_assets)
        asset_cpy = []
        image_old_identifier_new_identifier_dict = {}
        for item in image_assets:
            dupe = json.loads(json.dumps(item))
            dupe["new_identifier"] = Helpers.guid()
            asset_cpy.append(dupe)
        
        for item in asset_cpy:
            path = "/SlideImages/" + slide.identifier + "/" + item["identifier"] + "." + item["extension"]
            new_path = "/SlideImages/" + slide_cpy.identifier + "/" + item["new_identifier"] + "." + item["extension"]
            mime = "image/jpeg"
            if item["extension"].lower() == "png":
                mime = "image/png"

            done = False
            while not done:
                try:
                    Helpers.gcs_copy(path, new_path, mime, "public-read")
                    done = True
                except:
                    done = done

        for item in asset_cpy:
            image_old_identifier_new_identifier_dict[item["identifier"]] = item["new_identifier"]
            item["identifier"] = item["new_identifier"]
            del item["new_identifier"]

        slide_cpy.image_assets = json.dumps(asset_cpy)

        #copy the slide items
        slide_identifiers = json.loads(slide.slide_identifiers)
        item_identifier_duplication_dict = {}
        new_identifier_lst = []
        for item in slide_identifiers:
            n_id = Helpers.guid()
            item_identifier_duplication_dict[item] = n_id
            new_identifier_lst.append(n_id)

        slide_items = SlideItem.query(SlideItem.identifier.IN(slide_identifiers))
        for item in slide_items:
            slide_item_cpy = SlideItem(
                identifier=item_identifier_duplication_dict[item.identifier],
                idx=item.idx,
                options=item.options                    
            )

            view_data = json.loads(item.views)
            view_data_cpy = []
            component_identifier_new_identifiers_dict = {}
            for view in view_data:
                view_cpy = []
                for component in view:
                    if not component["identifier"] in component_identifier_new_identifiers_dict:
                        component_identifier_new_identifiers_dict[component["identifier"]] = Helpers.guid()
                    new_id = component_identifier_new_identifiers_dict[component["identifier"]]
                    component["identifier"] = new_id
                    component_keys = component.keys()
                    if ("image_identifier" in component_keys) and ("image_extension" in component_keys):
                        component["image_identifier"] = image_old_identifier_new_identifier_dict[component["image_identifier"]]
                    view_cpy.append(component)

                view_data_cpy.append(view_cpy)

            slide_item_cpy.views = json.dumps(view_data_cpy)
            slide_item_cpy.put()

        slide_cpy.slide_identifiers = json.dumps(new_identifier_lst)
        slide_cpy.put()
