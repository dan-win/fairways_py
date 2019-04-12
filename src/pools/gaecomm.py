# -*- coding: utf-8 -*-
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
    _fake_operations= [
        "0071c064-5ace-11e9-84b2-002590ea2218", # 7, single
        "006103be-56a0-11e9-b335-002590ea2218", # 3, 8
        "003b2362-52a7-11e9-88a4-002590ea4448", # 3, 8
    ]

    trackers = [
        {
            "envelope": {
                "operationId":    t, # <- from FrontEnd!!! NOW IT CONTAINS OPERATION ID

                # "tvzPlf":           "<?>", # <- from FrontEnd?
                "gaTrackerId":      "UA-125243419-1",

                "gaClientId":       "<gaClientId>", # <- from FrontEnd
                "tvzCustomerId":    "<tvzCustomerId>", # <- from DB

                "originPage": "/film/my-millery/?fake_payment=1",
                "pageTitle": "Fake title — tvzavr.ru",
                "cids": "UA-97389153-4_cid::1662994990.1554284714|UA-125243419-1_cid::1662994990.1554284714|UA-132525321-1_cid::1662994990.1554284714",
            },
            "headers_info": {
                "user-agent": "<userAgent>",
            },
            "cookies": {},

        } for t in _fake_operations
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
            "operationId":    envelope["operationId"], # <- from FrontEnd!!!

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

    return decoded


@heap.store
def fetch_db_transaction_operation(ctx):
    """
    Read "transaction_operation", extend trackers
    """

    if not ctx:
        return None

    # pushed_transactions = heap.pull("decode_trackers")
    pushed_operations = list(ctx)
    pushed_operations_ids = _.pluck(pushed_operations, "operationId")

    transactions_string = ",".join(["\"{}\"".format(id) for id in pushed_operations_ids])

    # log.debug("fetch_db_transaction_operation INPUT: {}".format(pushed_transactions))

    # Get operations as groups of transactions:

    db = ConnectionPool.select(MySql,'MYSQL_BILLING')

    sql ="""
    select 
        transaction_id as transactionId, 
        operation_id as operationId, 
        transaction_type as transactionType
        from billing_dev.transaction_operation
        where operation_id in ({})
    """.format(transactions_string)

    transactions = db.get_records(sql)

    # log.debug('Operations ===================> \n{}\n'.format(transactions))

    # If some transactions not found in "transaction_operation" - pass them from  pushed_transactions with "simple" flag

    # decoded = _.Chain(pushed_transactions).map(lambda et: )

    transactions_ids = set(_.pluck(transactions, 'transactionId'))

    # Spread metadata from event to all transactions indexed by operation:
    mapped = \
        _.chain(
                transactions
            ).map(lambda t: \
                _.extend({}, t,
                    _.chain(
                            pushed_operations
                        ).find_where(
                            {"operationId": t["operationId"]}
                        ).pick(
                            "gaTrackerId",
                            "gaClientId", # <- from FrontEnd
                            "pageTitle",
                            "originResourcePath",
                            "userAgent",
                            "traceMode",
                            "sandboxMode",
                        ).value
                )
        ).value

    return {
        "transactions_ids":      transactions_ids,
        "mapped":   list(mapped),
    }


@heap.store
def fetch_db_transaction(ctx):
    
    if not ctx: 
        return None

    annotated = ctx

    transactions_ids = annotated["transactions_ids"]
    mapped = annotated["mapped"]

    # transactions = heap.pull("search_transaction_operation")
    transactions_string = ",".join(["\"{}\"".format(t) for t in transactions_ids])

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

    try:
        records = db.get_records(sql)    
    except Exception as e:
        log.error("Error in DB call *** '{}'; SQL: {}".format(e, sql))
        raise

    # # Annotate with Operations IDs:
    # records = _.map(records, lambda r: \
    #     _.extend(r, {'operation_id': transactions['by_id'][r['id']]['operation_id']}))

    # log.debug('Details ===================> \n{}\n'.format(records))

    # grouped = _.group_by(records, 'operation_id')
    # def print_items(r):
    #     print('item ===>', r, '+++\n')
    #     return {}

    result = \
        _.chain(
                mapped
            ).map(lambda rec: \
                _.extend({}, rec,
                    _.chain(
                            records
                        ).find_where(
                            {"transactionId": rec["transactionId"]}
                        ).pick(
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
    # counter = itertools.count()

    # # 1. Assign Ids for fake operations (single-pass transactions)
    # transactions = _.map(transactions, lambda t: t if "operationId" in t else _.extend(t, {
    #     "operationId": str(next(counter)),
    #     "singlePassOperation": True
    # }))
    
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
        "tvzavrgift",
        "tvzavrloyalty",
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
            log.info("Refused transactions??? -> {}".format(rec["transactions"]))
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
    
    if messages:
        log.info("Notifications ready: {}".format(messages))

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
            fetch_db_transaction_operation
        ).then(
            fetch_db_transaction
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

