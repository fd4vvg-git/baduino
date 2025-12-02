import argparse

logo =r"""

 ____             _          ____  ____        _             
|  _ \ _   _  ___| | ___   _|___ \|  _ \ _   _(_)_ __   ___  
| | | | | | |/ __| |/ / | | | __) | | | | | | | | '_ \ / _ \ 
| |_| | |_| | (__|   <| |_| |/ __/| |_| | |_| | | | | | (_) |
|____/ \__,_|\___|_|\_\\__, |_____|____/ \__,_|_|_| |_|\___/ 
                       |___/                                 
"""

# global settings

DEFAULT_DELAY = 0
LAST_COMMAND = None

#template

templateHeader = r"""
// FD4WG

#include <Keyboard.h>

const int safetyPin = 3;

bool payloadExecuted = false;

void setup() {
pinMode(safetyPin, INPUT_PULLUP);
Keyboard.begin();

}

void runPayload() {
//This section is for the badusb payload.
"""

templateFooter = r"""
      
}

void loop() {
int safetyState = digitalRead(safetyPin);

if (safetyState == LOW && payloadExecuted == false) {
  runPayload();
payloadExecuted = true;
}

if (safetyState == HIGH) {
  payloadExecuted=false;
}

}
"""


# key map dict

KEY_MAP = {
    "CTRL": "KEY_LEFT_CTRL",
    "CONTROL": "KEY_LEFT_CTRL",
    "ALT": "KEY_LEFT_ALT",
    "SHIFT": "KEY_LEFT_SHIFT",
    "ESCAPE": "KEY_ESC",
    "GUI": "KEY_LEFT_GUI",
    "WINDOWS": "KEY_LEFT_GUI",
    "WIN": "KEY_LEFT_GUI",
    "ENTER": "KEY_RETURN",
    "RETURN": "KEY_RETURN",
    "TAB": "KEY_TAB",
    "ESC": "KEY_ESC",
    "DELETE": "KEY_DELETE",
    "DEL": "KEY_DELETE",
    "SPACE": "' '",
    "UPARROW": "KEY_UP_ARROW",
    "DOWNARROW": "KEY_DOWN_ARROW",
    "LEFTARROW": "KEY_LEFT_ARROW",
    "RIGHTARROW": "KEY_RIGHT_ARROW",
    "HOME": "KEY_HOME",
    "END": "KEY_END",
    "PAGEUP": "KEY_PAGE_UP",
    "PAGEDOWN": "KEY_PAGE_DOWN",
    "F1": "KEY_F1",
    "F2": "KEY_F2",
    "F3": "KEY_F3",
    "F4": "KEY_F4",
    "F5": "KEY_F5",
    "F6": "KEY_F6",
    "F7": "KEY_F7",
    "F8": "KEY_F8",
    "F9": "KEY_F9",
    "F10": "KEY_F10",
    "F11": "KEY_F11",
    "F12": "KEY_F12",
}

for n in "0123456789":
    KEY_MAP[n] = f"'{n}'"

# handlers

def handle_delay(args, raw):
    global LAST_COMMAND
    LAST_COMMAND = f"delay({args[0]});"
    return LAST_COMMAND

def handle_string(args, raw):
    global LAST_COMMAND
    text = raw[len("STRING "):]
    escapedText = text.replace('\\', '\\\\').replace('"', '\\"')
    LAST_COMMAND = f'Keyboard.print("{escapedText}");'
    return LAST_COMMAND

def handle_rem(args, raw):
    return f"// {raw[4:].strip()}"

def handle_default_delay(args, raw):
    global DEFAULT_DELAY
    DEFAULT_DELAY = int(args[0])
    return f"// DEFAULT_DELAY set to {DEFAULT_DELAY}ms"

def handle_repeat(args, raw):
    global LAST_COMMAND
    if not LAST_COMMAND:
        return "// Nothing to repeat"
    try:
        times = int(args[0])
    except:
        times = 1
    return "\n".join([LAST_COMMAND] * times)

# combo key handler

def handle_combo(parts):
    cpp_lines = []
    for a in parts:
        key = a.upper()
        if key in KEY_MAP:
            cpp_lines.append(f"Keyboard.press({KEY_MAP[key]});")
        elif len(a) == 1: 
            cpp_lines.append(f"Keyboard.press('{a.lower()}');")
        else:
            cpp_lines.append(f"// Unknown key: {a}")
    cpp_lines.append("Keyboard.releaseAll();")
    return "\n".join(cpp_lines)

# command dict

COMMANDS = {
    "DELAY": handle_delay,
    "STRING": handle_string,
    "REM": handle_rem,
    "DEFAULT_DELAY": handle_default_delay,
    "REPEAT": handle_repeat,
}

# line interpreter

def interpret_line(line):
    line = line.strip()
    if not line:
        return ""

    parts = line.split()
    cmd = parts[0].upper()
    args = parts[1:]

    if cmd in COMMANDS:
        cpp = COMMANDS[cmd](args, line)
    else:
        cpp = handle_combo(parts)

    if DEFAULT_DELAY > 0 and cpp and not cpp.startswith("//"):
        cpp += f"\ndelay({DEFAULT_DELAY});"

    return cpp

# Main

def main():
    print(logo)
    parser = argparse.ArgumentParser(
        prog="Ducky2Duino",
        description="Translates DuckyScript to an Arduino C++ (Keyboard.h) payload."
    )
    parser.add_argument("input_file", help="Path to DuckyScript file")
    parser.add_argument("-o", "--output", help="Write output to a file", default=None)
    parser.add_argument("-t", "--template", action="store_true",
                        help="Wraps output in my Baduino template")
    args = parser.parse_args()

    cpp_lines = []

    with open(args.input_file, "r") as f:
        for line in f:
            cpp_lines.append(interpret_line(line))

    output_text = "\n".join(cpp_lines)
   
    if args.template:
        tabbedOutput = "\n".join(" " + line for line in output_text.splitlines())
        output_text = f"{templateHeader}\n{tabbedOutput}\n{templateFooter}"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Baduino Payload saved to {args.output}\n")
    else:
        print("Baduino Payload:\n\n")
        print(output_text)
        print(" \n")

if __name__ == "__main__":
    main()
