"""
Robotic Finger - Wire Tendon Servo Controller (Python)
=======================================================
Controls a soft robotic finger via dual wire tendon system.

The servo horn has a spool that winds/unwinds stainless steel cable
through Bowden sheaths and PTFE tube guides to curl/extend the finger.

Usage:
  python finger_servo_control.py --mode gpio     # Direct Raspberry Pi GPIO
  python finger_servo_control.py --mode serial   # Arduino via USB serial
  python finger_servo_control.py --mode serial --port /dev/ttyUSB0
"""

import argparse
import time
import sys
import math

# --- Wire Tendon Angle Mapping ---
# Servo angle controls spool rotation = wire pull distance
TENDON_FULL_SLACK   = 10    # Wire slack, finger fully open
TENDON_LIGHT_PULL   = 60    # Light tension, finger starts curling
TENDON_THREAD_GRIP  = 110   # Thread holding tension
TENDON_FULL_PULL    = 160   # Max pull, finger fully closed
TENDON_REST         = 45    # Pretensioned rest position

# --- Config ---
SERVO_PIN    = 18
SWEEP_DELAY  = 0.012
SERIAL_BAUD  = 9600
WIRE_DEADBAND = 3


class TendonController:
    """Base class for wire tendon servo control."""

    TENSION_NAMES = {0: "SLACK", 1: "LIGHT", 2: "MEDIUM", 3: "FULL"}

    def __init__(self):
        self.current_angle = TENDON_REST
        self.is_gripping = False
        self.tension_level = 1

    def set_angle(self, angle):
        raise NotImplementedError

    def _update_tension(self):
        if self.current_angle <= TENDON_FULL_SLACK + WIRE_DEADBAND:
            self.tension_level = 0
        elif self.current_angle <= TENDON_LIGHT_PULL:
            self.tension_level = 1
        elif self.current_angle <= TENDON_THREAD_GRIP:
            self.tension_level = 2
        else:
            self.tension_level = 3

    def smooth_move(self, target_angle):
        target_angle = max(0, min(180, target_angle))
        step = 1 if target_angle > self.current_angle else -1

        while self.current_angle != target_angle:
            self.current_angle += step
            self.set_angle(self.current_angle)
            time.sleep(SWEEP_DELAY)

        self._update_tension()
        print(f"  Spool at {self.current_angle}° | Tension: {self.TENSION_NAMES[self.tension_level]}")

    def release_wire(self):
        print("Releasing wire (finger opens)...")
        self.smooth_move(TENDON_FULL_SLACK)
        self.is_gripping = False

    def full_pull(self):
        print("Full wire pull (finger closes)...")
        self.smooth_move(TENDON_FULL_PULL)
        self.is_gripping = True

    def thread_grip(self):
        print("Thread grip tension...")
        self.smooth_move(TENDON_THREAD_GRIP)
        self.is_gripping = True

    def light_curl(self):
        print("Light curl...")
        self.smooth_move(TENDON_LIGHT_PULL)
        self.is_gripping = False

    def rest_tension(self):
        print("Rest pretension...")
        self.smooth_move(TENDON_REST)
        self.is_gripping = False

    def thread_keep_sequence(self):
        """
        Wire tendon thread keeping sequence:
        1. Release wire -> finger opens fully
        2. Light pull -> finger starts curling
        3. Medium pull -> thread grip tension
        4. Oscillation -> seat thread in guide grooves
        5. Hold steady
        """
        print("Wire Tendon Thread Keep Sequence")
        print("================================")

        print("  [1/5] Releasing wire - finger opens...")
        self.smooth_move(TENDON_FULL_SLACK)
        time.sleep(1.2)

        print("  [2/5] Light pretension - begin curl...")
        self.smooth_move(TENDON_LIGHT_PULL)
        time.sleep(1.0)

        print("  [3/5] Thread grip tension - closing on thread...")
        self.smooth_move(TENDON_THREAD_GRIP)
        time.sleep(0.5)

        print("  [4/5] Oscillating to seat thread in grooves...")
        start = time.time()
        while time.time() - start < 3.0:
            oscillation = int(5 * math.sin(time.time() * 3))
            self.set_angle(TENDON_THREAD_GRIP + oscillation)
            time.sleep(0.05)

        print("  [5/5] Holding steady tension.")
        self.set_angle(TENDON_THREAD_GRIP)
        self.current_angle = TENDON_THREAD_GRIP
        self.is_gripping = True
        self._update_tension()
        print("  Thread secured!")

    def increase_tension(self, step=15):
        new_angle = min(180, self.current_angle + step)
        print(f"Tension +{step}...")
        self.smooth_move(new_angle)

    def decrease_tension(self, step=15):
        new_angle = max(0, self.current_angle - step)
        print(f"Tension -{step}...")
        self.smooth_move(new_angle)

    def status(self):
        self._update_tension()
        print(f"--- Wire Tendon Status ---")
        print(f"  Servo: {self.current_angle}° | Tension: {self.TENSION_NAMES[self.tension_level]}")
        print(f"  Gripping: {'Yes' if self.is_gripping else 'No'}")
        print(f"  Route: Spool -> Bowden -> Base -> PTFE guides -> Pulleys -> Anchor")
        print(f"--------------------------")

    def cleanup(self):
        pass


