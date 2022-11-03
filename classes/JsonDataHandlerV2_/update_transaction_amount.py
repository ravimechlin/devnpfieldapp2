def update_transaction_amount(self):
    dollars = int(self.request.get("amount").split(".")[0])
    cents = int(self.request.get("amount").split(".")[1])
    if "-" in self.request.get("amount"):
        cents *= -1
        
    transaction = MonetaryTransactionV2.first(MonetaryTransactionV2.identifier == self.request.get("identifier"))
    if not transaction is None:
        transaction.dollars = dollars
        transaction.cents = cents
        transaction.put()
    

