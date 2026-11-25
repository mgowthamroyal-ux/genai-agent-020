Open index.html in Chrome after extracting the ZIP. All six default product photos are embedded and also included in assets. Internet is not required for these photos. Backend setup: install requirements.txt and configure .env for optional API functionality.

Product photographs cropped from six user-supplied screenshots, not original downloaded files. Sources shown in screenshots:
1 Sony: pcdiga.com
2 Apple Watch: istoreil.co.il
3 Samsung: ldlc.com
4 Nike: 50style.pl
5 boAt: amazon.in
6 MacBook: alsheikhstores.com

Previous setup instructions (image notes superseded):
# Online Photos Edition

Open index.html with internet access. External product images are not bundled and may fail if hosts block requests.

# Product Studio — GENAI-AGENT-020
New implementation based on the visible project requirements, not a patch to the unavailable original source.

## Open without installing anything
Extract ZIP and double-click index.html. Nine navigation pages work with browser local storage. Offline templates are not AI. Competitor data is entered manually. Reports use browser Print / Save as PDF. No data migration from the original project.

## Live HTML edition
In PowerShell in the extracted folder: `py -m pip install -r requirements.txt`. Copy .env.example to .env and set your own API key. Run `py server.py` and open http://127.0.0.1:8000. API requests require confirmation and may cost money. Never share .env. Server is local only, not production hardened.

## Native Streamlit edition
Run `py -m streamlit run app.py`. This separate three-page edition implements the core LLM content generation and SQLite draft storage required by the visible internship task. It does not share the HTML browser storage. The full nine-page HTML interface uses Flask, not Streamlit. Verify the task reference before submission.

HTML upgrade: theme toggle, SVG product illustrations and navigation icons, category filter and clickable chart bars, activity panel, footer. Browser storage remains local to the page origin.


Branded edition: six sample products with external retailer image URLs and company website favicon badges. Internet is required for images, and third-party hosts may block or change URLs. Prices are illustrative. The HTML is an independent nine-page application; app.py is the earlier separate three-page Streamlit example. Not affiliated with depicted brands.

Offline edition: bundled SVG product illustrations and company-name badges are placeholders, not real photographs or official logos. Use Products > Edit > Upload real product photo > Save product to replace them. Extract all files before opening index.html. Existing browser data is not migrated.

Screenshot edition: products 1–4 use crops of the supplied ChatGPT screenshot. Samsung and Nike are partial crops; boAt and MacBook remain illustrations. Images are not original manufacturer files.

## Photo edition
Sony and Apple Watch photographs are screenshot crops. Samsung and Nike photographs are partial screenshot crops. boAt and MacBook retain placeholder illustrations. External photo retrieval failed. All assets are local.

Midnight 3D edition: CSS depth, blue palette and hover effects; backend unchanged.

Aurora edition: original CSS gradient and metallic sphere artwork; dark mode default. Existing six supplied product photos retained.

Full Aurora edition: fixed CSS ambient background across every page. Theme toggle adjusts glow intensity. Product photos unchanged.
