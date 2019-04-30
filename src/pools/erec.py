# -*- coding: utf-8 -*-
"""
Updates catalog in easyrec
"""
import os, sys

import logging
logging.basicConfig(
    # filename='example.log', 
    format='erec: %(asctime)s %(levelname)s:%(message)s', 
    level=logging.DEBUG)
log = logging.getLogger(__name__)

import re
import json
import csv
import itertools

import requests
import urllib

from enum import Enum, IntEnum

from hostapi.io import Heap, JsonStore, NullStore, Redis, Alchemy, MySql, ConnectionPool, DbTaskSet, json_stream

from hostapi.chains import Chain 

from hostapi.underscore import Underscore as _

from ci import fakedb

USE_FAKE_DB = os.getenv('FAKE_DB', False)

buffer_path = os.getenv('EVENTMACHINE_BUFFER', './../buffer')
# engine = BinStore(buffer_path)
engine = NullStore()
heap = Heap(engine)
jsonfile = JsonStore(buffer_path)


class CLIP_TYPES(Enum):
    Single = 1
    Set = 2
    SetElement = 3
    Season = 5
    
    def __str__(self):
        return '%s' % self.value

CLIP_SELECTED_TYPES = (
    CLIP_TYPES.Single.value,
    CLIP_TYPES.Set.value,
    # CLIP_TYPES.SetElement.value,
    CLIP_TYPES.Season.value,
)

class MARK_TYPES(Enum):
    CATEGORIES = 1
    TAGS = 2

    ACTORS = 5
    DIRECTORS = 6
    YEARS = 7
    COUNTRIES = 9
    GENRES = 14

    AWARDS = 15
    BADGE = 20
    CAMPAIGN = 17
    CHANNELS = 3
    COMPOSERS = 10
    DELETED = 12
    MOOD = 19
    PAYMENTS = 16
    PROMOPAGE = 18
    RECOMMENDATIONS = 4
    RESTRICTIONS = 11
    STUDIO = 8
    YEAR_INTERVALS = 13

    def __str__(self):
        return '%s' % self.value


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)

MARK_AGE_FROM_6 = 19018
MARK_AGE_FROM_12 = 18576
MARK_AGE_FROM_14 = 20380
MARK_AGE_FROM_16 = 9598
MARK_AGE_FROM_18 = 37064

MARKS_AGES = (
    MARK_AGE_FROM_6,
    MARK_AGE_FROM_12,
    MARK_AGE_FROM_14,
    MARK_AGE_FROM_16,
    MARK_AGE_FROM_18,
)

db_media = "MYSQL_VK"
# db_media = "MYSQL_VK_SECONDARY"
# db_media_secondary = "MYSQL_VK_SECONDARY"
db_easyrec = "MYSQL_EASYREC"

