


def get_user_expenses(username):
    expenses_ref = db.collection("expenses")
    expenses_docs = expenses_ref.where("Username", "==", username).stream()
    expenses = {doc.id: doc.to_dict() for doc in expenses_docs}
    return expenses
