/*
 * Robotic Finger Servo Control
 * =============================
 * Controls a servo-actuated robotic finger for thread keeping.
 *
 * Hardware:
 *   - Arduino Uno/Nano
 *   - SG90 or MG90S micro servo motor
 *   - 10K potentiometer (optional, for manual control)
 *   - Push button (for grip/release toggle)
 *
 * Wiring:
 *   Servo signal  -> Pin 9 (PWM)
 *   Potentiometer -> A0
 *   Button        -> Pin 2 (with pull-up)
 *   Servo VCC     -> 5V (use external supply for MG90S)
 *   Servo GND     -> GND
 */

#include <Servo.h>

// --- Pin Definitions ---
#define SERVO_PIN       9
#define POT_PIN         A0
#define BUTTON_PIN      2
#define LED_PIN         13

// --- Finger Position Angles ---
#define FINGER_OPEN     10    // Fully open angle (degrees)
#define FINGER_CLOSED   160   // Fully closed/grip angle (degrees)
#define THREAD_HOLD     120   // Thread holding position (degrees)
#define FINGER_REST     45    // Rest/neutral position (degrees)

// --- Timing ---
#define SWEEP_DELAY     15    // Delay between servo steps (ms)
#define DEBOUNCE_MS     200   // Button debounce time (ms)
#define GRIP_PAUSE_MS   500   // Pause at grip position (ms)

// --- Control Modes ---
enum ControlMode {
    MODE_MANUAL,        // Potentiometer controls position
    MODE_TOGGLE,        // Button toggles open/close
    MODE_THREAD_KEEP,   // Thread keeping sequence
    MODE_SERIAL         // Serial command control
};

// --- Global State ---
Servo fingerServo;
ControlMode currentMode = MODE_SERIAL;
int currentAngle = FINGER_REST;
int targetAngle = FINGER_REST;
bool isGripping = false;
unsigned long lastButtonPress = 0;
unsigned long lastSerialCmd = 0;

// --- Thread keeping state ---
bool threadKeepActive = false;
int threadKeepStep = 0;
unsigned long threadKeepTimer = 0;

void setup() {
    Serial.begin(9600);
    Serial.println(F("=== Robotic Finger Controller ==="));
    Serial.println(F("Commands:"));
    Serial.println(F("  o - Open finger"));
    Serial.println(F("  c - Close/grip finger"));
    Serial.println(F("  t - Thread hold position"));
    Serial.println(F("  r - Rest position"));
    Serial.println(F("  k - Thread keeping sequence"));
    Serial.println(F("  m - Toggle manual (pot) mode"));
    Serial.println(F("  0-180 - Set exact angle"));
    Serial.println(F("================================"));

    fingerServo.attach(SERVO_PIN);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);

    // Move to rest position
    smoothMove(FINGER_REST);
    Serial.println(F("Ready. Finger at rest position."));
}

void loop() {
    // Check for serial commands
    handleSerialInput();

    // Check button
    handleButton();

    // Run current mode
    switch (currentMode) {
        case MODE_MANUAL:
            handleManualMode();
            break;
        case MODE_TOGGLE:
            // Handled in button interrupt
            break;
        case MODE_THREAD_KEEP:
            handleThreadKeepSequence();
            break;
        case MODE_SERIAL:
            // Handled in serial input
            break;
    }

    // Smooth movement update
    updateServoPosition();
}

/* Move servo smoothly to target angle */
void smoothMove(int target) {
    target = constrain(target, 0, 180);
    targetAngle = target;

    while (currentAngle != targetAngle) {
        if (currentAngle < targetAngle) {
            currentAngle++;
        } else {
            currentAngle--;
        }
        fingerServo.write(currentAngle);
        delay(SWEEP_DELAY);
    }
}

/* Non-blocking servo position update */
void updateServoPosition() {
    static unsigned long lastUpdate = 0;

    if (millis() - lastUpdate >= SWEEP_DELAY) {
        lastUpdate = millis();

        if (currentAngle < targetAngle) {
            currentAngle++;
            fingerServo.write(currentAngle);
        } else if (currentAngle > targetAngle) {
            currentAngle--;
            fingerServo.write(currentAngle);
        }
    }
}

