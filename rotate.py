#!/usr/bin/env python

import datetime
import json
import os
import sys
import logging
import shutil


def generate_filename(filename_format, date, prefix, extension):
    return filename_format.format(date=date, prefix=prefix, extension=extension)


def parse_filename_data(filepath):
    filename = os.path.basename(filepath)
    prefix = ''
    extension = ''
    if filename[-6:] == 'tar.gz':
        prefix = filename[:-7]
        extension = filename[-6:]
    else:
        split = os.path.splitext(filename)
        prefix = split[0]
        extension = split[1].lstrip('.')
    return {'prefix': prefix, 'extension': extension}


def parse_filename_date(filename, separator='-', day_pos=1, month_pos=2, year_pos=3):
    data = parse_filename_data(filename)
    name = data['prefix']
    split = name.split(separator)

    day = None
    month = None
    year = None

    if len(split) >= day_pos:
        day = int(split[day_pos])
    if len(split) >= month_pos:
        month = int(split[month_pos])
    if len(split) >= year_pos:
        year = int(split[year_pos])
    return datetime.datetime(day=day, month=month, year=year)


def should_backup_daily(date=None):
    # return True everyday
    return True


def should_backup_weekly(date=None):
    # return True every monday
    if date is None:
        date = datetime.datetime.now()

    backup = False
    if date.weekday() == 0:
        backup = True

    return backup


def should_backup_monthly(date=None):
    # return True every first day of the month
    if date is None:
        date = datetime.datetime.now()

    backup = False
    if date.day == 1:
        backup = True

    return backup


def get_purge_list(filelist, max_num, separator='-', day_pos=1, month_pos=2, year_pos=3):
    # return oldest files that must be deleted
    purge_list = []
    dates = {}

    for filename in filelist:
        dates[filename] = parse_filename_date(filename, separator, day_pos, month_pos, year_pos)

    sorted_list = sorted(filelist, key=lambda filename: dates[filename])

    if len(sorted_list) > max_num:
        purge_list = sorted_list[:len(sorted_list) - max_num]

    return purge_list


def get_config(config_path=None):
    config = {}

    config['daily_dir'] = '/var/backup/daily'
    config['daily_num'] = 14

    config['weekly_dir'] = '/var/backup/weekly'
    config['weekly_num'] = 5

    config['monthly_dir'] = '/var/backup/monthly'
    config['monthly_num'] = 12

    config['filename_format'] = '{prefix}-{date:%d-%m-%Y}.{extension}'

    if config_path:
        config_data = None
        with open(config_path) as f:
            config_data = json.load(f)

        if config_data:
            config['daily_dir'] = config_data.get('daily_dir', config['daily_dir'])
            config['daily_num'] = config_data.get('daily_num', config['daily_num'])
            config['weekly_dir'] = config_data.get('weekly_dir', config['weekly_dir'])
            config['weekly_num'] = config_data.get('weekly_num', config['weekly_num'])
            config['monthly_dir'] = config_data.get('monthly_dir', config['monthly_dir'])
            config['monthly_num'] = config_data.get('monthly_num', config['monthly_num'])
            config['filename_format'] = config_data.get('filename_format', config['filename_format'])

    return config


def backup_file(filepath, target_dir, filename_format='{prefix}-{date:%d-%m-%Y}.{extension}', date=None):
    if date is None:
        date = datetime.datetime.now()

    parsed_data = parse_filename_data(filepath)
    target_filename = generate_filename(filename_format=filename_format, date=date, prefix=parsed_data['prefix'], extension=parsed_data['extension'])
    target_filepath = os.path.join(target_dir, target_filename)

    logging.debug("backup %s" % target_filepath)
    shutil.copyfile(filepath, target_filepath)


def get_files(target_dir):
    filelist = []
    rawlist = os.listdir(target_dir)
    for filename in rawlist:
        filepath = os.path.join(target_dir, filename)
        if os.path.isfile(filepath):
            filelist.append(filepath)

    return filelist


def main():
    filepath = None
    config_path = None
    date = datetime.datetime.now()
    logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)

    if len(sys.argv) == 1:
        print('usage: rotate.py <file>')

    elif len(sys.argv) == 2:
        filepath = sys.argv[1]

    elif len(sys.argv) == 3:
        config_path = sys.argv[1]
        filepath = sys.argv[2]

    if filepath is None:
        return 1

    config = get_config(config_path)
    if should_backup_daily(date):
        backup_file(filepath, config['daily_dir'], config['filename_format'], date)
    if should_backup_weekly(date):
        backup_file(filepath, config['daily_dir'], config['filename_format'], date)
    if should_backup_monthly(date):
        backup_file(filepath, config['daily_dir'], config['filename_format'], date)

    daily_purge_list = get_purge_list(get_files(config['daily_dir']),
                                      config['daily_num'],
                                      config.get('filename_separator', '-'),
                                      config.get('day_pos', 1),
                                      config.get('month_pos', 2),
                                      config.get('year_pos', 3),
                                      )

    for removed_path in daily_purge_list:
        logging.info('removing %s' % removed_path)
        os.unlink(removed_path)

    weekly_purge_list = get_purge_list(get_files(config['weekly_dir']),
                                      config['weekly_num'],
                                      config.get('filename_separator', '-'),
                                      config.get('day_pos', 1),
                                      config.get('month_pos', 2),
                                      config.get('year_pos', 3),
                                      )

    for removed_path in weekly_purge_list:
        logging.info('removing %s' % removed_path)
        os.unlink(removed_path)

    monthly_purge_list = get_purge_list(get_files(config['monthly_dir']),
                                      config['monthly_num'],
                                      config.get('filename_separator', '-'),
                                      config.get('day_pos', 1),
                                      config.get('month_pos', 2),
                                      config.get('year_pos', 3),
                                      )

    for removed_path in monthly_purge_list:
        logging.info('removing %s' % removed_path)
        os.unlink(removed_path)


if __name__ == '__main__':
    return_val = main()
    exit(return_val)
