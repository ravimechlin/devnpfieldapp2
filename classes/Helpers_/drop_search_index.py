@staticmethod
def drop_search_index(index_name):
    try:
        doc_index = search.Index(name=index_name)

        while True:
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            doc_index.delete(document_ids)
    except:
        return 1