/* Handle serial commands */
void handleSerialInput() {
    if (!Serial.available()) return;

    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() == 0) return;

    // Single character commands
    if (input.length() == 1) {
        switch (input.charAt(0)) {
            case 'o': case 'O':
                targetAngle = FINGER_OPEN;
                isGripping = false;
                threadKeepActive = false;
                Serial.println(F("-> Opening finger"));
                break;

            case 'c': case 'C':
                targetAngle = FINGER_CLOSED;
                isGripping = true;
                threadKeepActive = false;
                Serial.println(F("-> Closing/gripping"));
                break;

            case 't': case 'T':
                targetAngle = THREAD_HOLD;
                isGripping = true;
                threadKeepActive = false;
                Serial.println(F("-> Thread hold position"));
                break;

            case 'r': case 'R':
                targetAngle = FINGER_REST;
                isGripping = false;
                threadKeepActive = false;
                Serial.println(F("-> Rest position"));
                break;

            case 'k': case 'K':
                startThreadKeepSequence();
                break;

            case 'm': case 'M':
                if (currentMode == MODE_MANUAL) {
                    currentMode = MODE_SERIAL;
                    Serial.println(F("-> Serial control mode"));
                } else {
                    currentMode = MODE_MANUAL;
                    Serial.println(F("-> Manual (potentiometer) mode"));
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
    // Numeric angle input
    else {
        int angle = input.toInt();
        if (angle >= 0 && angle <= 180) {
            targetAngle = angle;
            threadKeepActive = false;
            Serial.print(F("-> Moving to "));
            Serial.print(angle);
            Serial.println(F(" degrees"));
        } else {
            Serial.println(F("Invalid angle. Use 0-180."));
        }
    }
}

/* Handle physical button press */
void handleButton() {
    if (digitalRead(BUTTON_PIN) == LOW) {
        if (millis() - lastButtonPress > DEBOUNCE_MS) {
            lastButtonPress = millis();

            isGripping = !isGripping;
            if (isGripping) {
                targetAngle = THREAD_HOLD;
                digitalWrite(LED_PIN, HIGH);
                Serial.println(F("[Button] Gripping thread"));
            } else {
                targetAngle = FINGER_OPEN;
                digitalWrite(LED_PIN, LOW);
                Serial.println(F("[Button] Releasing"));
            }
        }
    }
}

/* Potentiometer manual control */
void handleManualMode() {
    int potValue = analogRead(POT_PIN);
    int mappedAngle = map(potValue, 0, 1023, FINGER_OPEN, FINGER_CLOSED);

    // Only update if significant change (reduce jitter)
    if (abs(mappedAngle - targetAngle) > 2) {
        targetAngle = mappedAngle;
    }
}

/*
 * Thread Keeping Sequence
 * -----------------------
 * Automated sequence for picking up and holding thread:
 * 1. Open finger wide
 * 2. Move to thread catching position
 * 3. Close slowly to grip thread
 * 4. Hold at thread-keep tension
 * 5. Slight oscillation to maintain grip
 */
void startThreadKeepSequence() {
    threadKeepActive = true;
    threadKeepStep = 0;
    threadKeepTimer = millis();
    currentMode = MODE_THREAD_KEEP;
    Serial.println(F("-> Starting thread keep sequence"));
}

void handleThreadKeepSequence() {
    if (!threadKeepActive) return;

    unsigned long elapsed = millis() - threadKeepTimer;

    switch (threadKeepStep) {
        case 0: // Open finger
            targetAngle = FINGER_OPEN;
            if (elapsed > 1000) {
                threadKeepStep = 1;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Opening for thread..."));
            }
            break;

        case 1: // Move to catch position
            targetAngle = FINGER_REST;
            if (elapsed > 800) {
                threadKeepStep = 2;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Positioning..."));
            }
            break;

        case 2: // Slow close to grip
            targetAngle = THREAD_HOLD;
            if (elapsed > 1200) {
                threadKeepStep = 3;
                threadKeepTimer = millis();
                Serial.println(F("  [TK] Gripping thread..."));
                digitalWrite(LED_PIN, HIGH);
            }
            break;

        case 3: // Hold with micro-adjustments
            {
                // Gentle oscillation for secure grip (±3 degrees)
                int oscillation = 3 * sin(millis() / 500.0);
                targetAngle = THREAD_HOLD + oscillation;

                if (elapsed > 5000) {
                    // Settle at hold position
                    targetAngle = THREAD_HOLD;
                    threadKeepStep = 4;
                    Serial.println(F("  [TK] Thread secured. Holding."));
                }
            }
            break;

        case 4: // Steady hold - waiting for release command
            targetAngle = THREAD_HOLD;
            // Stay here until user sends another command
            break;
    }
}

/* Print current status */
void printStatus() {
    Serial.println(F("--- Status ---"));
    Serial.print(F("  Angle: "));
    Serial.print(currentAngle);
    Serial.print(F(" / Target: "));
    Serial.println(targetAngle);
    Serial.print(F("  Gripping: "));
    Serial.println(isGripping ? F("Yes") : F("No"));
    Serial.print(F("  Mode: "));
    switch (currentMode) {
        case MODE_MANUAL:      Serial.println(F("Manual")); break;
        case MODE_TOGGLE:      Serial.println(F("Toggle")); break;
        case MODE_THREAD_KEEP: Serial.println(F("Thread Keep")); break;
        case MODE_SERIAL:      Serial.println(F("Serial")); break;
    }
    Serial.print(F("  Thread Keep: "));
    Serial.println(threadKeepActive ? F("Active") : F("Inactive"));
    Serial.println(F("--------------"));
}