@fakedb.fixture(USE_FAKE_DB)
class DBA(DbTaskSet):
    # OPERATOR = None # Set to MySqlOperator or whatelse...
    """
    Hint: we can use sql with parameters like:
    "SELECT * FROM table_name where id = {}"
    and call:
    DBA.CLIP_TEST.get_records(id="54")
    """
    # LEGAL_TERRITORY_VOD = (
    #     """select clip_id, AVOD, SVOD, TVOD, EST from vk.clip_legal_territory_vod order by clip_id desc""", 
    #     db_media, 
    #     MySql,
    #     )
    # REGION_DEPENDENCE = (
    #     """select parent_region_id, child_region_id from vk.region_dependence""", 
    #     db_media, 
    #     MySql,
    #     )
    # TARIFF_PLATFORM = (
    #     """select tariff_id, platform_id from vk.tariff_platform where platform_id in (1)""", 
    #     db_media, 
    #     MySql,
    #     )
    # TARIFF = (
    #     """select id, name, price, currency_iso, duration, vod_system from vk.tariff where active=1 and hidden=0""", 
    #     db_media, 
    #     MySql,
    #     )
    # TARIFF_REGION = (
    #     """select tariff_id, region_id from vk.tariff_region""", 
    #     db_media, 
    #     MySql,
    #     )
    # CLIP_TARIFF = (
    #     """select tariff_id, clip_id, granted_clip_id, expired from vk.clip_tariff where expired=0""", 
    #     db_media, 
    #     MySql,
    #     )

    # CLIP_TEST = (
    #     """select id, name, meganame, issue, seo_alias, duration, description, type_id from vk.clip where id in ({id__in}) limit 10""", 
    #     db_media, 
    #     MySql,
    #     )
    # REGION = (
    #     """select id, name, description, active, currency_iso, territory_id, country_id from vk.region where active=1""", 
    #     db_media, 
    #     MySql,
    #     )

    # Cleaned:
    MARK = (
        """select  id, name, mark_type_id, seo_alias from vk.mark where visible=1 and id in ({id__in})""", 
        db_media, 
        MySql,
        (
            ("id",          fakedb.AutoIncField), 
            ("name",        fakedb.NameField), 
            ("mark_type_id", fakedb.EnumField(MARK_TYPES)), 
            ("seo_alias",   fakedb.SlugField("{}/")),
        )
    )
    CLIP_MARK = (
        """select clip_id, mark_id, position from vk.clip_mark where clip_id in ({id__in}) and not mark_id=674 order by position """, 
        db_media, 
        MySql,
        (
            ("clip_id",     fakedb.FK("CLIP", "id")), 
            ("mark_id",     fakedb.FK("MARK", "id")), 
            ("position",    fakedb.EnumField([1,2,3])),         
        )
    )

    CLIP = (
        """
        select id, name, meganame, issue, seo_alias, type_id from vk.clip 
        where type_id in ({types}) and 
        visible=1 and id>={id__ge} order by id limit {limit}
        """, 
        db_media, 
        MySql,
        (
            ("id",          fakedb.AutoIncField), 
            ("name",        fakedb.TemplateField("Film {last_name}")), 
            ("meganame",    "NULL"), 
            ("issue",       fakedb.YearField), 
            ("seo_alias",   fakedb.TemplateField("film/{slug}/")), 
            ("type_id",     fakedb.EnumField(CLIP_TYPES)),
        )
    )
    
    CLIP_LAST_ID = (
        """ 
        select max(id) as lastId from vk.clip
        """,
        db_media, 
        MySql,
        (
            ("lastId", 1),
        )
    )


    SYN_STATE_GET = (
        """
        select 
            model_name as modelName, 
            key_name as keyName, 
            key_type as keyType, 
            last_known_key as lastKnownKey, 
            last_updated_key as lastUpdatedKey,
            active, 
            changedate 
        from easyrec.elcamino_sync
        where model_name = '{modelName}'
        """,
        db_easyrec, 
        MySql,
        (
            ("modelName", "item"),
            ("keyName", "itemid"),
            ("keyType", "int"),
            ("lastKnownKey", 0),
            ("lastUpdatedKey", 0),
            ("active", 1),
            ("changedate", "0000-00-00"),
        )
    )

    SYN_STATE_SET = (
        """
        UPDATE easyrec.elcamino_sync SET 
            last_known_key = '{lastKnownKey}', 
            last_updated_key = '{lastUpdatedKey}'  
        WHERE model_name = '{modelName}'
        """,
        db_easyrec, 
        MySql,
        ()
    )
    
    EASYREC_ITEM_INSERT_MANY = (
        """
        INSERT INTO easyrec.item
            (tenantId, itemid, itemtype, description, profileData, url, imageurl)
        VALUES
            {args}
        ON DUPLICATE KEY UPDATE description=VALUES(description), profileData=VALUES(profileData), url=VALUES(url), imageurl=VALUES(imageurl)            
        """,
        db_easyrec, 
        MySql,
        ()
    )

    EASYREC_ITEM_MAPPING_GET = (
        """
        select stringId from easyrec.idmapping
        """,
        db_easyrec, 
        MySql,
        ()
    )

    EASYREC_ITEM_MAPPING_SET = (
        """
        INSERT INTO easyrec.idmapping
            (stringId)
        VALUES
            {args}
        ON DUPLICATE KEY UPDATE stringId=VALUES(stringId)            
        """,
        db_easyrec, 
        MySql,
        ()
    )

    
#     INSERT_EASYREC_ITEM = (
#         """
#         INSERT INTO table (id,Col1,Col2) VALUES (1,1,1),(2,2,3),(3,9,3),(4,10,12)
# ON DUPLICATE KEY UPDATE Col1=VALUES(Col1),Col2=VALUES(Col2);
#         """
#         db_easyrec, MySql)
        
#     UPDATE_EASYREC_ITEM = (
#         """
#         """
#         db_easyrec, MySql)


# TO-DO: make more concise

DEFAULTS = {
    "chunkSize": 100
}
TENANT_ID = 2


@heap.store
def init_env(ctx):
    return _.extend({}, DEFAULTS, ctx)

def check_tvz_catalog_length(ctx):
    result = DBA.CLIP_LAST_ID.get_records()
    return {
        "sourceClipLastId": int(result[0]["lastId"])
    }


# def fetch_origin_clips(ctx):
#     result = DBA.CLIP.get_records(id__ge=100)
#     print(result)
#     return result

# def start(ctx):
#     ctx = ctx or {}
#     default = {

#     }

