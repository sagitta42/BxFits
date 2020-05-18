#!/bin/bash
name=mredchuk
echo "name: $name"
condor_transfer_data -name sn-01.cr.cnaf.infn.it $name -constraint 'JobStatus == 4'
sleep 5
condor_rm -name sn-01.cr.cnaf.infn.it $name -constraint 'JobStatus == 4'
