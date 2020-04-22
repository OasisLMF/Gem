```
project_name [OM]: GEM Model for OASIS (test)
project_slug [GEMModelforOASIS(test)]: gemoasismodel
project_short_description [Oasis Model]: A GEM Model for the OASIS framework
project_maintainer [<full name of primary project maintainer>]: GEM Foundation
project_maintainer_email [<primary GitHub account email of primary project maintainer>]: devops@openquake.org
version [0.0.1]: 
primary_language [Python]: 
organization [OasisLMF]: GEM Foundation
model_identifier [OM]: GMO
model_version [0.0.0.1]: 0.0.0.1
```


GEM Foundation GMO Model README
====================================================================================

## Installing and running the model

The easiest way to test the model is under the [oasislmf python package](https://github.com/OasisLMF/OasisLMF). If you have access to a unix computer, this can be done as follows:
```
pip install oasislmf
./run-mdk.sh
```
This will place output in the folder runs.
You can change the model settings, including the exposure used for input, by editing the file `oasislmf.json`


## Running the GEM using docker 

To run using the full oasis platform you'll need a system with [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed.
On linux systems there is a launch script `./run-platform.sh` which start up the model worker, [Oasis API](http://localhost:8000/) and [User Interface](http://localhost:8080/).
