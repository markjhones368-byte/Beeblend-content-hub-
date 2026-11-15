set -x
npm i -g lighthouse@12.6.1 >/dev/null 2>&1
export CHROME_PATH=$(python -c "import glob,os;print(sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome')))[-1])")
mkdir -p out
LIVE=https://beeblend.co.uk/
DRAFT="https://eptqzg-e5.myshopify.com/?preview_theme_id=200711209347&_fd=0&pb=0"
LIVE_MS="https://eptqzg-e5.myshopify.com/?_fd=0&pb=0"
run(){ timeout 150 lighthouse "$1" --quiet --max-wait-for-load=40000 --chrome-flags="--headless=new --no-sandbox" $3 --output=json --output-path=out/$2.json --only-categories=performance,seo,best-practices,accessibility || true; }
for i in 1 2; do
 run "$LIVE_MS" live_mobile_$i
 run "$DRAFT" draft_mobile_$i
 run "$LIVE_MS" live_desktop_$i "--preset=desktop"
 run "$DRAFT" draft_desktop_$i "--preset=desktop"
done
curl -sL -A "Mozilla/5.0" "$LIVE" -o out/home.html
curl -sL -A "Mozilla/5.0" -c out/cj -b out/cj "$DRAFT" -o out/draft.html
CSS=$(grep -o '//beeblend.co.uk/cdn/shop/t/[0-9]*/assets/bb-premium.css[^"]*' out/home.html | head -1)
curl -sL "https:$CSS" -o out/bb-premium.orig.css
python tools/uk_summ.py
