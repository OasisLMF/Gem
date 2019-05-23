#! /bin/bash
make -C model_data/GMO/
time oasislmf model run -C mdk-oasislmf-gem.json
