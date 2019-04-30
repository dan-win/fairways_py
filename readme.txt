Test command to create tracker:


curl -X GET 'http://127.0.0.1:10000/send/evt/gaecom?tvzPlf=tvz&gaClientId=client-id&tvzCustomerId=customer-id&transactionId=0111180a-4bdb-11e9-bcdf-002590ea2218'
production endpoint:
curl -X GET 'https://trec.tvzavr.ru/radar/send/evt/gaecom?tvzPlf=tvz&gaClientId=client-id&tvzCustomerId=customer-id&transactionId=0111180a-4bdb-11e9-bcdf-002590ea2218'


TO-DO:
* trace json scheme!