# -*- coding: utf-8 -*-
import os, sys

import logging
logging.basicConfig(
    # filename='example.log', 
    format='gaecomm: %(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG)
log = logging.getLogger(__name__)

import re
import json
import itertools

import requests
import urllib

from enum import Enum, IntEnum

from hostapi.io import Heap, JsonStore, NullStore, Redis, Alchemy, MySql, ConnectionPool, DbTaskSet, json_stream

from hostapi.chains import Chain 

from hostapi.underscore import Underscore as _

buffer_path = os.getenv('EVENTMACHINE_BUFFER', './../buffer')

from ci import fakedb

FAKE_DB_MODE = os.getenv('FAKE_DB_MODE', False)
DB_FIXTURE_DATA = os.getenv("DB_FIXTURE_DATA", "")

# print(
#     "DEBUG:::::",
#     "|", 
#     fakedb.MODES.USE_FAKE, "|",
#     "FAKE_DB_MODE >>>", 
#     os.environ["FAKE_DB_MODE"], 
#     os.getenv("FAKE_DB_MODE"),
#     "DB_FIXTURE_DATA >>>", 
#     os.environ["DB_FIXTURE_DATA"], 
#     os.getenv("DB_FIXTURE_DATA")
# )
# Flags for test modes:
SANDBOX_MODE = os.getenv('SANDBOX_MODE', False)
LOG_ONLY = os.getenv("MUTE_NOTOFICATIONS", False)
# True in debug:
DO_NOT_FILTER_PS = os.getenv("DO_NOT_FILTER_PS", False)

settings = {
    "FAKE_DB_MODE": FAKE_DB_MODE,
    "DB_FIXTURE_DATA": len(DB_FIXTURE_DATA) > 0,
    "SANDBOX_MODE": SANDBOX_MODE,
    "LOG_ONLY": LOG_ONLY,
    "DO_NOT_FILTER_PS": DO_NOT_FILTER_PS
}

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

TRANSACTION_TYPES = (WITHDRAWAL, OVERDRAFT, DEPOSIT)

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


BANNED_PS_SYSTEMS = [
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
    'bta', 'eltex', 'tlk','ucell',
]

QA_TARIFFS = (262,341,342,343,344,575)


PLF_GROUP = {
   "3cr": "Telecom",
   "abt": "STB",
   "adr": "Mobile",
   "am1": "Web",
   "and": "Mobile",
   "apl": "Mobile",
   "aze": "Web",
   "azr": "Web",
   "bta": "Telecom",
   "bti": "Telecom",
   "bts": "Telecom",
   "btt": "Telecom",
   "ctv": "Telecom",
   "dtv": "Telecom",
   "dun": "STB",
   "egr": "Web",
   "elx": "Telecom",
   "fm1": "Web",
   "fo3": "Web",
   "fxm": "SmartTV",
   "g11": "Web",
   "gn4": "Web",
   "gn5": "Web",
   "gn6": "Web",
   "gn7": "Web",
   "gn8": "Web",
   "gn9": "Web",
   "gtv": "Web",
   "hcs": "SmartTV",
   "htm": "Web",
   "imp": "Telecom",
   "ios": "Mobile",
   "itv": "Telecom",
   "kar": "Web",
   "kat": "Telecom",
   "kbr": "ExternalSite",
   "kcl": "Telecom",
   "kpr": "Web",
   "ksr": "ExternalSite",
   "ler": "SmartTV",
   "let": "SmartTV",
   "lgn": "SmartTV",
   "lgs": "SmartTV",
   "liv": "Web",
   "mag": "STB",
   "med": "Web",
   "mir": "Web",
   "mo4": "Web",
   "mrt": "Web",
   "mva": "Mobile",
   "mvi": "Mobile",
   "mvl": "Telecom",
   "nth": "SmartTV",
   "ntr": "SmartTV",
   "nu1": "Web",
   "nur": "Web",
   "ot1": "Web",
   "otm": "Web",
   "phl": "SmartTV",
   "phn": "SmartTV",
   "pnc": "SmartTV",
   "pns": "SmartTV",
   "psk": "Telecom",
   "rca": "Mobile",
   "rcf": "Web",
   "rch": "Web",
   "rci": "Mobile",
   "rcl": "SmartTV",
   "rcp": "SmartTV",
   "rcs": "SmartTV",
   "rcw": "Web",
   "rcx": "SmartTV",
   "rcy": "SmartTV",
   "rmb": "STB",
   "rst": "Web",
   "s11": "Web",
   "s12": "Web",
   "s13": "Web",
   "s14": "Web",
   "s15": "Web",
   "s16": "Web",
   "s17": "Web",
   "s18": "Web",
   "s19": "Web",
   "s20": "Web",
   "s21": "Web",
   "s22": "Web",
   "s23": "Web",
   "s24": "Web",
   "s25": "Web",
   "s26": "Web",
   "s27": "Web",
   "s28": "Web",
   "s29": "Web",
   "s30": "Web",
   "sce": "SmartTV",
   "scr": "SmartTV",
   "si1": "Web",
   "smg": "SmartTV",
   "smp": "SmartTV",
   "spu": "Web",
   "sra": "SmartTV",
   "st1": "Web",
   "st2": "Web",
   "st3": "Web",
   "sta": "SmartTV",
   "stb": "STB",
   "std": "SmartTV",
   "stv": "SmartTV",
   "svp": "Web",
   "tas": "Web",
   "tdm": "Telecom",
   "tel": "Web",
   "tlk": "Telecom",
   "tll": "Telecom",
   "tlt": "Telecom",
   "tnt": "Telecom",
   "tsh": "SmartTV",
   "ttc": "Telecom",
   "tva": "SmartTV",
   "tvz": "Web",
   "tza": "Mobile",
   "tzf": "Web",
   "tzi": "Mobile",
   "u12": "Web",
   "ukz": "Web",
   "uzb": "Web",
   "uzp": "Web",
   "vid": "Web",
   "vl4": "Web",
   "vl5": "Web",
   "vl6": "Web",
   "vls": "Web",
   "vlu": "Web",
   "xmi": "SmartTV",
   "zea": "SmartTV"
}

ATTR_TEMPLATES = {
    "Web": {
        "TMPL_TITLE": "{pageTitle}",
        "TMPL_HOST": "tvzavr.ru",
        "TMPL_URI": {
            "clip":         "{originResourcePath}",
            "subscription": "{originResourcePath}",
            "wallet":       "{originResourcePath}",
            "unknown":      "{originResourcePath}",
        },
        "TMPL_TRANSACT_INFO": "{timeStamp} | {tvzCustomerId}",
    },
    "SmartTV": {
        "TMPL_TITLE": "{pageTitle}",
        "TMPL_HOST": "{tvzPlf}/{tvzStvPlfName}.com",
        "TMPL_URI": {
            "clip":         "/video/description/{clipSeoAlias}",
            "subscription": "/subscriptions",
            "wallet":       "/profile/account",
            "unknown":      "?",
        },
        "TMPL_TRANSACT_INFO": "{timeStamp} | {tvzCustomerId} | {tvzPlf}",
    },
}

ATTR_TEMPLATES["default"] = ATTR_TEMPLATES["Web"]

# Plf group -> tracker id
GA_TRACKER_ID = {
    "Web":      "UA-132525321-1",
    "SmartTV":  "UA-130113311-1",
    "default":  "UA-125243419-1" # <-- Test counter
}


# From repo: <our gitlab>/smart-tv/smarttv-main/blob/big_dialog_merge/js/platform.js
# Host rule: window.platform.plfCode+'/'+window.platform.plf + '.com'
SMARTTV_UA_MAPPING = (
    # regex - plf - ignore - ignore - plfName
    ("SmartHub",   "smp", "samsung", "Samsung", "Orsay"       ), #  Samsung на нативной платформе
    ("Tizen",      "smp", "tizen",   "Samsung", "Tizen"       ), #  Samsung с операционной системой Tizen
    ("SimpleSmart", "lgn", "lg",      "LG",      "SimpleSmart" ), #  LG платформа потокового вещания
    ("Web0S|WebOS", "lgn", "lg",      "LG",      "WebOS"       ), #  LG на платформе WebOS
    ("NetCast",    "lgn", "lg",      "LG",      "NetCast"     ), #  LG на платформе netCast
    ("LGSmartTV",  "lgn", "lg",      "LG",      "LGLegacy"    ), #  LG на нативной платформе
    ("DTVNetBrowser|Espial|Toshiba", "tsh", "desktop", None,      "Toshiba"     ), # Toshiba
    ("NETTV|Philips", "phn", "desktop", None,      "Philips"     ), #  Philips
    ("Sony|Bravia", "sce", "sony",    "Sony",    "Sony"        ), #  Sony
    ("Viera",      "pnc", "desktop", None,      "Panasonic"   ), #  Panasonic
    ("hisense",    "hcs", "desktop", None,      "Hisense"     ), #  Телевизор компании hisense
    ("spiderMan",  "tzf", "desktop", None,      "TVZavr"      ), #  FlashPlayer
    ("infomir",    "mag", "desktop", "Mag",     "MagTV"       ), #  Приставка mag250
    ("fxm",        "fxm", "desktop", None,      "Foxxum"      ), #  SmartTV от платформы FXM
    ("netrange",   "ntr", "desktop", None,      "Netrange"    ), #  SmartTV от платформы netrange
    ("PCBrowser",  "std", "desktop", None,      "Unknown"     ), #  Неизвестная платформа
)


class MyRedisConn(Redis):
    """
    Here is implementation which specific to this app (model structure: hash of arrays, we are using only one of them: "evt/gaecomm")
    """
    def fetch (self, _ignored):
        trackers = []
        # Data exist in multiple chunks, so join them together by enumeration:
        while True:
            chunk = self.engine.rpop("evt/gaecom")
            if chunk is None:
                break
            rec = chunk.decode()
            memdata = json.loads(rec)
            for event in memdata:
                trackers.append(event)

        return trackers


def env_middleware(handler, arg):
    pass


db_media = "MYSQL_VK"
db_billing = "MYSQL_BILLING"
redis_alias = "REDIS_ADDRESS"


DB_FIXTURE_DICT = DB_FIXTURE_DATA and json.loads(DB_FIXTURE_DATA) or None

@fakedb.fixture(test_mode=FAKE_DB_MODE, fixture=DB_FIXTURE_DATA)
class DBA(DbTaskSet):

    EVENTS = (
        "",
        redis_alias,
        MyRedisConn,
        (
            ("cookies", {}),
            ("headers_info", {
                    "user-agent": ["Mozilla/5.0 (Linux; Tizen 2.2; SAMSUNG SM-Z9005) AppleWebKit/537.3 (KHTML, like Gecko) Version/2.2 like Android 4.1; Mobile Safari/537.3"],
                }
            ),
            ("envelope", fakedb.ChildModel((
                ("trace_message",    1),
                # "do_not_filter_ps": 1,

                ("operationId",    fakedb.FK("TRANSACTION_OPERATION", "operationId")),

                ("originPage",       fakedb.SlugField("/film/{}/")),
                ("pageTitle", "Fake title — tvzavr.ru"),
                ("cids", "UA-97389153-4_cid::1662994990.1554284714|UA-125243419-1_cid::1662994990.1554284714|UA-132525321-1_cid::1662994990.1554284714"),
            )))
        ),
    )

    TRANSACTION_OPERATION = (
        # """select  id, name, mark_type_id, seo_alias from vk.mark where visible=1 and id in ({id__in})""", 
        """
        select 
            transaction_id as transactionId, 
            operation_id as operationId 
            from billing_dev.transaction_operation
            where operation_id in ({id__in})
        """,
        db_billing, 
        MySql,
        (
            ("operationId",        fakedb.Uuid4Field), 
            ("transactionId",      fakedb.FK("TRANSACTION", "transactionId")),
        )
    )

    TRANSACTION = (
        """
        select 
            id as transactionId,
            user_id as tvzCustomerId,
            type as transactionType,
            shop_id as shopId,
            ps_id as paymentSystemId,
            product_id as productId,
            created as timeStamp,
            updated,
            amount,
            remote_amount as remoteAmount,
            status,
            remote_id,
            shop_f1 as tvzPlf,
            foreign_amount as foreignAmount,
            foreign_currency as currency 
            from billing_dev.transaction 
            where id in ({id__in})
        """,
        db_billing, 
        MySql,
        (
            ("transactionId",       fakedb.Uuid4Field), 
            ("tvzCustomerId",       fakedb.Uuid4Field), 
            ("transactionType",     fakedb.EnumField(TRANSACTION_TYPES)),

            ("shopId",              fakedb.ConstField("test-shop")), 

            ("paymentSystemId",     fakedb.EnumField(["tvzpromo", "tvzavrwallet", "FAKE"])),
            # ("productId",           fakedb.EnumField(["2", "25", "43-23173", "19-17864"])),
            ("productId",           fakedb.EnumField(["2", "3", "2-1", "3-2"])),
            ("timeStamp",           "2015-07-07 13:23:22"),
            ("updated",             "0000-00-00 00:00:00"),
            ("amount",              fakedb.EnumField([99, 249, 499])),
            ("remoteAmount",        fakedb.EnumField([1, None])),

            ("status",              fakedb.EnumField(ACK)),

            ("remote_id",           ""),
            ("tvzPlf",              fakedb.EnumField(["tvz", "smp"])),
            ("foreignAmount",       ""),
            ("currency",            "RUB"),
        )
    )

    TARIFF = (
        """
        select id, name as tariffName, vod_system as tariffVod from vk.tariff where id in ({id__in})
        """,
        db_media,
        MySql,
        (
            ("id", fakedb.AutoIncField),
            ("tariffName", fakedb.TemplateField("Tariff {last_name}")),
            ("tariffVod", fakedb.EnumField(["avod", "tvod", "svod", "est"])),
        )
    )

    CLIP = (
        """
        select id, name, meganame, issue as year, type_id, seo_alias from vk.clip where id in ({id__in})
        """, 
        db_media, 
        MySql,
        (
            ("id",          fakedb.AutoIncField), 
            ("name",        fakedb.TemplateField("Film {last_name}")), 
            ("meganame",    "NULL"), 
            ("year",        fakedb.YearField), 
            ("seo_alias",   fakedb.TemplateField("film/{slug}/")), 
            ("type_id",     fakedb.EnumField([1,2,3,5])),
        )
    )

    CLIP_MARK = (
        """select clip_id, mark_id, position from vk.clip_mark where clip_id in ({id__in}) and not mark_id=674 order by position """, 
        db_media, 
        MySql,
        (
            ("clip_id",     fakedb.FK("CLIP", "id")), 
            ("mark_id",     fakedb.EnumField([71, 675, 678])), 
            ("position",    fakedb.EnumField([1,2,3])),  
        )
    )



def detect_smarttv_ua(ua_name):
    """
    # Test
    >>> detect_smarttv_ua("Mozilla/5.0 (SmartHub; SMART-TV; U; Linux/SmartTV) AppleWebKit/531.2+ (KHTML, like Gecko) WebBrowser/1.0 SmartTV Safari/531.2+")
    ('smp', 'Orsay')
    >>> detect_smarttv_ua("Mozilla/5.0 (Linux; Tizen 2.2; SAMSUNG SM-Z9005) AppleWebKit/537.3 (KHTML, like Gecko) Version/2.2 like Android 4.1; Mobile Safari/537.3")
    ('smp', 'Tizen')
    >>> detect_smarttv_ua("Mozilla/5.0 (Unknown; Linux armv7l) AppleWebKit/537.1+ (KHTML, like Gecko)Safari/537.1+ LG Browser/6.00.00(+mouse+3D+SCREEN+TUNER; LGE; model_name; 00.00.00;0x00000001; LCD_SS1A); LG SimpleSmart.TV-2016 /00.00.00 (LG, model_name, wired)")
    ('lgn', 'SimpleSmart')
    >>> detect_smarttv_ua("Mozilla/5.0 (DirectFB; U; Linux 35230; en) AppleWebKit/531.2+ (KHTML, like Gecko) Safari/531.2+ LG Browser/4.1.4(+3D+SCREEN+TUNER; LGE; 42LW5700-SA; 04.02.28; 0x00000001;); LG NetCast.TV-2011")
    ('lgn', 'NetCast')
    >>> detect_smarttv_ua("Mozilla/5.0 (LuneOS, like webOS/3.0.5; Tablet) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.9.2 Chrome/56.0.2924.103 Safari/537.36")
    ('lgn', 'WebOS')
    >>> detect_smarttv_ua("Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.2.1 Chr0me/38.0.2125.122 Safari/537.36 LG Browser/8.00.00(LGE; STB-5500-UA; 07.05.11; 1; DTV_H16A); webOS.TV-2016; LG NetCast.TV-2013 Compatible (LGE, STB-5500-UA, wireless)")
    ('lgn', 'WebOS')
    >>> detect_smarttv_ua("Opera/9.80 (Linux armv7l; HbbTV/1.2.1 (; Philips; 40HFL5010T12; ; PHILIPSTV; CE-HTML/1.0 NETTV/4.4.1 SmartTvA/3.0.0 Firmware/004.002.036.135 (PhilipsTV, 3.1.1,)en) ) Presto/2.12.407 Version/12.50")
    ('phn', 'Philips')
    >>> detect_smarttv_ua("Mozilla/5.0 (Linux; U; Linux; ja-jp; DTV; TSBNetTV/T3E01CD.0203.DDD) AppleWebKit/536(KHTML, like Gecko) NX/3.0 (DTV; HTML; R1.0;) DTVNetBrowser/2.2 (000039;T3E01CD;0203;DDD) InettvBrowser/2.2 (000039;T3E01CD;0203;DDD)")
    ('tsh', 'Toshiba')
    """
    for (pattern, plf, _1, _2, plf_name) in SMARTTV_UA_MAPPING:
        if re.search(pattern, ua_name, flags=re.IGNORECASE) is not None:
            return (plf, plf_name)
    return (None, None)


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

    # redis_db =  ConnectionPool.select(Redis, "REDIS_ADDRESS") 

    # trackers = []
    # # Data exist in multiple chunks, so join them together by enumeration:
    # while True:
    #     chunk = redis_db.engine.rpop("evt/gaecom")
    #     if chunk is None:
    #         break
    #     rec = chunk.decode()
    #     memdata = json.loads(rec)
    #     for event in memdata:
    #         trackers.append(event)
    trackers = DBA.EVENTS.get_records()
    print("REDIS:", json.dumps(trackers))
    return trackers

def fake_trackers(ctx):
    """
    Fake test mock
    """
    _fake_operations= [
        # "0071c064-5ace-11e9-84b2-002590ea2218", # 7, single
        # "006103be-56a0-11e9-b335-002590ea2218", # 3, 8
        # "003b2362-52a7-11e9-88a4-002590ea4448", # 3, 8
        # # Smart -tv:
        # "7bc0b56a-6512-11e9-942c-0cc47a172970",
        "9e5a6aee-6512-11e9-a9c1-0cc47a172970",

        "001dd578-6c42-11e9-a63b-002590ea2218",

        # # Direct purchase from wallet (should be filtered):
        # "00736262-7012-11e9-8ee3-002590ea2218",        
        # "0053b554-6c28-11e9-9b5b-002590ea2218",

        # cloudpayments -> wallet -> purchase
        "bee5effc-75cc-11e9-b05b-002590ea2218",
        # Trial purchase:
        "5f5a0294-7612-11e9-b936-0cc47a172970",
        # Auto deposit (recurrent)
        "bd933bd8-418c-11e9-a0c7-0cc47a172970",
        # Conflict transaction particular test case
        "df2d3968-765e-11e9-8eea-0cc47a172970",
        # Trial subscription for 1 rub:
        "7c05b48c-7c99-11e9-a969-002590ea2218",


    ]

    trackers = [
        {
            "envelope": {
                # Mandatory: switch ON test flags:
                # SANDBOX_MODE = os.getenv('SANDBOX_MODE', False)
                # LOG_ONLY = False
                # DO_NOT_FILTER_PS = False
                "use_test_counter": 1,
                "trace_message":    1,
                # "do_not_filter_ps": 1,

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
                "user-agent": ["Mozilla/5.0 (Linux; Tizen 2.2; SAMSUNG SM-Z9005) AppleWebKit/537.3 (KHTML, like Gecko) Version/2.2 like Android 4.1; Mobile Safari/537.3"],
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
        """
        Note: SmartTV clients return raw value of CID while web clients returns "dict" of CIDs where keys formatted like "<UA-counter-id>_cid"
        """
        delimiter = "_cid::"
        if text.find(delimiter) < 0:
            if len(text) > 0:
                return text # text contains CID value
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
        
        sandbox_mode =  SANDBOX_MODE or "use_test_counter" in envelope
        log_only =      LOG_ONLY or "trace_message" in envelope
        do_not_filter_ps = DO_NOT_FILTER_PS or "do_not_filter_ps" in envelope

        gaTrackerId = "UA-125243419-1"
        if sandbox_mode:
            gaTrackerId = "UA-125243419-1"
        # cookies = item["cookies"]
        metadata = {
            "operationId":    envelope["operationId"], # <- from FrontEnd!!!

            # "gaTrackerId": parsed["envelope"]["gaTrackerId"], # <- from FrontEnd?
            # "gaTrackerId":                  gaTrackerId,
            # "gaClientId":                   extract_cid(envelope["cids"], gaTrackerId), # <- from FrontEnd
            "gaRawCids":                    envelope["cids"],
            # "tvzCustomerId":              envelope["tvzCustomerId"], # <- from DB
            "pageTitle":                    envelope.get("pageTitle"),
            "originResourcePath":           envelope.get("originPage"),
            "userAgent":                    headers["user-agent"][0],
            "testMode_logOnly":             log_only,
            "testMode_showAllPaymentSystems": do_not_filter_ps,
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

    # transactions_string = ",".join(["\"{}\"".format(id) for id in pushed_operations_ids])

    # log.debug("fetch_db_transaction_operation INPUT: {}".format(pushed_transactions))

    # Get operations as groups of transactions:

    # db = ConnectionPool.select(MySql,'MYSQL_BILLING')

    # sql ="""
    # select 
    #     transaction_id as transactionId, 
    #     operation_id as operationId, 
    #     transaction_type as transactionType
    #     from billing_dev.transaction_operation
    #     where operation_id in ({})
    # """.format(transactions_string)

    # transactions = db.get_records(sql)

    transactions = DBA.TRANSACTION_OPERATION.get_records(id__in=pushed_operations_ids)

    # log.debug('Operations ===================> \n{}\n'.format(transactions))

    # If some transactions not found in "transaction_operation" - pass them from  pushed_transactions with "simple" flag

    # decoded = _.Chain(pushed_transactions).map(lambda et: )

    transactions_ids = set(_.pluck(transactions, 'transactionId'))

    # Spread metadata from event to all transactions indexed by operation:
    mapped = \
        _.chain(
                transactions
            ).filter(
                lambda t: t["operationId"] in pushed_operations_ids
            ).map(lambda t: \
                _.extend({}, t,
                    _.chain(
                            pushed_operations
                        ).find_where(
                            {"operationId": t["operationId"]}
                        ).pick(
                            # "gaTrackerId",
                            # "gaClientId", # <- from FrontEnd,
                            "gaRawCids",
                            "pageTitle",
                            "originResourcePath",
                            "userAgent",
                            "testMode_logOnly",
                            "testMode_showAllPaymentSystems",
                        ).value
                )
        ).value
    
    if not transactions_ids:
        log.error("Unresolved transactions! ->>>  {}".format(ctx))

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

    if not transactions_ids:
        return None

    mapped = annotated["mapped"]

    # transactions = heap.pull("search_transaction_operation")
    transactions_string = ",".join(["\"{}\"".format(t) for t in transactions_ids])

    # db = ConnectionPool.select(MySql,'MYSQL_BILLING')

    # sql = """select 
    #         id as transactionId,
    #         user_id as tvzCustomerId,
    #         type as transactionType,
    #         shop_id as shopId,
    #         ps_id as paymentSystemId,
    #         product_id as productId,
    #         created as timeStamp,
    #         updated,
    #         amount,
    #         remote_amount as remoteAmount,
    #         status,
    #         remote_id,
    #         shop_f1 as tvzPlf,
    #         foreign_amount as foreignAmount,
    #         foreign_currency as currency 
    #         from billing_dev.transaction 
    #         where id in ({})""".format(transactions_string)
    
    # # log.debug('SQL ===================> \n{}\n'.format(sql))

    try:
        # records = db.get_records(sql)
        records = DBA.TRANSACTION.get_records(id__in=list(transactions_ids))
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
                            "remoteAmount",
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
    
    def decode_plf_name():
        # Resolve plf
        auto_plf, auto_plf_name = detect_smarttv_ua(headers.get("user-agent"))
        plf = envelope.get("plf")


    if not ctx: 
        return None

    operations = ctx

    notifications = []

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
                t["status"] in ACK and t["testMode_showAllPaymentSystems"] or not t["paymentSystemId"] in BANNED_PS_SYSTEMS
        ).value

        # Select only "real" amount if any (in case of trial subscriptions real amount is less than declared "amount"):
        transactions = _.map(
            transactions, 
            lambda t: _.extend({}, t, {"amount": t["remoteAmount"] or t["amount"]})
        )

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
        ).map(lambda t: _.pick(t, "productId", "amount", "remoteAmount", "currency", "status", "shopId", "transactionType")).value

        passthrought = _.chain(transactions).filter(lambda t: t["transactionType"] == OVERDRAFT).map(lambda t: _.pick(t, "productId", "paymentSystemId", "amount", "remoteAmount", "currency", "status", "shopId", "transactionType")).value

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

        # Filter test tariffs:
        transactions = _.filter(transactions, lambda t: t not in QA_TARIFFS)

        # Drop unresolved operations where no transactions with ACK status:
        if len(transactions) == 0:
            log.info("Refused transactions??? Dropping -> {}".format(rec["transactions"]))
            continue
        
        # Drop direct purchases from wallet (probably mixed with promo-money)
        # Use: paymentSystemId, transactionType
        if _.chain(transactions).filter(
                lambda t: t["paymentSystemId"] != "tvzpromo"
            ).size().value == 1 \
            and \
            _.chain(transactions).filter(
                lambda t: t["transactionType"] == WITHDRAWAL and t["paymentSystemId"] == "tvzavrwallet"
            ).size().value == 1:

            log.info("Purchase from wallet. Dropping operation {} -> {}".format(operationId, transactions))
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
            "operationId",
            "tvzPlf",
            "gaTrackerId",
            # "gaClientId",
            "gaRawCids",
            "tvzCustomerId",
            "originResourcePath",
            "pageTitle",
            "userAgent",
            "cookies",
            "paymentSystemId",
            "timeStamp",
            # "amount",
            "currency",
            "testMode_logOnly",
            "testMode_showAllPaymentSystems",
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

        # ids = ",".join(["\"{}\"".format(id) for id in clipsIds])
        
        # db = ConnectionPool.select(MySql, 'MYSQL_VK')
        
        # sql ="""
        #     select id, name, meganame, issue as year, type_id, seo_alias from vk.clip where id in ({})
        #     """.format(ids)
        # clip_info = db.get_records(sql)

        clip_info = DBA.CLIP.get_records(id__in=clipsIds)

        # sql ="""
        #     select clip_id, mark_id from vk.clip_mark where clip_id in ({})
        #     """.format(ids)
        # clip_marks = db.get_records(sql)


        clip_marks = DBA.CLIP_MARK.get_records(id__in=clipsIds)


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
                clipSeoAlias = None
            else:
                clipName = get_title(clip)
                clipCategory = get_category(clip)
                clipSeoAlias = clip["seo_alias"]

            _.extend(ntf, {
                "clipName": clipName,
                "clipCategory": clipCategory,
                "clipSeoAlias": clipSeoAlias,
            })

    if tariffsIds:

        # ids = ",".join(["\"{}\"".format(id) for id in tariffsIds])
        
        # db = ConnectionPool.select(MySql, 'MYSQL_VK')
        
        # sql ="""
        #     select id, name as tariffName, vod_system as tariffVod from vk.tariff where id in ({})
        #     """.format(ids)
        # tariff_info = db.get_records(sql)

        tariff_info = DBA.TARIFF.get_records(id__in=tariffsIds)

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
    def extract_cid(text, gaTrackerId):
        """
        Note: SmartTV clients return raw value of CID while web clients returns "dict" of CIDs where keys formatted like "<UA-counter-id>_cid"
        """
        delimiter = "_cid::"
        if text.find(delimiter) < 0:
            if len(text) > 0:
                return text # text contains CID value
            return "NOT_FOUND"
        pairs = dict(_.map(text.split("|"), lambda p: p.split(delimiter)))
        # log.debug("PAIRS::: {}".format(pairs))
        return pairs.get(gaTrackerId, "ERROR")

    # trackers = heap.pull("decode_trackers")
    if not ctx:
        return None

    notifications = ctx["notifications"]
    operations = ctx["operations"]

    messages = []
    
    for t in notifications:

        # locationInfo = "" # location.pathname + location.hash + location.search
        # title = "<title>"
        amount = t["amount"]
        promo_amount = t["promoAmount"]
        amount -= promo_amount

        # Ignore 100% promo
        if amount == 0:
            continue
        
        # Detect platform details
        plf = t["tvzPlf"]
        plf_group = PLF_GROUP.get(plf, "default")
        templates = ATTR_TEMPLATES.get(plf_group, None)
        if templates is None:
            templates = ATTR_TEMPLATES["default"]

        if plf_group in ("SmartTV", "STB"):
            auto_plf, plf_name = detect_smarttv_ua(t["userAgent"])
            t = _.extend({}, t, {"tvzStvPlfName": plf_name})
            log.debug("PLF is not web: {},{}".format(auto_plf, plf_name))
            
        log.debug("PLF DETECTION READY: {}".format(t))

        gaTrackerId = GA_TRACKER_ID.get(plf_group, None)
        if gaTrackerId is None:
            gaTrackerId = GA_TRACKER_ID["default"]

        tariffId = t.get("tariffId", "id")
        tariffName = t.get("tariffName")
        tariffVod = t.get("tariffVod", "vod?")

        isSubscription = tariffVod.lower() == "svod"

        if isSubscription:
            # Подписка
            subjectId = tariffId
            subjectName = tariffName
            extCat = "Подписка"
            ea = "Подписка"
            operation_kind = "subscription"
        elif t["clipId"]:
            # Фильм
            subjectId = t["clipId"]
            subjectName = t["clipName"]
            extCat = t["clipCategory"]
            ea = "Фильм"
            operation_kind = "clip"
        elif t["wallet"] is not None:
            # Кошелек
            subjectId = 0
            subjectName = "Пополнение"
            extCat = "Пополнение"
            ea = "Пополнение"
            operation_kind = "wallet"
        else:
            # "Непойми что" - блин это похоже пополнение?
            subjectId = ""
            subjectName = "?"
            extCat = "?"
            ea = "Invalid data in billing!"
            operation_kind = "unknown"
        
        if SANDBOX_MODE:
            subjectName = "[{}] {}".format(t["tvzPlf"], subjectName)
        


        ga_event_data = {
            "v":    1,
            "t":    "event",
            "tid":  gaTrackerId,
            "cid":  extract_cid(t["gaRawCids"], gaTrackerId),
            # "cid":  t["gaClientId"],
            "uid":  t["tvzCustomerId"],
            "dh":   templates["TMPL_HOST"].format(**t), # "host", e.f.: tvzavr.ru
            "dp":   templates["TMPL_URI"][operation_kind].format(**t), # "web page"
            "dt":   templates["TMPL_TITLE"].format(**t), # From DB????
            "pa":   "purchase",
            # "ti":   t["transactionId"], # UUID + dd.mm.YY hh:mm:ss пользователя + дата
            "ti":   templates["TMPL_TRANSACT_INFO"].format(**t),
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
            "__trace_mode__": t["testMode_logOnly"]
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
        chunk_no = cnt  #  20
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

# Export scheduled interval
interval_secs = 60


# ###############################
# Legend
# ###############################
import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(settings)
# ###############################


# Export main runner
def run(ctx):
    # pass
    source = fetch_trackers
    dest = send_ga_ecomm_event
    return run_with(source, dest)

def test(ctx):
    import pprint
    
    def dest(ctx):
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(ctx)
        return ctx
        
    source = fake_trackers
    # source = fetch_trackers

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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
