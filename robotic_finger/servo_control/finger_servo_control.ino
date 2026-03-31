/*
 * Robotic Finger - Wire Tendon Servo Controller
 * ================================================
 * Controls a soft robotic finger via DUAL WIRE TENDON system:
 *   - Flexor tendon (servo pulls to close/grip)
 *   - Extensor tendon (servo releases to open via return tension)
 *
 * The servo horn spool winds/unwinds wire to actuate the finger.
 *
 * Hardware:
 *   - Arduino Uno/Nano
 *   - SG90 or MG90S micro servo motor
 *   - 0.5-0.8mm stainless steel cable / Dyneema line
 *   - Bowden cable sheath (1mm ID PTFE tube)
 *   - 10K potentiometer (optional, for manual control)
 *   - Push button (for grip/release toggle)
 *
 * Wiring:
 *   Servo signal  -> Pin 9 (PWM)
 *   Potentiometer -> A0 (optional)
 *   Button        -> Pin 2 (with internal pull-up)
 *   Servo VCC     -> 5V (external supply recommended for MG90S)
 *   Servo GND     -> GND
 *
 * Tendon Routing:
 *   Servo spool -> Bowden sheath -> Finger base entry port ->
 *   PTFE tube guides -> Pulley redirects at joints ->
 *   Wire anchor/crimp at fingertip
 */

#include <Servo.h>

// --- Pin Definitions ---
#define SERVO_PIN       9
#define POT_PIN         A0
#define BUTTON_PIN      2
#define LED_PIN         13

// --- Tendon Travel Angles ---
// These map servo rotation to wire pull distance on the spool.
// Calibrate based on your spool radius and wire wrap.
#define TENDON_FULL_SLACK   10    // Servo angle: wire fully slack (finger open)
#define TENDON_LIGHT_PULL   60    // Light tension (finger starts to curl)
#define TENDON_THREAD_GRIP  110   // Thread holding tension
#define TENDON_FULL_PULL    160   // Maximum pull (finger fully closed)
#define TENDON_REST         45    // Neutral rest tension

// --- Wire Tension Calibration ---
// Adjust these after assembly based on your wire length and spool size
#define WIRE_PRETENSION     5     // Degrees of pretension to remove slack
#define WIRE_DEADBAND       3     // Ignore angle changes smaller than this

// --- Timing ---
#define SWEEP_DELAY     12    // Delay between servo steps (ms) - smooth wire pull
#define DEBOUNCE_MS     200   // Button debounce (ms)
#define TENSION_CHECK_MS 100  // Wire tension check interval (ms)

// --- Control Modes ---
enum ControlMode {
    MODE_MANUAL,        // Potentiometer controls wire tension
    MODE_TOGGLE,        // Button toggles grip/release
    MODE_THREAD_KEEP,   // Automated thread keeping sequence
    MODE_SERIAL,        // Serial command control
    MODE_TENSION        // Constant tension hold mode
};

// --- Global State ---
Servo tendonServo;
ControlMode currentMode = MODE_SERIAL;
int currentAngle = TENDON_REST;
int targetAngle = TENDON_REST;
bool isGripping = false;
unsigned long lastButtonPress = 0;

// --- Thread keeping state ---
bool threadKeepActive = false;
int threadKeepStep = 0;
unsigned long threadKeepTimer = 0;

// --- Wire tension tracking ---
int wireTensionLevel = 0;  // 0=slack, 1=light, 2=medium, 3=full

void setup() {
    Serial.begin(9600);
    Serial.println(F("=== Wire Tendon Finger Controller ==="));
    Serial.println(F("Commands:"));
    Serial.println(F("  o - Open (release wire tension)"));
    Serial.println(F("  c - Close (full tendon pull)"));
    Serial.println(F("  t - Thread hold (medium tension)"));
    Serial.println(F("  r - Rest position (light pretension)"));
    Serial.println(F("  k - Thread keeping sequence"));
    Serial.println(F("  l - Light curl"));
    Serial.println(F("  + - Increase tension step"));
    Serial.println(F("  - - Decrease tension step"));
    Serial.println(F("  m - Toggle manual (pot) mode"));
    Serial.println(F("  ? - Show status"));
    Serial.println(F("  0-180 - Set exact servo angle"));
    Serial.println(F("========================================"));

    tendonServo.attach(SERVO_PIN);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);

    // Apply pretension to remove wire slack
    smoothMove(TENDON_REST);
    wireTensionLevel = 1;
    Serial.println(F("Ready. Wire pretensioned at rest."));
}

