@staticmethod
def increment_tally_for_user(user_rep_id, metric):
    try:
        tally = 0

        #  get the current tally
        ####
        ###
        #  try memcache

        h_p_t = Helpers.pacific_today()
        tally_key = user_rep_id + "_tally_" + metric + "_" + str(h_p_t)
        val1 = memcache.get(tally_key)
        if val1 is None:
            # if it's not in memcache, try KV Store

            kv_item = KeyValueStoreItem.first(KeyValueStoreItem.keyy == tally_key)
            if kv_item is None:
                # if it's not in the KV store, try the flat file
                f = GCSLockedFile("/LB_Metrics/daily_tallies/" + tally_key + ".tally")
                content = f.read()
                if not content is None:
                    tally = int(content)
                f.unlock()
            else:
                tally = int(kv_item.val)

        else:
            tally = int(val1)


        tally += 1

        # ### write the current tally

        memcache.set(key=tally_key, value=str(tally), time=60 * 60 * 25)
        kv_item2 = KeyValueStoreItem.first(KeyValueStoreItem.keyy == tally_key)
        if kv_item2 is None:
            kv_item3 = KeyValueStoreItem(
                identifier=Helpers.guid(),
                keyy=tally_key,
                val=str(tally),
                expiration=Helpers.pacific_now() + timedelta(hours=25)
            )
            kv_item3.put()
        else:
            kv_item2.val = str(tally)
            kv_item2.put()

        f2 = GCSLockedFile("/LB_Metrics/daily_tallies/" + tally_key + ".tally")
        f2.write(str(tally), "text/plain", "public-read")
        f2.unlock()

    except:
        logging.error("Couldn't write to the tally...")
        logging.info(user_rep_id)
        logging.info(metric)
