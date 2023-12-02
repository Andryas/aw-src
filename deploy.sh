#!/bin/bash
# rc-update add docker boot

echo; echo "setting the gcp image tag to the newly built one..."
docker save -o scraping.tar aw/scraping:latest

echo; echo "pushing the image to VM"
gcloud compute scp scraping.tar scraping:/home/wavrzenczak --zone "us-central1-a" --project "waurzenczak"