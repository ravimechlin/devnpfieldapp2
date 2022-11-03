@staticmethod
def delete_search_document(index, doc_id):
    idx = search.Index(name=index)
    idx.delete([doc_id])

