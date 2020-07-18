from __future__ import print_function
from __future__ import unicode_literals
import sys
import logging
import requests
import datetime
import dateutil
import uploader
import utilities
import formatter
import postprocess
import oneaday_filter
import result_formatter
import scraper_connection


def main(file_details, geo_details, server_details, petrarch_version, run_date, mongo_details, logger_file=None, run_filter=None,
         version=''):
    """
    Main function to run all the things.

    Parameters
    ----------

    file_details: Named tuple.
                    All the other config information not in ``server_details``.

    geo_details: Named tuple.
                  Settings for geocoding.

    server_details: Named tuple.
                    Config information specifically related to the remote
                    server for FTP uploading.

    petrarch_version: String.
                       Which version of Petrarch to use. Must be '1' or '2'

    logger_file: String.
                    Path to a log file. Defaults to ``None`` and opens a
                    ``PHOX_pipeline.log`` file in the current working
                    directory.

    run_filter: String.
                Whether to run the ``oneaday_formatter``. Takes True or False
                (strings) as values.

    run_date: String.
                Date of the format YYYYMMDD. The pipeline will run using this
                date. If not specified the pipeline will run with
                ``current_date`` minus one day.
    """
    if logger_file:
        utilities.init_logger(logger_file)
    else:
        utilities.init_logger('PHOX_pipeline.log')
    # get a local copy for the pipeline
    logger = logging.getLogger('pipeline_log')

    if petrarch_version == '1':
        from petrarch import petrarch
        logger.info("Using original Petrarch version")
    elif petrarch_version == '2':
        from petrarch2 import petrarch2 as petrarch
        logger.info("Using Petrarch2")
    else:
        logger.error("Invalid Petrarch version. Argument must be '1' or '2'")


    print('\nPHOX.pipeline run:', datetime.datetime.utcnow())

    if run_date:
        process_date = dateutil.parser.parse(run_date)
        date_string = '{:02d}{:02d}{:02d}'.format(process_date.year,
                                                  process_date.month,
                                                  process_date.day)
        logger.info('Date string: {}'.format(date_string))
        print('Date string:', date_string)
    else:
        process_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        date_string = '{:02d}{:02d}{:02d}'.format(process_date.year,
                                                  process_date.month,
                                                  process_date.day)
        logger.info('Date string: {}'.format(date_string))
        print('Date string:', date_string)
    results, scraperfilename = scraper_connection.main(process_date,
                                                       file_details)
    if geo_details.geo_service == "Mordecai":
        dest = "{0}:{1}/places".format(geo_details.mordecai_host, geo_details.mordecai_port)
        try:
            out = requests.get(dest)
            assert out.status_code == 200
        except (AssertionError, requests.exceptions.ConnectionError):
            print("Mordecai geolocation service not responding. Continuing anyway...")
    elif geo_details.geo_service == "CLIFF":
        print("CLIFF")
    else:
        print("Invalid geo service name. Must be 'CLIFF' or 'Mordecai'. Continuing...")


    if scraperfilename:
        logger.info("Scraper file name: " + scraperfilename)
        print("Scraper file name:", scraperfilename)

    logger.info("Running Mongo.formatter.py")
    print("Running Mongo.formatter.py")
    formatted = formatter.main(results, file_details,
                               process_date, date_string)
    logger.info("Running PETRARCH")
    file_details.fullfile_stem + date_string
    if run_filter == 'False':
        print('Running PETRARCH and writing to a file. No one-a-day.')
        logger.info('Running PETRARCH and writing to a file. No one-a-day.')
        # Command to write output to a file directly from PETR
        #        petrarch.run_pipeline(formatted,
        #                              '{}{}.txt'.format(file_details.fullfile_stem,
        #                                                date_string), parsed=True)

        
        petr_results = petrarch.run_pipeline(formatted, config = "petr_config.ini", write_output=False,
        
        # DGM TEst
        # petrarch.run_pipeline(formatted, out_file = "TESTOUT.txt", config = "petr_config.ini", write_output=True,
                                             parsed=True)
        #sys.exit()

    elif run_filter == 'True':
        print('Running PETRARCH and returning output.')
        logger.info('Running PETRARCH and returning output.')
        petr_results = petrarch.run_pipeline(formatted, config = "petr_config.ini", write_output=False,
                                             parsed=True)
    else:
        print("""Can't run with the options you've specified. You need to fix
              something.""")
        logger.warning("Can't run with the options you've specified. Exiting.")
        sys.exit()

    if run_filter == 'True':
        logger.info("Running oneaday_formatter.py")
        print("Running oneaday_formatter.py")
        formatted_results = oneaday_filter.main(petr_results)
    else:
        logger.info("Running result_formatter.py")
        print("Running result_formatter.py")
        formatted_results = result_formatter.main(petr_results)

    logger.info("Running postprocess.py")
    print("Running postprocess.py")
    if version:
        postprocess.main(formatted_results, date_string, version, file_details,
                         server_details, geo_details)
    else:
        print("Please specify a data version number. Program ending.")

    #logger.info("Running phox_uploader.py")
    # print("Running phox_uploader.py")
    # try:
    #     uploader.main(date_string, server_details, file_details)
    # except Exception as e:
    #     logger.warning("Error on the upload portion. {}".format(e))
    #     print("""Error on the uploader. This step isn't absolutely necessary.
    #           Valid events should still be generated.""")

    logger.info('PHOX.pipeline end')
    print('PHOX.pipeline end:', datetime.datetime.utcnow())


def run():
    #server_details, geo_details, file_details, petrarch_version, run_date = utilities.parse_config('PHOX_config.ini')
    cfg = utilities.parse_config('PHOX_config.ini')
    main(cfg['file_list'], cfg['geo_list'], cfg['server_list'], 
         cfg['petrarch_version'], cfg['run_date'], cfg['file_list'].log_file,
         run_filter=cfg['file_list'].oneaday_filter, version='v0.0.0')

if __name__ == '__main__':
    run()