def fetch_update_status(ctx):
    """
    """
    syn_state = DBA.SYN_STATE_GET.get_records(
        modelName='item'
    )
    def typecast(value, type):
        if type == "int":
            return int(value)
        if type == "bool":
            return bool(value)
        return value

    item_syn_state = syn_state[0]
    key_type = item_syn_state["keyType"]
    return _.extend({}, ctx, {
        "updateStatus": {
            "modelName":    item_syn_state["modelName"], 
            "keyName":      item_syn_state["keyName"], 
            "keyType":      key_type, 
            "lastKnownKey":  typecast(item_syn_state["lastKnownKey"], key_type), 
            "lastUpdatedKey": typecast(item_syn_state["lastUpdatedKey"], key_type),
        }
    })


def fetch_origin_clips(ctx):
    """ 
    CLIP 
    """
    to_id = ctx["sourceClipLastId"]    
    from_id = ctx["updateStatus"]["lastUpdatedKey"]
    chunk_size = ctx["chunkSize"]


    if from_id < to_id:
        clips = DBA.CLIP.get_records(
            id__ge=from_id,
            types=CLIP_SELECTED_TYPES,
            limit=chunk_size
        )

        id__in = _.chain(clips).pluck("id").map(int).value

        result = _.extend({}, ctx, {
            "clip_id__in": id__in,
            "clips": clips,
        })

        # print(result)
        return result
    else:
        return None

def fetch_origin_clip_marks(ctx):
    """ CLIP_MARK """
    clip_ids = list(ctx["clip_id__in"])
    clip_marks = DBA.CLIP_MARK.get_records(id__in=clip_ids)
    id__in = _.pluck(clip_marks, "mark_id")
    # print(clip_marks)
    return _.extend({}, ctx, {
        "mark_id__in": id__in,
        "clip_marks": clip_marks,
    })

def fetch_origin_marks(ctx):
    """ MARK """
    mark_id__in = list(ctx["mark_id__in"])
    marks = DBA.MARK.get_records(id__in=mark_id__in)
    # print(marks)
    return _.extend({}, ctx, {
        "marks": marks
    })

def reflect_mark_to_clip(ctx):
    """
    """
    clip_marks = ctx["clip_marks"]
    marks = ctx["marks"]
    reflection = _.map(clip_marks, 
        lambda cm:\
            _.extend({}, cm, _.find_where(marks, {"id": cm["mark_id"]}))
    )
    return _.extend({}, ctx, {
        "marks_lookup": reflection
    })

def annotate_clip_with_mark(ctx):
    def select_marks(marks_gr, clip_id, mark_type, pick_field):
        marks_for_clip = marks_gr.get(clip_id, [])
        return _.chain(marks_for_clip).filter(
            lambda m: \
                m.get("mark_type_id") == mark_type.value
        ).sort_by(
            lambda m:\
                m.get("position") or 999
        ).pluck(pick_field).value
    
    def map_age(memo, mark_id):
        value = {
            MARK_AGE_FROM_18: 18,
            MARK_AGE_FROM_16: 16,
            MARK_AGE_FROM_14: 14,
            MARK_AGE_FROM_12: 12,
            MARK_AGE_FROM_6: 6,
        }[mark_id]        
        return max(memo, value)


    clips = list(ctx["clips"])
    marks = list(ctx["marks_lookup"])
    marks_gr = _.group_by(marks, "clip_id")
    pick_field = "mark_id"
    annotated = _.chain(clips).map(lambda c: \
        _.extend({}, c, {
            "ages": 
                _.chain(
                        marks_gr.get(c["id"], [])
                    ).pluck(
                        "mark_id"
                    ).filter(
                        lambda id: id in MARKS_AGES
                    ).reduce(
                        map_age, 0
                    ).value,
            "categories": 
                select_marks(marks_gr, c["id"], MARK_TYPES.CATEGORIES, pick_field),
            "genres": 
                select_marks(marks_gr, c["id"], MARK_TYPES.GENRES, pick_field),
            "moods": 
                select_marks(marks_gr, c["id"], MARK_TYPES.MOOD, pick_field),
            "tags": 
                select_marks(marks_gr, c["id"], MARK_TYPES.TAGS, pick_field),
            "actors": 
                select_marks(marks_gr, c["id"], MARK_TYPES.ACTORS, pick_field),
            "directors": 
                select_marks(marks_gr, c["id"], MARK_TYPES.DIRECTORS, pick_field),
            "studio": 
                select_marks(marks_gr, c["id"], MARK_TYPES.STUDIO, pick_field),
            "countries": 
                select_marks(marks_gr, c["id"], MARK_TYPES.COUNTRIES, pick_field),
            "composers": 
                select_marks(marks_gr, c["id"], MARK_TYPES.COMPOSERS, pick_field),
            "year_intervals": 
                select_marks(marks_gr, c["id"], MARK_TYPES.YEAR_INTERVALS, pick_field),
        })).value

    # print(marks)
    # return _.extend({}, ctx, {"marks": marks})
    return _.extend({}, ctx, {
       "annotated": annotated
    }) 