void loop() {
    handleSerialInput();
    handleButton();

    switch (currentMode) {
        case MODE_MANUAL:
            handleManualMode();
            break;
        case MODE_THREAD_KEEP:
            handleThreadKeepSequence();
            break;
        default:
            break;
    }

    updateServoPosition();
}

/* Smoothly wind/unwind wire to target angle */
void smoothMove(int target) {
    target = constrain(target, 0, 180);
    targetAngle = target;

    while (currentAngle != targetAngle) {
        if (currentAngle < targetAngle) {
            currentAngle++;
        } else {
            currentAngle--;
        }
        tendonServo.write(currentAngle);
        delay(SWEEP_DELAY);
    }
    updateTensionLevel();
}

/* Non-blocking servo position update */
void updateServoPosition() {
    static unsigned long lastUpdate = 0;

    if (millis() - lastUpdate >= SWEEP_DELAY) {
        lastUpdate = millis();

        if (currentAngle < targetAngle) {
            currentAngle++;
            tendonServo.write(currentAngle);
        } else if (currentAngle > targetAngle) {
            currentAngle--;
            tendonServo.write(currentAngle);
        }
    }
}

/* Track wire tension level based on servo angle */
void updateTensionLevel() {
    if (currentAngle <= TENDON_FULL_SLACK + WIRE_DEADBAND) {
        wireTensionLevel = 0;  // slack
    } else if (currentAngle <= TENDON_LIGHT_PULL) {
        wireTensionLevel = 1;  // light
    } else if (currentAngle <= TENDON_THREAD_GRIP) {
        wireTensionLevel = 2;  // medium (thread grip)
    } else {
        wireTensionLevel = 3;  // full pull
    }
    digitalWrite(LED_PIN, wireTensionLevel >= 2 ? HIGH : LOW);
}

/* Handle serial commands */
void handleSerialInput() {
    if (!Serial.available()) return;

    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() == 0) return;

    // Check if input is numeric (angle command)
    bool isNumeric = true;
    for (unsigned int i = 0; i < input.length(); i++) {
        if (!isDigit(input.charAt(i))) {
            isNumeric = false;
            break;
        }
    }

    if (isNumeric) {
        int angle = input.toInt();
        if (angle >= 0 && angle <= 180) {
            targetAngle = angle;
            threadKeepActive = false;
            currentMode = MODE_SERIAL;
            Serial.print(F("-> Spool to "));
            Serial.print(angle);
            Serial.println(F("° (wire tension change)"));
        } else {
            Serial.println(F("Invalid angle. Use 0-180."));
        }
    }
    else if (input.length() == 1) {
        switch (input.charAt(0)) {
            case 'o': case 'O':
                targetAngle = TENDON_FULL_SLACK;
                isGripping = false;
                threadKeepActive = false;
                currentMode = MODE_SERIAL;
                Serial.println(F("-> Releasing wire (finger opens)"));
                break;

            case 'c': case 'C':
                targetAngle = TENDON_FULL_PULL;
                isGripping = true;
                threadKeepActive = false;
                currentMode = MODE_SERIAL;
                Serial.println(F("-> Full pull (finger closes)"));
                break;

            case 't': case 'T':
                targetAngle = TENDON_THREAD_GRIP;
                isGripping = true;
                threadKeepActive = false;
                currentMode = MODE_SERIAL;
                Serial.println(F("-> Thread grip tension"));
                break;

            case 'r': case 'R':
                targetAngle = TENDON_REST;
                isGripping = false;
                threadKeepActive = false;
                currentMode = MODE_SERIAL;
                Serial.println(F("-> Rest (pretension only)"));
                break;

            case 'l': case 'L':
                targetAngle = TENDON_LIGHT_PULL;
                isGripping = false;
                threadKeepActive = false;
                currentMode = MODE_SERIAL;
                Serial.println(F("-> Light curl"));
                break;

            case 'k': case 'K':
                startThreadKeepSequence();
                break;

            case '+':
                targetAngle = constrain(targetAngle + 15, 0, 180);
                Serial.print(F("-> Tension +15 -> "));
                Serial.println(targetAngle);
                break;

            case '-':
                targetAngle = constrain(targetAngle - 15, 0, 180);
                Serial.print(F("-> Tension -15 -> "));
                Serial.println(targetAngle);
                break;

            case 'm': case 'M':
                if (currentMode == MODE_MANUAL) {
                    currentMode = MODE_SERIAL;
                    Serial.println(F("-> Serial control mode"));
                } else {
                    currentMode = MODE_MANUAL;
                    Serial.println(F("-> Manual (pot) mode - controls wire tension"));
                }
                break;

            case '?':
                printStatus();
                break;

            default:
                Serial.print(F("Unknown command: "));
                Serial.println(input);
                break;
        }
    }
    else {
        Serial.print(F("Invalid input: "));
        Serial.println(input);
    }
}

