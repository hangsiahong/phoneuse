<img src="packaging/icons/hicolor/256x256/apps/co.lxe.PhoneUse.png" width="128" alt="Phone Use icon: a sleepy cloud hugging a phone">

# Phone Use (hangsiahong fork)

Use your iPhone from your Linux desktop: its screen in a window over AirPlay, and your
laptop's own Bluetooth as the phone's mouse and keyboard. Click to tap, drag to swipe,
scroll, and type. Agents (Claude Code, Codex) can drive it too, with your permission.
No jailbreak, no cable, no extra board.

This is a fork of [lxe/phoneuse](https://github.com/lxe/phoneuse) by Aleksey Smolenchuk,
developed on its own from here. It runs from source on Linux; the iPhone app is still
[Phone Use on the App Store](https://apps.apple.com/us/app/phone-use/id6832337610).

## What this fork adds

- **Any Wayland compositor, not only Hyprland.** On niri, Sway, GNOME or KDE the mirror
  window takes the mouse, touchpad and keys itself, through GTK (`phoneuse/gtk_input.py`):
  hover moves the phone's pointer, click taps, drag swipes (also past the window's edge),
  wheel and two-finger scroll scroll, and keys type while the window has focus.
- **Clean restarts.** Everything `phoneuse serve` starts exits with it, even when it is
  killed, so a crashed or restarted `serve` doesn't leave the ports held ("already running").
- **Which way the phone faces** in `GET :8777/api/picture` (`"landscape": true|false`), so
  a desktop shell can turn the window with the phone.
- Screen reading falls back to the CPU when the GPU's cuDNN won't load.
- [ansai shell](https://github.com/hangsiahong/ansai-shell) runs it for you: Settings › Displays ›
  Control an iPhone starts `phoneuse serve`, opens the window when the phone mirrors,
  floats it phone-shaped at the right and reshapes it when the phone turns.

## Install (Linux, from source)

```sh
git clone https://github.com/hangsiahong/phoneuse.git ~/phoneuse
ln -s ~/phoneuse/bin/phoneuse ~/.local/bin/phoneuse
phoneuse install   # needs sudo: the Bluetooth HID service
phoneuse up        # or `phoneuse serve` without the window
```

Then pair the iPhone app, connect the phone to this PC over Bluetooth, and on the iPhone
pick **Screen Mirroring › Phone Use on &lt;your computer&gt;**.
[docs/SOURCE.md](docs/SOURCE.md) has the requirements, firewall ports and each step.

`phoneuse install` turns off bluetoothd's input plugin: while it is installed, the PC
doesn't take Bluetooth mice and keyboards for itself.

## More

- [How it works](ARCHITECTURE.md) · [The iPhone app and its API](docs/COMPANION.md)
- [The bridge](docs/BRIDGE.md): an ESP32 board as the phone's keyboard and mouse instead
  of the PC's Bluetooth (optional)
- [Windows](docs/WINDOWS.md) · [Mac](docs/MAC.md), as upstream left them; untested here

## License

MIT, as upstream. Copyright (c) 2026 Aleksey Smolenchuk; fork changes by their authors.
