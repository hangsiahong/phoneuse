"""Mouse, touchpad and keyboard on the mirror window itself, through GTK, for compositors
without Hyprland's IPC (niri, Sway, GNOME, KDE): mirror_input.py's gestures (pointer.py)
without /dev/input. Hover moves the phone's pointer, click taps, drag swipes, the wheel or
two-finger scroll scrolls, and keys type on the phone while the window has focus.
The process is `-m phoneuse.window`, so the HID daemon takes it as the owner's input."""
import time

from gi.repository import Gdk, Gtk

from . import screen, touch
from .hidclient import Hid
from .mirror_input import _EV2HID, _EVMOD, NOTCH_PT
from .pointer import Keys, Pointer

EVDEV_OFFSET = 8  # Wayland/XKB keycode = evdev code + 8


def log(*a):
    print(time.strftime("%H:%M:%S"), "mirror input:", *a, flush=True)


def attach(win, phone):
    """Drive the phone from `phone` (window.Phone) inside `win`."""
    shared = {"hid": None}

    def hid():
        if shared["hid"] is None:
            shared["hid"] = Hid()
        return shared["hid"]

    pointer = Pointer(hid, log)
    keys = Keys(hid)
    at = {"xy": None}  # last pointer position over the widget

    def frac(x, y):
        """Widget coordinates -> fractions of the phone picture (outside 0..1 on the bezel)."""
        px, py, pw, ph = screen.picture_rect((0, 0), (phone.get_width(), phone.get_height()), phone.points())
        return (x - px) / pw, (y - py) / ph

    def live():
        return not phone.waiting

    def on_motion(_c, x, y):
        at["xy"] = (x, y)
        if live() and not pointer.pressed:
            pointer.hover(*frac(x, y))

    motion = Gtk.EventControllerMotion()
    motion.connect("motion", on_motion)
    phone.add_controller(motion)

    # A drag keeps reporting while the pointer is outside the window (GTK's implicit grab).
    drag = Gtk.GestureDrag(button=Gdk.BUTTON_PRIMARY)
    start = {"xy": (0, 0)}

    def on_begin(_g, x, y):
        start["xy"] = (x, y)
        if live():
            pointer.hover(*frac(x, y))
            pointer.press(*frac(x, y))

    def on_update(_g, dx, dy):
        x, y = start["xy"][0] + dx, start["xy"][1] + dy
        at["xy"] = (x, y)
        if pointer.pressed:
            pointer.hover(*frac(x, y))

    drag.connect("drag-begin", on_begin)
    drag.connect("drag-update", on_update)
    drag.connect("drag-end", lambda *_: pointer.release())
    phone.add_controller(drag)

    # iOS ignores the wheel: pointer.scroll turns it into a drag. Wheel notches and touchpad
    # pixels both become phone points; positive moves the content down (finger dragging down).
    scroll = Gtk.EventControllerScroll(flags=Gtk.EventControllerScrollFlags.BOTH_AXES)

    def on_scroll(c, dx, dy):
        if not live() or at["xy"] is None:
            return True
        pointer.hover(*frac(*at["xy"]))
        if c.get_unit() == Gdk.ScrollUnit.WHEEL:
            pointer.scroll(-dx * NOTCH_PT, -dy * NOTCH_PT)
        else:  # touchpad: follow the fingers 1:1 with the picture
            _px, _py, pw, ph = screen.picture_rect((0, 0), (phone.get_width(), phone.get_height()), phone.points())
            pts = touch.pt()
            pointer.scroll(-dx * pts[0] / pw, -dy * pts[1] / ph)
        return True

    scroll.connect("scroll", on_scroll)
    phone.add_controller(scroll)

    key = Gtk.EventControllerKey()

    def on_key(down):
        def handler(_c, _keyval, keycode, _state):
            code = keycode - EVDEV_OFFSET
            if not live() or (code not in _EVMOD and code not in _EV2HID):
                return False
            try:
                if code in _EVMOD:
                    keys.modifier(_EVMOD[code], down)
                else:
                    keys.key(_EV2HID[code], down)  # held keys repeat on the phone itself
            except Exception as e:
                log("key error:", e)
                shared["hid"] = None
            return True
        return handler

    key.connect("key-pressed", on_key(True))
    key.connect("key-released", lambda c, kv, kc, st: on_key(False)(c, kv, kc, st))
    win.add_controller(key)

    def on_active(w, _p):
        if not w.is_active():  # focus left: let go of everything on the phone
            try:
                keys.release_all()
            except Exception as e:
                log("key error:", e)
            pointer.release()

    win.connect("notify::is-active", on_active)
    log("hover, click, drag, scroll and type on the window drive the phone")
    return pointer
