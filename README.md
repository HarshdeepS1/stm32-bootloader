# STM32 Bootloader + HIL Test Framework

A bare-metal bootloader for the STM32F446RE that receives firmware 
over UART using the XMODEM protocol and flashes it safely.

## Hardware
- NUCLEO-F446RE development board

## Projects
- `bootloader/` — bare-metal bootloader firmware
- `app/` — test application firmware  
- `host-tools/` — Python scripts for sending firmware over UART

## Progress
- [x] Phase 0: Toolchain setup, LED blink, UART hello world
- [x] Phase 1: Memory layout, linker scripts, bootloader jump
- [x] Phase 2: XMODEM receive protocol
- [ ] Phase 3: Flash write + CRC verification
- [ ] Phase 4: HIL test harness
- [ ] Phase 5: Integration and polish

## Usage
Flash `bootloader` to the STM32, hold the blue button on reset 
to enter update mode, then run:
```
cd host-tools
python xmodem_send.py
```