class GPIOTendonController(TendonController):
    """Raspberry Pi GPIO control."""

    def __init__(self):
        super().__init__()
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(SERVO_PIN, GPIO.OUT)
            self.pwm = GPIO.PWM(SERVO_PIN, 50)
            self.pwm.start(self._angle_to_duty(TENDON_REST))
            print(f"GPIO servo on pin {SERVO_PIN}")
        except ImportError:
            print("ERROR: RPi.GPIO not available. Use --mode serial.")
            sys.exit(1)

    @staticmethod
    def _angle_to_duty(angle):
        return 2.5 + (angle / 180.0) * 10.0

    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        self.current_angle = angle
        self.pwm.ChangeDutyCycle(self._angle_to_duty(angle))

    def cleanup(self):
        self.pwm.stop()
        self.GPIO.cleanup()
        print("GPIO cleaned up.")


class SerialTendonController(TendonController):
    """Arduino serial control."""

    def __init__(self, port="/dev/ttyUSB0", baud=SERIAL_BAUD):
        super().__init__()
        try:
            import serial
            self.ser = serial.Serial(port, baud, timeout=2)
            time.sleep(2)
            while self.ser.in_waiting:
                print(f"  Arduino: {self.ser.readline().decode().strip()}")
            print(f"Serial connected: {port} @ {baud}")
        except ImportError:
            print("ERROR: pip install pyserial")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    def _send(self, cmd):
        self.ser.write(f"{cmd}\n".encode())
        time.sleep(0.1)
        while self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            if line:
                print(f"  Arduino: {line}")

    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        self.current_angle = angle
        self._send(str(angle))

    def smooth_move(self, target_angle):
        self._send(str(target_angle))
        self.current_angle = target_angle
        self._update_tension()

    def release_wire(self):
        print("Releasing wire...")
        self._send("o")
        self.is_gripping = False

    def full_pull(self):
        print("Full pull...")
        self._send("c")
        self.is_gripping = True

    def thread_grip(self):
        print("Thread grip...")
        self._send("t")
        self.is_gripping = True

    def rest_tension(self):
        print("Rest tension...")
        self._send("r")
        self.is_gripping = False

    def light_curl(self):
        print("Light curl...")
        self._send("l")
        self.is_gripping = False

    def thread_keep_sequence(self):
        print("Thread keep sequence...")
        self._send("k")
        time.sleep(8)
        while self.ser.in_waiting:
            line = self.ser.readline().decode().strip()
            if line:
                print(f"  Arduino: {line}")
        self.is_gripping = True

    def increase_tension(self, step=15):
        self._send("+")

    def decrease_tension(self, step=15):
        self._send("-")

    def cleanup(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            print("Serial closed.")


def interactive_control(ctrl):
    print("\n=== Wire Tendon Finger Control ===")
    print("Commands:")
    print("  o       - Release wire (open)")
    print("  c       - Full pull (close)")
    print("  t       - Thread grip tension")
    print("  l       - Light curl")
    print("  r       - Rest pretension")
    print("  k       - Thread keep sequence")
    print("  +/-     - Adjust tension ±15°")
    print("  0-180   - Set exact spool angle")
    print("  ?       - Status")
    print("  q       - Quit")
    print("==================================\n")

    while True:
        try:
            cmd = input("tendon> ").strip().lower()

            if not cmd:
                continue
            elif cmd == 'q':
                print("Releasing wire and shutting down...")
                ctrl.rest_tension()
                break
            elif cmd == 'o':
                ctrl.release_wire()
            elif cmd == 'c':
                ctrl.full_pull()
            elif cmd == 't':
                ctrl.thread_grip()
            elif cmd == 'l':
                ctrl.light_curl()
            elif cmd == 'r':
                ctrl.rest_tension()
            elif cmd == 'k':
                ctrl.thread_keep_sequence()
            elif cmd == '+':
                ctrl.increase_tension()
            elif cmd == '-':
                ctrl.decrease_tension()
            elif cmd == '?':
                ctrl.status()
            else:
                try:
                    angle = int(cmd)
                    if 0 <= angle <= 180:
                        ctrl.smooth_move(angle)
                    else:
                        print("Angle must be 0-180")
                except ValueError:
                    print(f"Unknown: {cmd}")

        except KeyboardInterrupt:
            print("\nReleasing wire...")
            ctrl.rest_tension()
            break
        except EOFError:
            break

    ctrl.cleanup()


def main():
    parser = argparse.ArgumentParser(description="Wire Tendon Finger Controller")
    parser.add_argument("--mode", choices=["gpio", "serial"], default="serial")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=SERIAL_BAUD)
    args = parser.parse_args()

    if args.mode == "gpio":
        ctrl = GPIOTendonController()
    else:
        ctrl = SerialTendonController(port=args.port, baud=args.baud)

    interactive_control(ctrl)


if __name__ == "__main__":
    main()
