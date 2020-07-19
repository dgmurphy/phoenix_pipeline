# Phoenix Pipeline

A fork of the OEDA Phoenix Pipeline. See the original repo for more detailed information:

https://github.com/openeventdata/phoenix_pipeline

and

https://phoenix-pipeline.readthedocs.io/en/latest/

The Phoenix Pipeline takes the sentence content and the parse trees and produces events using the Petrarch event coder. Petrach includes a number of data dictionaries including the CAMEO event codes, Actor, Agent and Issues dictionaries, and a Discards list. 

Read more about Petrarch here:

https://petrarch.readthedocs.io/


Note: this version of the pipeline has Geocoding disabled. Events will not be location coded but the source sentence will be saved with each event so a seperate process can be used to perform sentence-level geocoding.


## Prerequisites
Requires text content and parse trees to be populated in MongoDB.

## Install

### Clone the Repo


```git clone https://github.com/dgmurphy/phoenix_pipeline.git```

### Create Python Environment & Install libraries

In the phoenix_pipeline directory perform the usual steps to create & activate the virtual environment, then pip install -r requirements.txt.


### Edit the Config File

The pipeline will process events on a per-day basis by checking the date fields of the stories in MongoDB.
To process events for a particular day we need to specify that day in the config file.


In the file `PHOX_config.ini` :

`run_date = 20200713`

NOTE: To process events on the same day they were collected, set the run_date to today's date plus one day.

### Do a Test Run of the Pipeline

```python pipeline.py```


The pipeline should produce a csv file e.g.:

`events.full.20200713.csv`

Open this file in LibreOffice to view it.  For the seperator options use:

* Seperated by: Tab only
* String delimeter: '   (single quote)
