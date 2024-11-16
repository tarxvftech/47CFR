#!/bin/bash


curl -X GET "https://www.ecfr.gov/api/versioner/v1/full/2024-11-14/title-47.xml?chapter=1&part=97" -H  "accept: application/xml" -o part_97.xml
curl -X GET "https://www.ecfr.gov/api/versioner/v1/full/2024-11-14/title-47.xml?chapter=1&part=80" -H  "accept: application/xml" -o part_80.xml
#and then auto-indented with vim gg=G