# print (check_tvz_catalog_length())

def to_easyrec_item(ctx):
    #   `id` int(11) NOT NULL AUTO_INCREMENT,
    #   `tenantId` int(11) NOT NULL,
    #   `itemid` varchar(250) NOT NULL DEFAULT '',
    #   `itemtype` varchar(20) NOT NULL DEFAULT '',
    #   `description` varchar(500) DEFAULT NULL,
    #   `profileData` text,
    #   `url` varchar(500) DEFAULT NULL,
    #   `imageurl` varchar(500) DEFAULT NULL,
    #   `active` tinyint(1) DEFAULT '1',
    #   `creationdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #   `changedate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
    if not ctx:
        return None
    
    annotated = ctx["annotated"]

    def encode_name(clip):
        name = clip["name"] or clip["meganame"]
        return urllib.parse.quote(name)
    
    easyrec_items = _.chain(annotated).map(
        lambda c: {
            "id": "",
            "tenantId": TENANT_ID,
            "itemId": c["id"],
            "itemtype": "ITEM",
            "description": encode_name(c),
            "profileData": json.dumps(
                    _.pick(c, "type_id", "ages", "categories", "genres", "moods", "tags", "actors", "directors", "studio", "composers", "year_intervals"),
                    cls=EnumEncoder,
                ),
            "url": "//www.tvzavr.ru/film/{seo_alias}/".format(**c),
            "imageurl": "//www.tvzavr.ru/common/tvzstatic/cache/300x450/{id}.jpg".format(**c),
            "active": 1
        }
    ).value

    return _.extend({}, ctx, {
        "easyrec_items": easyrec_items
    })

def update_easyrec_item(ctx):
    if ctx is None:
        return None
    
    def smart_quote(v):
        if isinstance(v, str):
            return "\"{}\"".format(v)
        return str(v)
    
    data = ctx["easyrec_items"]
    buff = []
    for rec in data:
        # Order is mandatory!:
        row = "({tenantId}, '{itemId}', '{itemtype}', '{description}', '{profileData}', '{url}', '{imageurl}')".format(**rec)
        buff.append(row)
    args = ",".join(buff)
    num_rows = DBA.EASYREC_ITEM_INSERT_MANY.execute(args=args)

    log.info("easyrec catalog: {} items updated".format(num_rows))
    # update_args = _.reduce(data, )
    return _.extend({}, ctx, {
        "items_updated": num_rows
    })

def reflect_last_updated(ctx):
    if ctx is None:
        return None

    clip_ids = ctx["clip_id__in"]
    lastUpdatedKey = max(clip_ids)
    lastKnownKey = ctx["sourceClipLastId"]
    modelName = "item"
    DBA.SYN_STATE_SET.execute(
        lastKnownKey=lastKnownKey, 
        lastUpdatedKey=lastUpdatedKey, 
        modelName=modelName)
    return ctx

def update_easyrec_idmapping(ctx):
    """
    idmapping is a table with simple registry of string ids
    """
    if ctx is None:
        return None
    
    records = DBA.EASYREC_ITEM_MAPPING_GET.get_records()
    # Note - values are strings!!!
    known_ids = _.pluck(records, "stringId")
    # Convert to strings:
    updated_ids = _.map(ctx["clip_id__in"], str)
    ids_to_insert = list(
        set(updated_ids).difference(set(known_ids))
    )
    if ids_to_insert:
        args = ",".join(_.map(ids_to_insert, "('{}')".format))
        DBA.EASYREC_ITEM_MAPPING_SET.execute(args=args)

    return ctx


def to_csv(ctx):
    if not ctx:
        return None

    with open('mycsvfile.csv','w') as f:
        fieldnames = ctx[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # writer.writeheader()
        for r in ctx:
            writer.writerow(r)
    
    return ctx

def run_with(source, dest):
    return Chain(
            source
        ).then(
            init_env
        ).merge(
            check_tvz_catalog_length,
            fetch_update_status,
        ).then(
        #     lambda r: log.debug(" merged result: {}".format(r)) and r
        # ).then(
            fetch_origin_clips
        ).then(
            fetch_origin_clip_marks
        ).then(
            fetch_origin_marks
        ).then(
            reflect_mark_to_clip
        ).then(
            annotate_clip_with_mark
        ).then(
            to_easyrec_item
        ).then(
            # to_csv
            update_easyrec_item
        # )
        # .then(
        #     annotate_subject
        ).then(
            reflect_last_updated
        ).then(
            update_easyrec_idmapping
        ).then(
            dest
        )

interval_secs = 60

def run(ctx):
    run_with(ctx, lambda ctx: ctx)

def runall(ctx):
    run_with(
        ctx,
        json_stream('./result10.json')
        # to_csv
    )