set -x
npm i -g lighthouse@12.6.1 >/dev/null 2>&1
CH=$(python -c "import glob,os;print(sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome')))[-1])")
export CHROME_PATH=$CH
mkdir -p out
for i in 1 2 3; do
 lighthouse https://beeblend.co.uk/ --quiet --chrome-flags="--headless=new --no-sandbox" --output=json --output-path=out/lh_mobile_$i.json --only-categories=performance || true
 lighthouse https://beeblend.co.uk/ --quiet --preset=desktop --chrome-flags="--headless=new --no-sandbox" --output=json --output-path=out/lh_desktop_$i.json --only-categories=performance || true
done
lighthouse https://beeblend.co.uk/products/lychee-honey --quiet --chrome-flags="--headless=new --no-sandbox" --output=json --output-path=out/lh_mobile_product.json --only-categories=performance,seo,best-practices,accessibility || true
curl -sL -A "Mozilla/5.0" https://beeblend.co.uk/ -o out/home.html
curl -sL -A "Mozilla/5.0" https://beeblend.co.uk/robots.txt -o out/robots.txt
python tools/uk_summ.py
