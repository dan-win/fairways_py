# -*- coding: utf-8 -*-
"""
Updates catalog in easyrec
"""
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

from enum import Enum

from hostapi.io import Heap, JsonStore, NullStore, Redis, Alchemy, MySql, ConnectionPool, DbTaskSet, json_stream

from hostapi.chains import Chain 

from hostapi.underscore import Underscore as _

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
    CLIP_TYPES.Single,
    CLIP_TYPES.Set,
    # CLIP_TYPES.SetElement,
    CLIP_TYPES.Season,
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

db_media = "MYSQL_VK"
# db_media = "MYSQL_VK"

class DBA(DbTaskSet):
    # OPERATOR = None # Set to MySqlOperator or whatelse...
    """
    Hint: we can use sql with parameters like:
    "SELECT * FROM table_name where id = {}"
    and call:
    DBA.CLIP_TEST.get_records(id="54")
    """
    LEGAL_TERRITORY_VOD = (
        """select clip_id, AVOD, SVOD, TVOD, EST from vk.clip_legal_territory_vod order by clip_id desc""", 
        db_media, MySql)
    REGION_DEPENDENCE = (
        """select parent_region_id, child_region_id from vk.region_dependence""", 
        db_media, MySql)
    TARIFF_PLATFORM = (
        """select tariff_id, platform_id from vk.tariff_platform where platform_id in (1)""", 
        db_media, MySql)
    TARIFF = (
        """select id, name, price, currency_iso, duration, vod_system from vk.tariff where active=1 and hidden=0""", 
        db_media, MySql)
    TARIFF_REGION = (
        """select tariff_id, region_id from vk.tariff_region""", 
        db_media, MySql)
    CLIP_TARIFF = (
        """select tariff_id, clip_id, granted_clip_id, expired from vk.clip_tariff where expired=0""", 
        db_media, MySql)
    MARK = (
        """select  id, name, mark_type_id, seo_alias from vk.mark where visible=1 and id in ({id__in})""", 
        db_media, MySql) # Выкинуты мусорные марки
    CLIP_MARK = (
        """select clip_id, mark_id, position from vk.clip_mark where clip_id in ({id__in}) order by position """, 
        db_media, MySql)
    CLIP = (
        """
        select id, name, meganame, issue, seo_alias, type_id from vk.clip 
        where type_id in ({types}) and 
        visible=1 and id>={id__ge} limit 10
        """, 
        db_media, MySql)
    CLIP_TEST = (
        """select id, name, meganame, issue, seo_alias, duration, description, type_id from vk.clip where id in ({id__in}) limit 10""", 
        db_media, MySql)
    REGION = (
        """select id, name, description, active, currency_iso, territory_id, country_id from vk.region where active=1""", 
        db_media, MySql)

@heap.store
def check_er_catalog_state(ctx):
    pass

def check_tvz_catalog_state(ctx):
    result = DBA.CLIP_TEST.get_records(id__in=[54, 100])
    print(result)
    return result


# def fetch_origin_clips(ctx):
#     result = DBA.CLIP.get_records(id__ge=100)
#     print(result)
#     return result

def fetch_origin_clips(ctx):
    """ CLIP """
    clips = DBA.CLIP.get_records(
        id__ge=40000,
        types=CLIP_SELECTED_TYPES
    )
    id__in = _.pluck(clips, "id")
    result = {
        "clip_id__in": id__in,
        "clips": clips,
    }
    print(result)
    return result

def fetch_origin_clip_marks(ctx):
    """ CLIP_MARK """
    clip_ids = list(ctx["clip_id__in"])
    clip_marks = DBA.CLIP_MARK.get_records(id__in=clip_ids)
    id__in = _.pluck(clip_marks, "mark_id")
    print(clip_marks)
    return _.extend({}, ctx, {
        "mark_id__in": id__in,
        "clip_marks": clip_marks,
    })

def fetch_origin_marks(ctx):
    """ MARK """
    mark_id__in = list(ctx["mark_id__in"])
    marks = DBA.MARK.get_records(id__in=mark_id__in)
    print(marks)
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
    def select_marks(marks_gr, clip_id, mark_type):
        marks_for_clip = marks_gr.get(clip_id, {})
        return _.chain(marks_for_clip).filter(
            lambda m: \
                m.get("mark_type_id") == mark_type.value
        ).sort_by(
            lambda m:\
                m.get("position") or 999
        ).pluck("mark_id").value


    clips = list(ctx["clips"])
    marks = list(ctx["marks_lookup"])
    marks_gr = _.group_by(marks, "clip_id")
    annotated = _.chain(clips).map(lambda c: \
        _.extend({}, c, {
            "categoties": select_marks(marks_gr, c["id"], MARK_TYPES.CATEGORIES),

            "genres": select_marks(marks_gr, c["id"], MARK_TYPES.GENRES),

            "moods": select_marks(marks_gr, c["id"], MARK_TYPES.MOOD),

            "tags": select_marks(marks_gr, c["id"], MARK_TYPES.TAGS),

            "actors": select_marks(marks_gr, c["id"], MARK_TYPES.ACTORS),

            "directors": select_marks(marks_gr, c["id"], MARK_TYPES.DIRECTORS),

            "studio": select_marks(marks_gr, c["id"], MARK_TYPES.STUDIO),

            "countries": select_marks(marks_gr, c["id"], MARK_TYPES.COUNTRIES),

            "composers": select_marks(marks_gr, c["id"], MARK_TYPES.COMPOSERS),

            "year_intervals": select_marks(marks_gr, c["id"], MARK_TYPES.YEAR_INTERVALS),


        })).value

    # print(marks)
    # return _.extend({}, ctx, {"marks": marks})
    return annotated

# print (check_tvz_catalog_state())

def run_with(source, dest):
    return Chain(
            source
        ).then(
            fetch_origin_clips
        ).then(
            fetch_origin_clip_marks
        ).then(
            fetch_origin_marks
        ).then(
            reflect_mark_to_clip
        ).then(
            annotate_clip_with_mark
        # )
        # .then(
        #     annotate_subject
        # ).then(
        #     encode_ga_ecomm_event
        ).then(
            dest
        )

def runall(ctx):
    run_with(
        {},
        json_stream('./result10.json')
    )