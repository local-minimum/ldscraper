#!/usr/bin/env python3

from scraper import Grades
from tinydb import Query
import numpy as np


def get_all_records_with_data(db, grade=Grades.Overall):

    q = Query()
    return db.search(q["{0}-average".format(grade.name)] != None)


def records_to_array(records, *keys):

    return np.array([[rec[key] for key in keys] for rec in records])


def score_adjustments(scores, votes_received, votes_given, N=4.4):

    return (scores * votes_received +
            np.maximum.outer(0, N - np.log2(votes_given + 1))) / (
                votes_received +
                np.maximum.outer(0, N - np.log2(votes_given + 1)))
