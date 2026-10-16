"""Web form frontend for the Weight / Mass Converter application.

Serves a browser-based interface built with ONLY the Python standard
library (http.server) plus plain HTML/CSS/JavaScript. There is no Flask,
Django, FastAPI, React, Node or npm involved. The backend (converter.py)
and the database layer (database.py) are reused unchanged.

Run with: python web_server.py
Then open: http://127.0.0.1:8000
"""

import html
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import converter
import database

HOST = "127.0.0.1"
PORT = 8000

UNITS = ["Kilogram", "Gram",  "Tonne"]

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Segoe UI", Arial, sans-serif; background: #f4f6f9; color: #1d2733; }
.page { max-width: 760px; margin: 0 auto; padding: 24px 24px 40px; }
.header { text-align: center; padding: 16px 0 6px; }
.header h1 { color: #1f4e79; font-size: 26px; letter-spacing: 0.5px; }
.header p { color: #5d6b7a; margin-top: 4px; }
.card { background: #ffffff; border: 1px solid #d9dee4; border-radius: 10px;
        padding: 22px; margin-top: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.05); }
label.field { display: block; font-size: 12px; color: #5d6b7a; margin-bottom: 4px; font-weight: 600; }
input[type=text] { width: 100%; padding: 11px; font-size: 15px; border: 1px solid #d9dee4;
                  border-radius: 6px; text-align: center; outline: none; }
input[type=text]:focus { border-color: #2e86c1; }
.unit-row { display: flex; gap: 10px; align-items: flex-end; margin-top: 14px; }
.unit-box { flex: 1; }
select { width: 100%; padding: 10px; font-size: 14px; border: 1px solid #d9dee4;
         border-radius: 6px; background: #ffffff; cursor: pointer; }
.buttons { display: flex; gap: 10px; margin-top: 18px; }
.btn { flex: 1; padding: 12px; border: none; border-radius: 6px; font-size: 15px;
       font-weight: 600; color: #ffffff; cursor: pointer; }
.btn.primary { background: #1f4e79; flex: 2; }
.btn.primary:hover { background: #163a5c; }
.btn.info { background: #2e86c1; }
.btn.info:hover { background: #2471a3; }
.btn.light { background: #7f8c8d; }
.btn.light:hover { background: #626f7d; }
.btn.danger { background: #c0392b; }
.btn.danger:hover { background: #943126; }
.banner { margin-top: 16px; padding: 14px; border-radius: 8px; font-weight: 600;
          text-align: center; font-size: 15px; }
.banner.ok { background: #eaf6ef; color: #1e7e34; border: 1px solid #bfe6cf; }
.banner.err { background: #fdeeea; color: #c0392b; border: 1px solid #f3c2bb; }
.history-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.history-head h2 { color: #1f4e79; font-size: 15px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { background: #1f4e79; color: #ffffff; padding: 10px; text-align: center; }
td { padding: 9px; text-align: center; border-bottom: 1px solid #eef1f5; }
tr:nth-child(even) td { background: #f8fafc; }
.empty { text-align: center; color: #5d6b7a; padding: 14px; }
.footer { text-align: center; color: #8a97a3; font-size: 12px; margin-top: 18px; }
"""

JS = """
function swapUnits() {
    var from = document.getElementById("from_unit");
    var to = document.getElementById("to_unit");
    var temp = from.value;
    from.value = to.value;
    to.value = temp;
}
function clearAll() {
    document.getElementById("value").value = "";
    document.getElementById("from_unit").value = "Kilogram";
    document.getElementById("to_unit").value = "Gram";
    var banner = document.getElementById("banner");
    if (banner) { banner.style.display = "none"; }
}
"""


def format_number(value):
    """Return a clean, readable string representation of a number.

    Integers show without decimals; other values are shown with up to ten
    decimal places, with trailing zeros removed.
    """
    number = float(value)
    if number == int(number):
        return str(int(number))
    return "{:.10f}".format(number).rstrip("0").rstrip(".")


def parse_value(raw):
    """Validate a submitted value.

    Returns (parsed_positive_float, None) or (None, friendly_error).
    """
    raw = raw.strip()
    if not raw:
        return None, converter.ERROR_EMPTY
    try:
        value = float(raw)
    except ValueError:
        return None, converter.ERROR_INVALID
    if value <= 0:
        return None, converter.ERROR_NON_POSITIVE
    return value, None


def _render_options(selected):
    options = []
    for unit in UNITS:
        mark = " selected" if unit == selected else ""
        options.append('<option value="{0}"{1}>{0}</option>'.format(html.escape(unit), mark))
    return "\n            ".join(options)


def _render_history_rows():
    records = database.get_history()
    if not records:
        return ('<tr><td colspan="5" class="empty">'
                "No conversions yet. Convert a value to build your history.</td></tr>")
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            "</tr>".format(
                html.escape(format_number(record["input_value"])),
                html.escape(record["from_unit"]),
                html.escape(record["to_unit"]),
                html.escape(format_number(record["result"])),
                html.escape(record["timestamp"]),
            )
        )
    return "\n            ".join(rows)


def render_page(value="", from_unit="Kilogram", to_unit="Gram", result=None, error=None):
    """Build the full HTML page for the browser."""
    banner = ""
    if error:
        banner = '<div class="banner err" id="banner">{}</div>'.format(html.escape(error))
    elif result:
        banner = '<div class="banner ok" id="banner">{}</div>'.format(html.escape(result))

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weight / Mass Converter</title>
<style>{css}</style>
</head>
<body>
<div class="page">
    <div class="header">
        <h1>WEIGHT / MASS CONVERTER</h1>
        <p>Convert between different units of weight and mass</p>
    </div>

    <div class="card">
        <form method="post" action="/convert">
            <label class="field" for="value">Enter Value</label>
            <input type="text" id="value" name="value" value="{value}" autofocus>

            <div class="unit-row">
                <div class="unit-box">
                    <label class="field" for="from_unit">From Unit</label>
                    <select id="from_unit" name="from_unit">
            {from_options}
                    </select>
                </div>
                <div class="unit-box">
                    <button type="button" class="btn info" id="swap" onclick="swapUnits()">SWAP</button>
                </div>
                <div class="unit-box">
                    <label class="field" for="to_unit">To Unit</label>
                    <select id="to_unit" name="to_unit">
            {to_options}
                    </select>
                </div>
            </div>

            <div class="buttons">
                <button type="submit" class="btn primary">CONVERT</button>
                <button type="button" class="btn light" onclick="clearAll()">CLEAR</button>
            </div>
        </form>
    </div>

    {banner}

    <div class="card">
        <div class="history-head">
            <h2>Conversion History</h2>
            <form method="post" action="/clear_history">
                <button type="submit" class="btn danger">CLEAR HISTORY</button>
            </form>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Input</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Result</th>
                    <th>Date/Time</th>
                </tr>
            </thead>
            <tbody>
            {history_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">Built with Python (standard library) &amp; SQLite - fully offline</div>
</div>
<script>{js}</script>
</body>
</html>""".format(
        css=CSS,
        js=JS,
        value=html.escape(value),
        from_options=_render_options(from_unit),
        to_options=_render_options(to_unit),
        banner=banner,
        history_rows=_render_history_rows(),
    )


class ConverterHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web form."""

    def log_message(self, fmt, *args):
        print("[server]", fmt % args)

    def _send_page(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        if parsed.path != "/":
            self._send_page(404, "text/plain; charset=utf-8", "Not found.")
            return

        query = parse_qs(parsed.query)
        value = query.get("value", [""])[0]
        from_unit = query.get("from_unit", [UNITS[0]])[0]
        to_unit = query.get("to_unit", [UNITS[1]])[0]
        result = query.get("result", [None])[0]
        error = query.get("error", [None])[0]
        if from_unit not in UNITS:
            from_unit = UNITS[0]
        if to_unit not in UNITS:
            to_unit = UNITS[1]

        page = render_page(value=value, from_unit=from_unit, to_unit=to_unit, result=result, error=error)
        self._send_page(200, "text/html; charset=utf-8", page)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        params = parse_qs(body)

        if parsed.path == "/convert":
            self._handle_convert(params)
        elif parsed.path == "/clear_history":
            database.clear_history()
            self._redirect("/")
        else:
            self._send_page(404, "text/plain; charset=utf-8", "Not found.")

    def _handle_convert(self, params):
        from_unit = params.get("from_unit", [UNITS[0]])[0]
        to_unit = params.get("to_unit", [UNITS[1]])[0]
        value_raw = params.get("value", [""])[0]

        base_state = {"value": value_raw, "from_unit": from_unit, "to_unit": to_unit}

        if from_unit not in UNITS or to_unit not in UNITS:
            base_state["error"] = "One of the selected units is not supported."
            self._redirect("/?" + urlencode(base_state))
            return

        value, error = parse_value(value_raw)
        if error:
            base_state["error"] = error
            self._redirect("/?" + urlencode(base_state))
            return

        try:
            result = converter.convert_weight(value, from_unit, to_unit)
        except KeyError:
            base_state["error"] = "One of the selected units is not supported."
            self._redirect("/?" + urlencode(base_state))
            return

        database.save_conversion(value, from_unit, to_unit, result)
        output = "{} {} = {} {}".format(
            format_number(value), from_unit, format_number(result), to_unit
        )
        query = {
            "value": format_number(value),
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": output,
        }
        self._redirect("/?" + urlencode(query))


def main():
    database.initialize_database()
    server = HTTPServer((HOST, PORT), ConverterHandler)
    url = "http://{}:{}/".format(HOST, PORT)
    print("Weight / Mass Converter web form running at", url)
    print("Press Ctrl+C to stop the server.")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()