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
git clone https://github.com/imprompt/oasis-test.git
cd oasis-test/model_data/GMO
wget http://sunstonerisk.com/files/domrep/footprint.csv.gz
cd ../..
./run-model.sh
```
This will place output in the folder runs.
You can change the model settings, including the exposure used for input, by editing the file mdk-oasislmf-gem.json

