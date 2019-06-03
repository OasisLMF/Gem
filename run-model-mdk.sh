#! /bin/bash
make -C model_data/GMO/
time oasislmf model run -C oasislmf.json
