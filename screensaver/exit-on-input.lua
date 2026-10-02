-- Quit mpv on any key press, mouse button, scroll or pointer movement, so the
-- video behaves like a screensaver.

local keys = {
  "ANY_UNICODE", "ESC", "ENTER", "SPACE", "TAB", "BS", "DEL", "INS", "HOME", "END",
  "PGUP", "PGDWN", "UP", "DOWN", "LEFT", "RIGHT", "KP_ENTER",
  "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
  "MBTN_LEFT", "MBTN_RIGHT", "MBTN_MID", "MBTN_BACK", "MBTN_FORWARD",
  "WHEEL_UP", "WHEEL_DOWN", "WHEEL_LEFT", "WHEEL_RIGHT",
}

-- The compositor replays held keys and reports a pointer position as soon as
-- the window maps, so input only counts once the window has settled.
local armed = false

mp.add_timeout(1, function()
  armed = true
end)

local function quit()
  if armed then
    mp.commandv("quit")
  end
end

for i, key in ipairs(keys) do
  mp.add_forced_key_binding(key, "exit-on-input-" .. i, quit)
end

-- Only movement away from where the pointer was once the window settled counts.
local origin = nil

mp.observe_property("mouse-pos", "native", function(_, pos)
  if not pos or not armed then
    return
  end
  if not origin then
    origin = pos
    return
  end
  if math.abs(pos.x - origin.x) > 8 or math.abs(pos.y - origin.y) > 8 then
    quit()
  end
end)

-- Losing focus (workspace switch, another window opening) also ends it.
mp.observe_property("focused", "bool", function(_, focused)
  if focused == false then
    quit()
  end
end)
