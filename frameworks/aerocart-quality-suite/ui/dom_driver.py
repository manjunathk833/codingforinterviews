"""Deterministic HTML DOM Harness for AeroCart UI Page Object Architecture."""
from html.parser import HTMLParser
from typing import Any, Callable, Dict, List, Optional


class _AeroCartHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.seats: Dict[str, Dict[str, Any]] = {}
        self.buttons_by_text: Dict[str, str] = {}
        self._active_btn_id: Optional[str] = None
        self._active_seat: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        amap = {k: v for k, v in attrs}
        el_id = amap.get("id")
        elem = {"tag": tag, "attrs": dict(amap), "text": "", "value": amap.get("value", "")}
        if el_id:
            self.by_id[el_id] = elem
        if tag == "button" and el_id:
            self._active_btn_id = el_id
        if amap.get("data-seat"):
            seat_code = amap["data-seat"]
            self.seats[seat_code] = {"seat": seat_code, "classes": set((amap.get("class") or "").split())}
            self._active_seat = seat_code
        if tag == "option" and "flight-select" in self.by_id and not self.by_id["flight-select"]["value"]:
            self.by_id["flight-select"]["value"] = amap.get("value", "")

    def handle_data(self, data: str) -> None:
        txt = data.strip()
        if self._active_btn_id and txt:
            self.by_id[self._active_btn_id]["text"] = txt
            self.buttons_by_text[txt] = self._active_btn_id

    def handle_endtag(self, tag: str) -> None:
        if tag == "button":
            self._active_btn_id = None
        if tag == "div":
            self._active_seat = None


class AeroCartDomSession:
    """Lightweight in-memory browser session over `apps.aerocart.server.UI_HTML` with route interception."""

    def __init__(self, html_source: str, transport: Callable[..., Dict[str, Any]]) -> None:
        parser = _AeroCartHtmlParser()
        parser.feed(html_source)
        self.by_id = parser.by_id
        self.seats = parser.seats
        self.buttons_by_text = parser.buttons_by_text
        self.selected_seat = "1A"
        self.transport = transport
        self.routes: Dict[str, Dict[str, Any]] = {}

    def intercept_route(self, path_prefix: str, status_code: int, payload: Dict[str, Any]) -> None:
        self.routes[path_prefix] = {"status_code": status_code, "data": dict(payload)}

    def fetch_json(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        for prefix, mocked in self.routes.items():
            if path.startswith(prefix):
                return {"status_code": mocked["status_code"], "data": dict(mocked["data"]), "mocked": True}
        return self.transport(method, path, body=body, headers=headers)
