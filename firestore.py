import sys
import os
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import firebase_admin
from firebase_admin import credentials,firestore
import sys
import os
def create_doc_reference(db,args):
    doc_ref = db.collection(args[0]).document(args[1])
    if len(args)>2:
        for arg in range(2, len(args),2):
            doc_ref = doc_ref.collection(args[arg]).document(args[arg + 1])
    return doc_ref
def create_document(db,*args,**kwargs):
    doc_ref=create_doc_reference(db,args)
    doc_ref.set({**kwargs})
def get_document(db,*args):
    doc_ref = create_doc_reference(db, args)
    doc=doc_ref.get()
    if doc.exists:
        # print(f"Document data: {doc.to_dict()}")
        return doc.to_dict()
    else:
        # print("No such document!")
        return None
def get_all_documents_field_in_collection(db,*args,field=None):
    # doc_ref = create_doc_reference(db, args)
    doc_ref = db.collection(args[0])
    if len(args)>1:
        for i in range(1,len(args)):
            if i%2==0:
                doc_ref = doc_ref.collection(args[i])
            else:
                doc_ref = doc_ref.document(args[i])
    field_values=[]
    docs=[]
    if field is None:
        for doc in doc_ref.list_documents():
            dic=doc.get().to_dict()
            docs.append(doc)
    else:
        if len(args)==1:
            for doc in doc_ref.list_documents():
                for collection in doc.collections():
                    if collection.id=='salespeople':
                        for d in collection.list_documents():
                            dic=d.get().to_dict()
                            value=dic[field]
                            field_values.append(value)
                            docs.append(d)
        else:
            for doc in doc_ref.list_documents():
                dic=doc.get().to_dict()
                # print(dic)
                try:
                    value=dic[field]
                    field_values.append(value)
                    docs.append(doc)
                except:
                    continue
    return field_values,docs

def update_document(db,*args,**kwargs):
    doc_ref = create_doc_reference(db, args)
    doc_ref.update({**kwargs})
def delete_field(db,*args,field):
    doc_ref=create_doc_reference(db,args)
    doc_ref.update({
        field: firestore.DELETE_FIELD
    })
def delete_assist(doc_ref):
    for doc in doc_ref.list_documents():
        # print(f'Document ID: {doc.id}', type(doc))
        subcollections = list(doc.collections())
        if not subcollections:
            # print(f'Deleting document: {doc.id}')
            doc.delete()
        else:
            for sub in subcollections:
                delete_collection(sub)
def get_document_subcollections(db,*args):
    doc_ref = create_doc_reference(db, args)
    subcollections = list(doc_ref.collections())
    ids=[s.id for s in subcollections]
    return ids
def delete_collection(doc_ref, batch_size=10):
    # print(type(doc_ref))
    if isinstance(doc_ref, firestore.DocumentReference):
        subcollections = list(doc_ref.collections())
        if not subcollections:
            # print(f'Deleting document: {doc_ref.id}')
            return doc_ref.delete()
        else:
            for s in subcollections:
                delete_assist(s)
    else:
        delete_assist(doc_ref)
def delete_document(db,*args):
    doc_ref = db.collection(args[0])
    for i in range(1, len(args)):
        if i % 2 != 0:
            doc_ref = doc_ref.document(args[i])
        else:
            doc_ref = doc_ref.collection(args[i])
    delete_collection(doc_ref)

