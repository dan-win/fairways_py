import os, sys

import logging
logging.basicConfig(
    # filename='example.log', 
    format='%(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG)
log = logging.getLogger(__name__)

import re
import json
import itertools

import requests
import urllib

from hostapi.io import Heap, JsonStore, NullStore, Redis, Alchemy, MySql, ConnectionPool, json_stream

from hostapi.chains import Chain 

from hostapi.underscore import Underscore as _

buffer_path = os.getenv('EVENTMACHINE_BUFFER', './../buffer')
# engine = BinStore(buffer_path)
engine = NullStore()
heap = Heap(engine)
jsonfile = JsonStore(buffer_path)

# Constants

# """
# TYPE
# """
# 3	Списание средств со счета
WITHDRAWAL = 3
# 7	Прямая оплата товара без создания счета
OVERDRAFT = 7 
# 8	Зачисление средств на счет
DEPOSIT = 8 

# """
# STATUS
# """
# 30	Списание с личного счета завершено
WITHDRAWAL_ACK = 30
# 15	Прямая оплата продукта через внешнюю платежную систему без окрытия счета; платеж подтвержден
OVERDRAFT_ACK = 15
# 20	Пополнение личного счета, платеж проведен
DEPOSIT_ACK = 20
# All acknowledgements
ACK = (WITHDRAWAL_ACK, OVERDRAFT_ACK, DEPOSIT_ACK)

"""
    route: String,
    sender:   String,
    headers_info: HashMap<String,Vec<String>>,
    cookies:   HashMap<String,String>,
    envelope:   HashMap<String,String>,

"""

# class TrackerMap:
#     def __init__(self, **raw_data):
#         envelope =  raw_data['envelope']
#         sender =    raw_data['sender']
#         headers =   raw_data['headers_info']
#         cookies =   raw_data['cookies']
#         route =     raw_data['route']

#         self.tvzPlf =       envelope.get('tvzPlf')
#         self.gaClientId =   envelope.get('gaClientId')
#         self.tvzCustomerId = envelope.get('tvzCustomerId')
#         self.transactionId = envelope.get('transactionId')
#         self.gaTrackerId =  "UA-125243419-1"

@heap.store
def fetch_trackers(ctx):
    """
    Extract data from remote buffer
    """

    redis_db =  ConnectionPool.select(Redis, "REDIS_ADDRESS") 

    trackers = []
    # Data exist in multiple chunks, so join them together by enumeration:
    while True:
        chunk = redis_db.engine.rpop("evt/gaecom")
        if chunk is None:
            break
        rec = chunk.decode()
        memdata = json.loads(rec)
        for event in memdata:
            trackers.append(event)

    return trackers

def fake_trackers(ctx):
    """
    Fake test mock
    """
    _fake_transactions= [
        # # complex transaction:
        # "04b72e54-4c9e-11e9-b1f3-002590ea2218",

        # # with product:
        # "0012d6fe-4038-11e9-b38a-0cc47a172970",

        # # with promo:
        # "000d672e-35f1-11e9-906d-002590ea2218",

        # # 100% promo:
        # "00aad1c4-41bf-11e9-a0af-002590ea2218",

        # Collection of complex transactions (3 per operation)
        "03a1ab52-4ca3-11e9-bd79-0cc47a172970", 
        "098e369c-4bdc-11e9-a5fa-002590ea2218", 
        "0aa50ef0-513d-11e9-8c00-0cc47a172970", 
        "0b91d2c8-522b-11e9-9ec7-002590ea2218", 
        "0bbf3144-5138-11e9-b958-0cc47a172970", 
        "0da89f38-4be6-11e9-b497-002590ea2218", 
        "1419d74c-5217-11e9-9382-0cc47a172970", 
        "1467df54-4bdd-11e9-9f98-0cc47a172970", 
        "171e3c46-4bd5-11e9-8cbd-002590ea2218", 
        "1ad3e198-5219-11e9-a6d8-0cc47a172970", 
        "1ae47028-4bdc-11e9-9176-002590ea2218", 
        "1b545634-4bd9-11e9-99dd-002590ea2218", 
        "1f3cff3c-5136-11e9-b29f-0cc47a172970", 
        "23b6b74c-4c9f-11e9-8aca-0cc47a172970", 
        "240a5fb6-4be4-11e9-80cb-0cc47a172970", 
        "2cb2b792-4bb9-11e9-a580-002590569245", 
        "2e2af452-5219-11e9-8be5-0cc47a172970", 
        "36d84982-521a-11e9-86e6-0cc47a172970", 
        "42d7b6fe-514e-11e9-be43-0cc47a172970", 
        "5e124aa2-4aea-11e9-969e-002590569245", 
        "625878c4-4bd1-11e9-9db7-002590ea2218", 
        "66e16f38-5219-11e9-bbb7-0cc47a172970", 
        "6c8e669a-513b-11e9-ad1d-0cc47a172970", 
        "70c4419c-5133-11e9-ab84-0cc47a172970", 
        "74864e8e-4bd8-11e9-abea-002590ea2218", 
        "7f705dc6-5141-11e9-98be-0cc47a172970", 
        "833265d8-4be9-11e9-9200-0cc47a172970", 
        "879d88c2-5216-11e9-a6e8-0cc47a172970", 
        "8f869fbe-4beb-11e9-a5c6-0cc47a172970", 
        "93db60ce-5134-11e9-88d6-0cc47a172970", 
        "9c45a060-4bd7-11e9-a134-002590ea2218", 
        "9cd43d0a-4bd4-11e9-ac88-0cc47a172970", 
        "9de82b24-4bdf-11e9-a46e-002590ea2218", 
        "a1f4eac4-5141-11e9-941b-002590ea2218", 
        "b1edf34a-4bd2-11e9-80fb-0cc47a172970", 
        "b6c006a6-4ca4-11e9-8813-002590ea2218", 
        "b72602d2-5134-11e9-bb3c-0cc47a172970", 
        "b86df0b2-4ca4-11e9-a5dc-002590ea2218", 
        "b9a95070-4ca4-11e9-917c-002590ea2218", 
        "b9ae9648-4ca4-11e9-b055-002590ea2218", 
        "b9b16c2e-4ca4-11e9-b048-002590ea2218", 
        "bb18e38c-4aea-11e9-a9eb-002590569245", 
        "bf760664-4ca5-11e9-ad63-002590ea2218", 
        "bf7e8a3c-4ca5-11e9-b388-002590ea2218", 
        "bf825dc4-4ca5-11e9-a75e-002590ea2218", 
        "c90ba9d8-5216-11e9-9a0b-0cc47a172970", 
        "ca61bb24-4c9e-11e9-9eb6-0cc47a172970", 
        "cc173958-5216-11e9-ba2f-0cc47a172970", 
        "d6ef0cd2-5141-11e9-814c-0cc47a172970", 
        "d75d1c88-522a-11e9-bc6b-002590ea2218", 
        "ddf40074-4ca4-11e9-b044-002590ea2218", 
        "e5526ce0-5148-11e9-873f-0cc47a172970", 
        "e79d914c-5219-11e9-aa76-0cc47a172970", 
        "e889e8c8-4bdc-11e9-8cc7-0cc47a172970", 
        "f1c6ac1a-4be5-11e9-968e-002590ea2218", 
        "f59d35fc-4bd1-11e9-a06c-002590ea2218", 
        "f63e7bd8-522a-11e9-843b-002590ea2218", 
        "fb97307c-513d-11e9-b661-0cc47a172970", 
        # End of 3-tier transactions

        '84cfa6de-54dc-11e9-8f4d-0cc47a172970', #	8	cloudpayments_test	2019-04-02 03:16:11
        'ffd03942-54d8-11e9-ad31-002590ea2218', #	7	tvzpromo	2019-04-02 02:50:59
        '13f71352-54d7-11e9-9304-002590ea2218', #	3	tvzavrwallet	2019-04-02 02:37:14
        '231d5dc6-54d4-11e9-aab0-0cc47a172970', #	8	cloudpayments_test	2019-04-02 02:16:11
        '5f8af814-54d3-11e9-887d-0cc47a172970', #	8	cloudpayments	2019-04-02 02:10:46
        '08ed65dc-54d3-11e9-9061-0cc47a172970', #	8	cloudpayments	2019-04-02 02:08:18
        '279b92ee-54d1-11e9-8bc4-0cc47a172970', #	8	applestore	2019-04-02 01:54:50
        'd125ab44-54cf-11e9-a757-002590ea2218', #	7	tvzpromo	2019-04-02 01:45:15
        '9c7b1870-54cf-11e9-9239-002590ea2218', #	8	applestore	2019-04-02 01:43:48
        '5cc95050-54cc-11e9-a96d-002590ea2218', #	3	tvzavrwallet	2019-04-02 01:20:31
        'c13669f2-54cb-11e9-889f-0cc47a172970', #	8	cloudpayments_test	2019-04-02 01:16:11
        '2c5ecf90-54cb-11e9-a31e-002590ea2218', #	7	tvzpromo	2019-04-02 01:12:01
        'c2b7c146-54ca-11e9-8d11-002590ea2218', #	8	applestore	2019-04-02 01:09:04
        '29e0dbe2-54ca-11e9-99e4-002590ea2218', #	8	cloudpayments	2019-04-02 01:04:48
        '73f2c7dc-54c9-11e9-b115-002590ea2218', #	8	applestore	2019-04-02 00:59:42
        '3b6bdc64-54c9-11e9-9c06-002590ea2218', #	8	applestore	2019-04-02 00:58:08
        '9ebfa45e-54c8-11e9-9c82-002590ea2218', #	8	applestore	2019-04-02 00:53:45
        '34ec1062-54c8-11e9-85ae-0cc47a172970', #	8	cloudpayments	2019-04-02 00:50:50
        'b607bd32-54c7-11e9-8130-002590ea2218', #	7	tvzpromo	2019-04-02 00:47:14
        '1dbb3cea-54c5-11e9-8610-0cc47a172970', #	8	mixplatnew	2019-04-02 00:29:31
        '14b56f72-1f46-44d5-b553-a9a3ec1edf0d', #	8	cloudpayments	2019-04-02 00:24:44
        '5fd354ca-54c3-11e9-8ea8-0cc47a172970', #	8	cloudpayments_test	2019-04-02 00:16:11
        'b6c86cbc-54c2-11e9-a857-002590ea2218', #	8	cloudpayments	2019-04-02 00:11:28
        'a024dfea-54c2-11e9-94de-002590ea2218', #	8	mixplatnew	2019-04-02 00:11:14
        'a3dca172-54c2-11e9-b9fd-0cc47a172970', #	3	tvzavrwallet	2019-04-02 00:10:56
        'f7bc430c-54c1-11e9-b7b4-0cc47a172970', #	7	tvzpromo	2019-04-02 00:06:07
        'ac0f4d14-54c1-11e9-a7e8-002590ea4448', #	8	cloudpayments	2019-04-02 00:04:01
        '5e362b22-54c0-11e9-8098-002590ea2218', #	3	tvzavrwallet	2019-04-01 23:54:40
        'd4448292-54bf-11e9-afe6-0cc47a172970', #	8	cloudpayments	2019-04-01 23:50:50
        '4b5fe2f2-54bd-11e9-8525-0cc47a172970', #	8	cloudpayments	2019-04-01 23:32:41
        'ca7c38ca-54bc-11e9-9d55-0cc47a172970', #	3	tvzavrwallet	2019-04-01 23:29:04
        'a4fad3cc-54bc-11e9-bf55-0cc47a172970', #	8	cloudpayments_test	2019-04-01 23:28:01
        'd2d6aaba-54bb-11e9-ab79-002590ea2218', #	8	tvzpromo	2019-04-01 23:22:08
        '17eff184-54bb-11e9-9a5a-0cc47a172970', #	8	tvzpromo	2019-04-01 23:16:54
        'fe316642-54ba-11e9-bb79-0cc47a172970', #	8	cloudpayments_test	2019-04-01 23:16:12
        'f7707d52-54ba-11e9-b66d-002590ea4448', #	8	cloudpayments	2019-04-01 23:16:01
        'b9f1217a-54ba-11e9-939e-0cc47a172970', #	7	tvzpromo	2019-04-01 23:14:17
        '95fb2ef0-54ba-11e9-a7cd-0cc47a172970', #	3	tvzavrwallet	2019-04-01 23:13:16
        '1e839646-54ba-11e9-a8fc-002590ea2218', #	7	tvzpromo	2019-04-01 23:09:56
        '567c0846-54b8-11e9-bcc5-002590ea2218', #	3	tvzavrwallet	2019-04-01 22:57:11
        '06f45c24-54b8-11e9-b387-0cc47a172970', #	7	tvzpromo	2019-04-01 22:54:58
        'f784d502-54b7-11e9-86e8-002590ea2218', #	7	tvzpromo	2019-04-01 22:54:32
        '697c9a1a-93c1-45b4-881b-dfdc6a9e469d', #	8	cloudpayments	2019-04-01 22:50:51
        'd20c01c0-54b6-11e9-8be0-0cc47a172970', #	7	tvzpromo	2019-04-01 22:46:19
        'e22ca24a-54b5-11e9-a719-0cc47a172970', #	7	tvzpromo	2019-04-01 22:39:37
        '33103f60-54b5-11e9-a4fd-002590ea2218', #	8	cloudpayments	2019-04-01 22:34:44
        '92a23bc8-54b4-11e9-a124-0cc47a172970', #	8	cloudpayments	2019-04-01 22:30:15
        '6a467af4-54b4-11e9-938f-0cc47a172970', #	8	cloudpayments	2019-04-01 22:29:07
        'fa12870a-54b3-11e9-b36c-002590ea2218', #	3	tvzavrwallet	2019-04-01 22:25:58
        'f306052c-54b3-11e9-9fcc-002590ea2218', #	7	tvzpromo	2019-04-01 22:25:46
        'c57632e4-54b3-11e9-8f87-002590ea2218', #	8	cloudpayments	2019-04-01 22:24:31
        'c06b39b2-54b2-11e9-846c-0cc47a172970', #	3	tvzavrwallet	2019-04-01 22:17:12
        'bac01c08-54b2-11e9-99f0-0cc47a172970', #	8	cloudpayments_test	2019-04-01 22:17:02
        '6f77add8-54b2-11e9-ba19-0cc47a172970', #	8	cloudpayments	2019-04-01 22:14:57
        '54eb474a-54b2-11e9-9c18-0cc47a172970', #	3	tvzavrwallet	2019-04-01 22:14:11
        '418d4f4a-54b2-11e9-86fd-0cc47a172970', #	7	tvzpromo	2019-04-01 22:13:39
        '2c2f7358-54b2-11e9-b805-0cc47a172970', #	8	cloudpayments_test	2019-04-01 22:13:03
        '98aebc06-54b1-11e9-aee1-002590ea2218', #	8	cloudpayments	2019-04-01 22:08:58
        '2350c7ba-54b1-11e9-8f6d-0cc47a172970', #	8	cloudpayments	2019-04-01 22:05:39
        'deb440a0-54b0-11e9-8a0b-002590ea2218', #	8	cloudpayments	2019-04-01 22:03:48
        'ccbe034a-54b0-11e9-9813-002590ea2218', #	7	tvzpromo	2019-04-01 22:03:13
        '68234864-54b0-11e9-ba65-002590ea2218', #	7	tvzpromo	2019-04-01 22:00:25
        '5bf17cfa-54b0-11e9-9b6c-0cc47a172970', #	7	tvzpromo	2019-04-01 22:00:04
        'a8eec39c-54af-11e9-a08c-002590ea2218', #	7	tvzpromo	2019-04-01 21:55:04
        '8c1ec960-54af-11e9-9404-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:54:15
        'ca9682f6-54ae-11e9-885e-0cc47a172970', #	8	cloudpayments	2019-04-01 21:48:52
        '1ecd8942-54ae-11e9-8460-002590ea2218', #	7	tvzpromo	2019-04-01 21:44:03
        '36611a34-54ad-11e9-96d5-0cc47a172970', #	7	tvzpromo	2019-04-01 21:37:33
        '76ad0a5e-54ac-11e9-8cc6-002590ea2218', #	7	tvzpromo	2019-04-01 21:32:11
        'c7cc634c-e8ad-47be-b3d3-94d88c3829b7', #	8	cloudpayments	2019-04-01 21:29:58
        '221023b4-54ac-11e9-a6e0-0cc47a172970', #	3	tvzavrwallet	2019-04-01 21:29:49
        'f4f31508-54ab-11e9-be87-0cc47a172970', #	7	tvzpromo	2019-04-01 21:28:33
        'b09f28ec-54ab-11e9-a955-002590ea2218', #	7	tvzpromo	2019-04-01 21:26:39
        'a7a32252-54ab-11e9-99d0-002590ea2218', #	7	tvzpromo	2019-04-01 21:26:24
        '5ed27668-54ab-11e9-9cd3-002590ea2218', #	7	tvzpromo	2019-04-01 21:24:21
        '52021416-54ab-11e9-8c63-002590ea4448', #	3	tvzavrwallet	2019-04-01 21:24:00
        '3e0c2f8c-54ab-11e9-87f2-002590ea2218', #	8	cloudpayments	2019-04-01 21:23:28
        '3e04456a-54ab-11e9-813a-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:23:26
        'f8c371f6-54aa-11e9-91bd-002590ea2218', #	8	tvzpromo	2019-04-01 21:21:30
        'e122ea54-54aa-11e9-9617-002590ea2218', #	8	tvzpromo	2019-04-01 21:20:51
        'e11e424c-54aa-11e9-b398-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:20:51
        'c5ddfa68-54aa-11e9-a6dc-002590ea2218', #	8	cloudpayments	2019-04-01 21:20:08
        'c5d5fd5e-54aa-11e9-9133-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:20:05
        'c30423c6-54aa-11e9-82e7-002590ea4448', #	3	tvzavrwallet	2019-04-01 21:20:00
        '8b5d5492-54aa-11e9-aeae-002590ea2218', #	7	tvzpromo	2019-04-01 21:18:27
        '873d8dd2-54aa-11e9-8bc7-002590ea2218', #	8	cloudpayments	2019-04-01 21:18:21
        '7a1f9e2e-54aa-11e9-9920-002590ea2218', #	8	cloudpayments	2019-04-01 21:17:59
        '7a13542a-54aa-11e9-a471-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:17:58
        '4c311e3e-54aa-11e9-85fc-0cc47a172970', #	8	cloudpayments	2019-04-01 21:16:42
        '4c2abf26-54aa-11e9-94c1-0cc47a172970', #	3	tvzavrwallet	2019-04-01 21:16:41
        '3c6f7338-54aa-11e9-b928-0cc47a172970', #	8	cloudpayments_test	2019-04-01 21:16:15
        '3c67b436-54aa-11e9-bee5-0cc47a172970', #	3	tvzavrwallet	2019-04-01 21:16:14
        '072cfba0-54aa-11e9-ad07-002590ea2218', #	8	cloudpayments	2019-04-01 21:14:46
        '07233b6a-54aa-11e9-a48e-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:14:45
        'a33d9190-54a9-11e9-b62f-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:11:57
        '6ecea8fe-54a9-11e9-8d62-002590ea2218', #	7	tvzpromo	2019-04-01 21:10:29
        'b77dd3aa-54a8-11e9-a2a2-0cc47a172970', #	3	tvzavrwallet	2019-04-01 21:05:22
        'a3c6bd0e-54a8-11e9-aa0a-0cc47a172970', #	3	tvzavrwallet	2019-04-01 21:04:49
        'a1f429bc-54a8-11e9-b870-002590ea2218', #	8	cloudpayments	2019-04-01 21:04:47
        'a1ee79a4-54a8-11e9-afe5-002590ea2218', #	3	tvzavrwallet	2019-04-01 21:04:46

        # Direct deposit:
        '00009e4c-7a31-4dad-a5c0-9939f167d1c1',

        # Partial trial:
        # '00038826-1cce-11e9-a7b6-0cc47a172970',
        # '0000b7a4-1cce-11e9-899e-0cc47a172970'

        # '0186dc66-2179-11e9-85d1-0cc47a172970'

    ]

    trackers = [
        {
            "envelope": {
                "transactionId":    t, # <- from FrontEnd!!!

                # "tvzPlf":           "<?>", # <- from FrontEnd?
                "gaTrackerId":      "UA-125243419-1",

                "gaClientId":       "<gaClientId>", # <- from FrontEnd
                "tvzCustomerId":    "<tvzCustomerId>", # <- from DB

                "originPage": "/film/my-millery/?fake_payment=1",
                "pageTitle": "Фильм  Мы – Миллеры  смотреть онлайн в HD качестве — tvzavr.ru",
                "cids": "UA-97389153-4_cid::1662994990.1554284714|UA-125243419-1_cid::1662994990.1554284714|UA-132525321-1_cid::1662994990.1554284714",
            },
            "headers_info": {
                "user-agent": "<userAgent>",
            },
            "cookies": {},

        } for t in _fake_transactions
    ]

    return trackers


@heap.store
def decode_trackers(ctx):
    """
    Mapping function
    """

    def extract_cid(text, gaTrackerId):
        delimiter = "_cid::"
        if text.find(delimiter) < 0:
            return "NOT_FOUND"
        pairs = dict(_.map(text.split("|"), lambda p: p.split(delimiter)))
        # log.debug("PAIRS::: {}".format(pairs))
        return pairs.get(gaTrackerId, "ERROR")

    # trackers = heap.pull("fetch_trackers")
    if not ctx:
        return None

    trackers = list(ctx)
    # log.debug("TRACKERS: {}".format(trackers))
    decoded = []
    for item in trackers:
        envelope = item["envelope"]
        headers = item["headers_info"]
        sandbox_mode = "use_test_counter" in envelope
        gaTrackerId = "UA-125243419-1"
        if sandbox_mode:
            gaTrackerId = "UA-125243419-1"
        # cookies = item["cookies"]
        metadata = {
            "transactionId":    envelope["transactionId"], # <- from FrontEnd!!!

            # "_raw": parsed.copy(),
            # "tvzPlf":           envelope["tvzPlf"], # <- from FrontEnd?
            # "tvzPlf": envelope.get("tvzPlf", "?"), # <- from FrontEnd?
            # "gaTrackerId": parsed["envelope"]["gaTrackerId"], # <- from FrontEnd?
            "gaTrackerId":      gaTrackerId,
            # "gaClientId":       envelope["gaClientId"], # <- from FrontEnd
            "gaClientId":       extract_cid(envelope["cids"], gaTrackerId), # <- from FrontEnd
            # "tvzCustomerId":    envelope["tvzCustomerId"], # <- from DB
            "pageTitle":        envelope["pageTitle"],
            "originResourcePath": envelope["originPage"],
            "userAgent":        headers["user-agent"],
            "traceMode":         "trace_message" in envelope and not sandbox_mode,
            "sandboxMode":          sandbox_mode,
        } 
        decoded.append(metadata)
    transactions_string = ",".join(["\"{}\"".format(t["transactionId"]) for t in decoded])
    return decoded


@heap.store
def annotate_operations(ctx):
    """
    Read "transaction_operation", extend trackers
    """

    if not ctx:
        return None

    # pushed_transactions = heap.pull("decode_trackers")
    pushed_transactions = list(ctx)
    pushed_transactions_ids = _.pluck(pushed_transactions, "transactionId")

    transactions_string = ",".join(["\"{}\"".format(id) for id in pushed_transactions_ids])

    # log.debug("annotate_operations INPUT: {}".format(pushed_transactions))

    # Get operations as groups of transactions:

    db = ConnectionPool.select(MySql,'MYSQL_BILLING')

    sql ="""
    select 
        transaction_id as transactionId, 
        operation_id as operationId, 
        transaction_type as transactionType
        from billing_dev.transaction_operation
        where operation_id in ( 
            select 
                operation_id 
                from billing_dev.transaction_operation
                where transaction_id in ({})
            )
    """.format(transactions_string)

    operations = db.get_records(sql)

    # log.debug('Operations ===================> \n{}\n'.format(operations))

    # If some operations not found in "transaction_operation" - pass them from  pushed_transactions with "simple" flag

    # decoded = _.Chain(pushed_transactions).map(lambda et: )

    complex_ops_ids = set(_.pluck(operations, 'transactionId'))

    # These transactions are absent in transaction_operation table:
    simple_ops_ids = [id for id in pushed_transactions_ids if id not in complex_ops_ids]

    all_ids = list(simple_ops_ids) + list(complex_ops_ids)

    try_attr = lambda v, name: v and v[name] or None

    def find_incoming_transaction(operations, pushed_transactions, transactionId):
        """
        Find "incoming" transaction from adjacent trackers (with the same "operationId")
        """
        enclosing_operation = _.find(
            operations, lambda o: o["transactionId"] == transactionId
        )["operationId"]

        adjacent_ids = _.chain(
                operations
            ).filter(
                lambda o: o["operationId"] == enclosing_operation
            ).pluck(
                "transactionId"
            ).value

        incoming = _.chain(
                pushed_transactions
            ).find(
                lambda t: t["transactionId"] in adjacent_ids
            ).pick(
                "gaTrackerId",
                "gaClientId", 
                "tvzCustomerId", 
                "pageTitle",
                "originResourcePath",
                "userAgent",
                "cookies",
                "traceMode", 
                "sandboxMode",
            ).value
        
        return incoming


    mapped = _.map(
        all_ids, 
        lambda transactionId: _.extend(
            {"transactionId": transactionId},
            _.chain(
                    operations
                ).find_where(
                    {"transactionId": transactionId}
                ).pick(
                    "operationId", "transactionType"
                ).value,
            _.find_where(
                    pushed_transactions, 
                    {"transactionId": transactionId}
                ) or find_incoming_transaction(operations, pushed_transactions, transactionId),
        )
    )

    return {
        "ids":      all_ids,
        "simple_ops_ids": list(simple_ops_ids),
        "complex_ops_ids": list(complex_ops_ids),
        "mapped":   list(mapped),
    }


@heap.store
def annotate_transactions(ctx):
    
    if not ctx: 
        return None

    annotated = ctx

    ids = annotated["ids"]
    simple_ops_ids = annotated["simple_ops_ids"]
    complex_ops_ids = annotated["complex_ops_ids"]
    mapped = annotated["mapped"]

    # transactions = heap.pull("search_transaction_operation")
    transactions_string = ",".join(["\"{}\"".format(t) for t in ids])

    db = ConnectionPool.select(MySql,'MYSQL_BILLING')

    sql = """select 
            id as transactionId,
            user_id as tvzCustomerId,
            type as transactionType,
            shop_id as shopId,
            ps_id as paymentSystemId,
            product_id as productId,
            created as timeStamp,
            updated,
            amount,
            status,
            remote_id,
            shop_f1 as tvzPlf,
            foreign_amount as foreignAmount,
            foreign_currency as currency 
            from billing_dev.transaction 
            where id in ({})""".format(transactions_string)
    
    # log.debug('SQL ===================> \n{}\n'.format(sql))

    records = db.get_records(sql)    

    # # Annotate with Operations IDs:
    # records = _.map(records, lambda r: \
    #     _.extend(r, {'operation_id': transactions['by_id'][r['id']]['operation_id']}))

    # log.debug('Details ===================> \n{}\n'.format(records))

    # grouped = _.group_by(records, 'operation_id')
    # def print_items(r):
    #     print('item ===>', r, '+++\n')
    #     return {}

    result = _.chain(mapped).map(
        lambda rec: _.extend({},
            rec,
            # {"transactionId": transactionId},
            _.chain(records).find_where({"transactionId": rec["transactionId"]}).pick(
                # "operationId", 
                "tvzCustomerId",
                "transactionType",
                "shopId",
                "paymentSystemId",
                "productId",
                "timeStamp",
                "amount",
                "status",
                "tvzPlf",
                "foreignAmount",
                "currency",
                ).value,
        )
    ).value

    # log.debug('Grouped 2 ===================> \n{}\n'.format(grouped))

    # sublime = lambda r: \
    #     {
    #         # 'subject': _.filter(r, lambda v: v['status'] in (3,7)),
    #         'history': r
    #     }
    # summary = _.map(grouped, sublime)

    # result = {
    #     'subject': [],
    #     'transactions': records
    # }

    return result


@heap.store
def normalize_operations(ctx):

    if not ctx: 
        return None

    transactions = ctx
    counter = itertools.count()
    # 1. Assign Ids for fake operations (single-pass transactions)
    transactions = _.map(transactions, lambda t: t if "operationId" in t else _.extend(t, {
        "operationId": str(next(counter)),
        "singlePassOperation": True
    }))
    # 2. Group group by operations
    # by_operation = _.group_by(transactions, "operationId")
    # 3. Move grouped in "transactions" attribute
    operations = _.reduce(transactions, 
        lambda memo, t:\
            _.extend({}, memo, {
                t["operationId"]: {
                    "transactions":         memo.get(t["operationId"], {}).get("transactions", []) + [t],
                    "transactionsCount":    memo.get(t["operationId"], {}).get("transactionsCount", 0) + 1 
                }
            }), {})
    
    return operations


@heap.store
def explore_transactions(ctx):
    """
    Detect subject of transactions, ...
    """

    product_cell = re.compile(r'^(\d*)(?:\-(\d*))?$')

    intermediate_cell = re.compile(r'^[^\-]*\-[^\-]*\-[^\-]*\-[^\-]*\-[^\-]*$')

    def is_reference_cell(cell):
        return cell and intermediate_cell.search(cell) is not None

    def is_product_cell(cell):
        return cell and product_cell.search(cell) is not None

    def decode_product(cell):
        def smart_int(v):
            if v is None: return v 
            return int(v)
        cleaned_cell = cell.strip()
        match = product_cell.search(cleaned_cell)
        if match is None: 
            return (None, None)
        mg = match.groups()
        return smart_int(mg[0]), smart_int(mg[1])

    if not ctx: 
        return None

    operations = ctx

    notifications = []
    banned_systems = [
        "applestore_test",
        "cloudpayments_test",
        "cloudpayments_tst1",
        "googleplay_test",
        "mixplatnew_test",
        "mixplatnew_tst1",
        "mixplattest",
        "payturetest",
        "samsung_test",
        "tvzavradmin",
    ]

    def filter_unresolved(t):
        """
        Sometimes transaction record has no "status" attribute. Why? 
        Looks like no record with such transactionId in "transactions" db table (?)
        Log such transactionsa, filter them from further processing.
        Field "status" comes from billing DB
        """
        is_resolved = "status" in t
        if is_resolved:
            return True
        log.error("Incomlete transaction record: {}".format(t))
        return False

    for operationId, rec in operations.items():
        # Filter only successfull:
        transactions = _.chain(rec["transactions"]).filter(
            filter_unresolved
        ).filter(
            lambda t: \
                t["status"] in ACK and t["sandboxMode"] or not t["paymentSystemId"] in banned_systems
        ).value
        # find final:
        terminal = _.filter(
            transactions, lambda t: t["productId"] and product_cell.search(t["productId"]) is not None)
        
        sources = _.chain(transactions).filter(
            lambda t: \
                t["transactionType"] in (DEPOSIT, OVERDRAFT) \
                    or (t["transactionType"] == WITHDRAWAL and is_reference_cell(t["productId"]))
        ).map(lambda t: _.pick(t, "paymentSystemId", "amount", "currency", "status", "shopId", "transactionType")).value
        
        target = _.chain(transactions).filter(
            lambda t: \
                t["transactionType"] in (WITHDRAWAL, OVERDRAFT) and is_product_cell(t["productId"])
        ).map(lambda t: _.pick(t, "productId", "amount", "currency", "status", "shopId", "transactionType")).value

        passthrought = _.chain(transactions).filter(lambda t: t["transactionType"] == OVERDRAFT).map(lambda t: _.pick(t, "productId", "paymentSystemId", "amount", "currency", "status", "shopId", "transactionType")).value

        # if len(terminal) != 1:
        #     log.error("Too many terminal transactions: {}".format(rec))
        #     continue
 
        # terminal = terminal.pop()

        # Detect all cases (promo, partial promo, test, ...)
        # Mark 100%=promo transactions to drop:

        # product
        # tariffId, clipId, wallet = decode_product(terminal["productId"])

        deposit_amount = _.reduce(sources, lambda memo, s: memo + s["amount"], 0)

        amount = _.reduce(target, lambda memo, s: memo + s["amount"], 0)

        promo_amount = _.chain(sources).filter(
                lambda s: s["shopId"] == "tvzavrpromo"
            ).reduce(
                lambda memo, s: memo + s["amount"], 0
            ).value

        promo_deposit_amount = _.chain(sources).filter(
                lambda s: s["shopId"] == "tvzavrpromo"
            ).reduce(
                lambda memo, s: memo + s["amount"], 0
            ).value

        if target:
            target = target.pop()
            tariffId, clipId = decode_product(target["productId"])
            wallet = False 
            
        else:
            tariffId, clipId, wallet = None, None, None
            if deposit_amount:
                wallet = True

        if len(transactions) == 0:
            log.debug("Refused transactions??? -> {}".format(rec["transactions"]))
            continue
        
        result_amount = amount or deposit_amount

        notification = _.extend({}, {
            "clipId":   clipId,
            "tariffId": tariffId,
            "wallet":   wallet,
            "operationId": operationId,
            "amount": deposit_amount if wallet else amount,
            "promoAmount": promo_deposit_amount if wallet else promo_amount,
            "DEBUG": {
                "sources": sources,
                "target": target,
                "passthrought": passthrought,
            }
        }, _.pick(transactions[0],
            "transactionId",
            "tvzPlf",
            "gaTrackerId",
            "gaClientId",
            "tvzCustomerId",
            "originResourcePath",
            "pageTitle",
            "userAgent",
            "cookies",
            "paymentSystemId",
            "timeStamp",
            # "amount",
            "currency",
            "traceMode",
            "sandboxMode",
        ))
        notifications.append(notification)
        # _.extend(operations[operationId], {
        #     "notification": notification
        # })
        # operations[operationId]["terminal"] = terminal

        operations[operationId]["sources"] = sources
        operations[operationId]["target"] = target
        operations[operationId]["passthrought"] = passthrought

    return {
        "operations": operations,
        "notifications": notifications,
    }


# @heap.store
# def filter_notifications(ctx):
#     if not ctx: 
#         return None

#     data = ctx
#     operations = data["operations"]
#     notifications = data["notifications"]

#     notifications = _.chain(notifications).filter(
#         lambda n: not(n[shop])
#     )


@heap.store
def annotate_subject(ctx):
    if not ctx: 
        return None

    data = ctx
    operations = data["operations"]
    notifications = data["notifications"]

    clipsIds = _.chain(notifications).pluck("clipId").filter(lambda r: r is not None).value
    tariffsIds = _.chain(notifications).pluck("tariffId").filter(lambda r: r is not None).value

    if clipsIds:
        # """
        # class CLIP_TYPES(object):
        # "Constant values instead of ForeignKey to 'clip_types' table "
        # # id from clip_types
        # SEASON = 5
        # SET = 2
        # SET_ELEMENT = 3
        # SINGLE = 1
        # """

        ids = ",".join(["\"{}\"".format(id) for id in clipsIds])
        
        db = ConnectionPool.select(MySql, 'MYSQL_VK')
        
        sql ="""
            select id, name, meganame, issue as year, type_id from vk.clip where id in ({})
            """.format(ids)
        clip_info = db.get_records(sql)

        sql ="""
            select clip_id, mark_id from vk.clip_mark where clip_id in ({})
            """.format(ids)
        clip_marks = db.get_records(sql)

        def get_title(clip):
            if clip is None:
                return "Not found!!!"
            return clip["meganame"] or clip["name"]

        def get_category(clip):
            if clip is None:
                return "Not found!!!"
            clipId = clip["id"]
            marks = _.chain(clip_marks).filter(lambda m:m["clip_id"] == clipId).pluck("mark_id").value
            if 71 in marks:
                return "Фильмы"
            if 675 in marks:
                return "Сериалы"
            if 678 in marks:
                return "Мультфильмы"
            return "Прочее"

        for ntf in notifications:
            clipId = ntf["clipId"]
            clip = _.find(clip_info, lambda c: c["id"] == clipId)
            if clipId is None:
                clipName = None 
                clipCategory = None
            else:
                clipName = get_title(clip)
                clipCategory = get_category(clip)

            _.extend(ntf, {
                "clipName": clipName,
                "clipCategory": clipCategory
            })

    if tariffsIds:

        ids = ",".join(["\"{}\"".format(id) for id in tariffsIds])
        
        db = ConnectionPool.select(MySql, 'MYSQL_VK')
        
        sql ="""
            select id, name as tariffName, vod_system as tariffVod from vk.tariff where id in ({})
            """.format(ids)
        tariff_info = db.get_records(sql)
        # log.debug('SQL ===================> \n{}\n'.format(sql))
        # log.debug('TARIFFS ===================> \n{}\n'.format(tariff_info))
        for ntf in notifications:
            tariffId = ntf["tariffId"]
            tariff = _.find(tariff_info, lambda c: c["id"] == tariffId)
            _.extend(ntf, _.pick(tariff, "tariffName", "tariffVod"))
    
    return {
        "operations": operations,
        "notifications": notifications,
    }


@heap.store
def encode_ga_ecomm_event(ctx):

    # trackers = heap.pull("decode_trackers")
    if not ctx:
        return None

    notifications = ctx["notifications"]
    operations = ctx["operations"]

    messages = []
    
    for t in notifications:

        # locationInfo = "" # location.pathname + location.hash + location.search
        title = "<title>"
        amount = t["amount"]
        promo_amount = t["promoAmount"]
        amount -= promo_amount

        # Ignore 100% promo
        if amount == 0:
            continue


        tariffId = t.get("tariffId", "id")
        tariffName = t.get("tariffName") or t.get("paymentSystemId")
        tariffVod = t.get("tariffVod", "vod?")

        isSubscription = tariffVod.lower() == "svod"

        if isSubscription:
            # Подписка
            subjectId = tariffId
            subjectName = tariffName
            extCat = "Подписка"
            ea = "Подписка"
        elif t["clipId"]:
            # Фильм
            subjectId = t["clipId"]
            subjectName = t["clipName"]
            extCat = t["clipCategory"]
            ea = "Фильм"
        elif t["wallet"] is not None:
            # Кошелек
            subjectId = tariffId
            subjectName = tariffName
            extCat = ""
            ea = "Пополнение"
        else:
            # "Непойми что"?
            subjectId = ""
            subjectName = ""
            extCat = ""
            ea = "Invalid data in billing!"

        ga_event_data = {
            "v":    1,
            "t":    "event",
            "tid":  t["gaTrackerId"],
            "cid":  t["gaClientId"],
            "uid":  t["tvzCustomerId"],
            "dh":   "tvzavr.ru",
            "dp":   t["originResourcePath"],
            "dt":   t["pageTitle"], # From DB????
            "pa":   "purchase",
            "ti":   t["transactionId"],
            "tr":   amount,
            "pr1id": subjectId, # Tariff or Clip. NB: Clip can be purchased by different tariffs!
            "pr1nm": subjectName,
            "pr1ca": extCat, # Subscription | Film | Cartoon | Episode
            "pr1pr": amount, 
            "pr1qt": "1",
            "pr1ps": "1",
            "ea":   ea,
            "el":   amount,
            "ec":   "buy",
            "__trace_mode__": t["traceMode"]
        }

        messages.append(ga_event_data)
    
    return {
        "messages": messages,
        # "operations": operations,

        "notifications": notifications
    }


@heap.store
def send_ga_ecomm_event(ctx):
    def post(payload):
        text_buff = '\n'.join(payload)
        # log.debug('buffer: {}'.format(text_buff))
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        resp = requests.post(ga_endpoint, text_buff, headers=headers)
        if resp.status_code >= 400:
            log.error("GA error: {}; {}".format(resp.status_code, resp.text))

    # trackers = heap.pull("decode_trackers")
    if not ctx:
        return None
        
    messages = ctx["messages"]
    notifications = ctx["notifications"]
    ga_endpoint = 'https://www.google-analytics.com/batch'
    data_size = 0
    raw_notificaitons = []
    payload = []
    chunks_count = 0

    for cnt, ga_event_data in enumerate(messages):
        chunk_no = cnt // 20
        if chunk_no > chunks_count:
            chunks_count = chunk_no
            post(payload)
            payload = []
            log.debug("Chunk dumped (due to count > 20): {}".format(chunks_count))

        # raw_notificaitons.append(ga_event_data)

        trace_mode = ga_event_data.pop("__trace_mode__")

        if trace_mode:
            msg = "===> trace notification: {}".format(ga_event_data)
            log.info(msg)
            # Ignore test data, output only to log:
            continue

        row = urllib.parse.urlencode(ga_event_data)
        row_size = len(row) + 1 # Take \n into account

        if data_size + row_size> 16000:
            post(payload)
            payload = []
            log.debug("Chunk dumped (due to size over 16k): {}".format(data_size))
            data_size = 0

        payload.append(row)
        data_size += row_size

    if payload:
        post(payload)
    
    return {
        "messages": messages,
        "notifications": notifications,
    }
    

connector = fetch_trackers
test_connector = fake_trackers

def run():
    source = fetch_trackers
    dest = send_ga_ecomm_event
    return run_with(source, dest)

def test():
    source = fake_trackers
    dest = lambda ctx: ctx
    return run_with(source, dest)

def run_with(source, dest):
    return Chain(
            source
        ).then(
            decode_trackers
        ).then(
            annotate_operations
        ).then(
            annotate_transactions
        ).then(
            normalize_operations
        ).then(
            explore_transactions
        ).then(
            annotate_subject
        ).then(
            encode_ga_ecomm_event
        ).then(
            dest
        )

