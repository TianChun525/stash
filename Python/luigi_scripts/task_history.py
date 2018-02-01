#!/usr/bin/bash

import sqlite3
import pandas


def read_task_db(fname):
    """
    Read a task history database written by luigi.
    """
    connection = sqlite3.connect(fname)
    # cursor = connection.cursor()
    # query = "SELECT name FROM sqlite_master WHERE type='table';"
    # tables = cursor.execute(query).fetchall()

    tasks = pandas.read_sql_query("SELECT * from tasks", connection)
    events = pandas.read_sql_query("SELECT * from task_events", connection)
    params = pandas.read_sql_query("SELECT * from task_parameters", connection)

    return tasks, events, params


def retrieve_status(fname, task_name=None):
    """
    Retrieve the task status given by `task_name` for each L1 dataset.
    """
    if task_name is None:
        raise ValueError('Parameter "task_name" cannot be None')

    tasks, events, params = read_task_db(fname)

    task = tasks[tasks.name == task_name]
    l1_datasets = params[params.name == 'level1']

    # event status for the DataStandardisation Task
    status = task.merge(events, how='left', left_on='id', right_on='task_id',
                        suffixes=['_{}'.format(task_name), '_events'])

    # final status for each DataStandardisation Task
    final_status = status.drop_duplicates('id_{}'.format(task_name),
                                          keep='last')

    # get the DONE, FAILED & PENDING Tasks
    # (if the task status is PENDING:
    # then the compute job could've timed out
    # or
    # an upstream dependency failed for some reason
    done = final_status[final_status.event_name == 'DONE']
    fail = final_status[final_status.event_name == 'FAILED']
    pending = final_status[final_status.event_name == 'PENDING']

    l1_done = done.merge(l1_datasets, how='left', right_on='task_id',
                         left_on='id_{}'.format(task_name))
    l1_fail = fail.merge(l1_datasets, how='left', right_on='task_id',
                         left_on='id_{}'.format(task_name))
    l1_pending = pending.merge(l1_datasets, how='left', right_on='task_id',
                               left_on='id_{}'.format(task_name))

    return l1_done, l1_fail, l1_pending
