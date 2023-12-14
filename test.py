def box(lines):
    longest = len(max(lines, key=len))
    print("".join([chr(0x2554)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x2557)]))
    for x in range(len(lines)):
        print(chr(0x2551) + " " + lines[x].ljust(longest) + " " +chr(0x2551))
    print("".join([chr(0x255A)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x255D)]))

box(["test", "testing", "box", "opo"])