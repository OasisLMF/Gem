GEM Foundation GMO Model README
====================================================================================


## Forked from 
* [imprompt/oasis-test](https://github.com/imprompt/oasis-test)
* [pslh/oasis-test](https://github.com/pslh/oasis-test)


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
On linux systems there is a launch script `./run-platform.sh` which start up the GEM model and Oasis Platform. Once running you can assess these via the following URL's

* [Local link - User Interface](http://localhost:8080/).
* [Local link - Oasis API](http://localhost:8000/) 
