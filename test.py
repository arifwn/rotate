import unittest

import datetime


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_filename_generation(self):
        # make sure the filename is generated correctly according to
        # format specified
        from rotate import generate_filename

        filename_format = '{prefix}-{date:%d-%m-%Y}.{extension}'
        expected_filename = 'backup-07-02-2015.tar.gz'
        current_date = datetime.datetime(day=7, month=2, year=2015)
        filename = generate_filename(filename_format=filename_format, date=current_date, prefix='backup', extension='tar.gz')
        self.assertEqual(expected_filename, filename)

    def test_filename_parsing(self):
        # make sure the filename parsers are working
        from rotate import parse_filename_data, parse_filename_date

        filename_format = '{prefix}-{date:%d-%m-%Y}.{extension}'
        input_filename = 'backup.tar.gz'
        input_filename_2 = 'backup.tgz'
        input_filename_with_date = 'backup-07-02-2015.tar.gz'

        expected_parsed_data = {'prefix': 'backup', 'extension': 'tar.gz'}
        expected_parsed_data_2 = {'prefix': 'backup', 'extension': 'tgz'}
        expected_parsed_date = datetime.datetime(day=7, month=2, year=2015)

        parsed_data = parse_filename_data(input_filename)
        parsed_data_2 = parse_filename_data(input_filename_2)
        parsed_date = parse_filename_date(input_filename_with_date, '-', 1, 2, 3)

        self.assertEqual(expected_parsed_data['prefix'], parsed_data['prefix'])
        self.assertEqual(expected_parsed_data['extension'], parsed_data['extension'])

        self.assertEqual(expected_parsed_data_2['prefix'], parsed_data_2['prefix'])
        self.assertEqual(expected_parsed_data_2['extension'], parsed_data_2['extension'])

        self.assertEqual(expected_parsed_date.day, parsed_date.day)
        self.assertEqual(expected_parsed_date.month, parsed_date.month)
        self.assertEqual(expected_parsed_date.year, parsed_date.year)

    def test_backup(self):
        from rotate import should_backup_daily, should_backup_weekly, should_backup_monthly

        self.assertEqual(True, should_backup_daily(datetime.datetime(day=1, month=3, year=2015)))
        self.assertEqual(True, should_backup_daily(datetime.datetime(day=2, month=3, year=2015)))

        self.assertEqual(True, should_backup_weekly(datetime.datetime(day=9, month=2, year=2015)))
        self.assertEqual(False, should_backup_weekly(datetime.datetime(day=10, month=2, year=2015)))

        self.assertEqual(True, should_backup_monthly(datetime.datetime(day=1, month=3, year=2015)))
        self.assertEqual(False, should_backup_monthly(datetime.datetime(day=2, month=3, year=2015)))

    def test_purge(self):
        from rotate import get_purge_list

        filelist = [
            'backup-16-02-2015.tar.gz',
            'backup-02-02-2015.tar.gz',
            'backup-01-02-2015.tar.gz',
            'backup-03-02-2015.tar.gz',
            'backup-14-02-2015.tar.gz',
            'backup-09-02-2015.tar.gz',
            'backup-04-02-2015.tar.gz',
            'backup-06-02-2015.tar.gz',
            'backup-05-02-2015.tar.gz',
            'backup-07-02-2015.tar.gz',
            'backup-10-02-2015.tar.gz',
            'backup-15-02-2015.tar.gz',
            'backup-11-02-2015.tar.gz',
            'backup-08-02-2015.tar.gz',
            'backup-13-02-2015.tar.gz',
            'backup-05-03-2015.tar.gz',
            'backup-12-02-2015.tar.gz',
        ]

        purge_list = get_purge_list(filelist, 14, '-', 1, 2, 3)
        self.assertEqual(3, len(purge_list))
        self.assertEqual('backup-01-02-2015.tar.gz', purge_list[0])
        self.assertEqual('backup-02-02-2015.tar.gz', purge_list[1])
        self.assertEqual('backup-03-02-2015.tar.gz', purge_list[2])

    def test_purge(self):
        from rotate import get_config

        config = get_config()

        self.assertEqual('/var/backup/daily', config['daily_dir'])
        self.assertEqual('/var/backup/weekly', config['weekly_dir'])
        self.assertEqual('/var/backup/monthly', config['monthly_dir'])

        config = get_config('test_dir/config.json')

        self.assertEqual('test_dir/daily', config['daily_dir'])
        self.assertEqual('test_dir/weekly', config['weekly_dir'])
        self.assertEqual('test_dir/monthly', config['monthly_dir'])

        self.assertEqual(14, config['daily_num'])
        self.assertEqual(5, config['weekly_num'])
        self.assertEqual(12, config['monthly_num'])

        self.assertEqual("{prefix}-{date:%d-%m-%Y}.{extension}", config['filename_format'])


if __name__ == '__main__':
    unittest.main()