/* Handle physical button press */
void handleButton() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (millis() - lastButtonPress > DEBOUNCE_MS) {
            lastButtonPress = millis();

            isGripping = !isGripping;
            if (isGripping) {
                targetAngle = TENDON_THREAD_GRIP;
                Serial.println(F("[Button] Wire pull -> grip thread"));
            } else {
                targetAngle = TENDON_FULL_SLACK;
                Serial.println(F("[Button] Wire release -> open"));
            }
        }
    }
}

/* Potentiometer controls wire tension directly */
void handleManualMode() {
    int potValue = analogRead(POT_PIN);
    int mappedAngle = map(potValue, 0, 1023, TENDON_FULL_SLACK, TENDON_FULL_PULL);

    if (abs(mappedAngle - targetAngle) > WIRE_DEADBAND) {
        targetAngle = mappedAngle;
        updateTensionLevel();
    }
}

/*
 * Thread Keeping Sequence (Wire Tendon Version)
 * -----------------------------------------------
 * 1. Release wire -> finger opens fully
 * 2. Light pretension -> finger begins to curl
 * 3. Medium pull -> finger grips thread in hook
 * 4. Micro-oscillation -> ensures thread seated in grooves
 * 5. Hold steady tension
 */
void startThreadKeepSequence() {
    threadKeepActive = true;
    threadKeepStep = 0;
    threadKeepTimer = millis();
    currentMode = MODE_THREAD_KEEP;
    Serial.println(F("-> Thread keep: releasing wire..."));
}

void handleThreadKeepSequence() {
    if (!threadKeepActive) return;

    unsigned long elapsed = millis() - threadKeepTimer;

    switch (threadKeepStep) {
        case 0: // Release wire - finger opens
            targetAngle = TENDON_FULL_SLACK;
            if (elapsed > 1200) {
                threadKeepStep = 1;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Wire slack, finger open. Place thread in hook."));
            }
            break;

        case 1: // Light pretension - start curling
            targetAngle = TENDON_LIGHT_PULL;
            if (elapsed > 1000) {
                threadKeepStep = 2;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Light pull, finger curling..."));
            }
            break;

        case 2: // Medium pull - grip thread
            targetAngle = TENDON_THREAD_GRIP;
            if (elapsed > 1500) {
                threadKeepStep = 3;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Thread grip tension applied"));
                digitalWrite(LED_PIN, HIGH);
            }
            break;

        case 3: // Micro-oscillation to seat thread in grooves
            {
                int oscillation = 5 * sin(millis() / 300.0);
                targetAngle = TENDON_THREAD_GRIP + oscillation;

                if (elapsed > 3000) {
                    targetAngle = TENDON_THREAD_GRIP;
                    threadKeepStep = 4;
                    Serial.println(F("  [TK] Thread secured. Holding tension."));
                }
            }
            break;

        case 4: // Steady hold
            targetAngle = TENDON_THREAD_GRIP;
            break;
    }
}

/* Print current status */
void printStatus() {
    Serial.println(F("--- Wire Tendon Status ---"));
    Serial.print(F("  Servo angle: "));
    Serial.print(currentAngle);
    Serial.print(F("° / Target: "));
    Serial.print(targetAngle);
    Serial.println(F("°"));

    Serial.print(F("  Wire tension: "));
    switch (wireTensionLevel) {
        case 0: Serial.println(F("SLACK (open)")); break;
        case 1: Serial.println(F("LIGHT (pretension)")); break;
        case 2: Serial.println(F("MEDIUM (thread grip)")); break;
        case 3: Serial.println(F("FULL (max curl)")); break;
    }

    Serial.print(F("  Gripping: "));
    Serial.println(isGripping ? F("Yes") : F("No"));

    Serial.print(F("  Mode: "));
    switch (currentMode) {
        case MODE_MANUAL:      Serial.println(F("Manual (pot)")); break;
        case MODE_TOGGLE:      Serial.println(F("Toggle")); break;
        case MODE_THREAD_KEEP: Serial.println(F("Thread Keep")); break;
        case MODE_SERIAL:      Serial.println(F("Serial")); break;
        case MODE_TENSION:     Serial.println(F("Tension hold")); break;
    }

    Serial.print(F("  Thread keep: "));
    Serial.println(threadKeepActive ? F("Active") : F("Inactive"));

    Serial.println(F("  Wire routing: Spool -> Bowden -> Base -> PTFE guides -> Pulleys -> Anchor"));
    Serial.println(F("--------------------------"));
}
