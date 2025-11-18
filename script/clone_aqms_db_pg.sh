#!/bin/bash
# script: clone_aqms_db_pg.sh
# auth: Nathan T. Stevens
# org: PNSN
# license: CC0-1.0
# purpose: This script clones the aqms-swg GitLab repo `aqms-db-pg` to get
# the PostgreSQL schema defining files for ANSS/AQMS databases
#
# Stack Overflow Attribution: SCRIPT_DIR syntax
# Source - https://stackoverflow.com/a
# Posted by dogbane, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-10, License - CC BY-SA 4.0 

# Get script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Clone into postgresql folder
git clone https://gitlab.com/aqms-swg/aqms-db-pg.git $SCRIPT_DIR/../postgresql/aqms-db-pg
