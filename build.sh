# rc-update add docker boot
echo; echo "building image..."; echo
docker build --platform=linux/amd64 -t aw/scraping  . || exit 1
