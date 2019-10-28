#!/bin/bash
# This script is called from the crontab which runs every Wednesday and downloads the latest GeoIP databases

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
mkdir -p $DIR/GeoLite
cd $DIR/GeoLite/

wget 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz' -O GeoLite2-City.tar.gz
wget 'https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz' -O GeoLite2-Country.tar.gz

tar -xzf GeoLite2-City.tar.gz 
tar -xzf GeoLite2-Country.tar.gz

mv GeoLite2-City_*/*.mmdb ./
mv GeoLite2-Country_*/*.mmdb ./

find . -not -name '*.mmdb' -delete
