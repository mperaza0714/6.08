#ifndef CONTROLS_H
#define CONTROLS_H

// MARK: Buttons

constexpr int BTN_DEBOUNCE = 50;
constexpr int BTN_PRESSED = 1;
constexpr int BTN_UNPRESSED = 0;
typedef struct Button {
    int pin, state, prev_state;
    unsigned long debounce;
};
void update_button(Button &btn);
bool pullup(const Button &btn);

// MARK: Switches

constexpr int SWT_DEBOUNCE = 50;
constexpr int SWT_ON = 1;
constexpr int SWT_OFF = 0;
typedef struct Switch {
    int pin, state, prev_state;
    unsigned long debounce;
} Switch;
void update_switch(Switch &swt);
bool flipped(const Switch &swt);

// MARK: Dials, sliders, phototransistors

constexpr int ADC_BITS = 12;
constexpr int EMA_PERIOD = 50;
constexpr int DIAL_RANGE = 3;
constexpr int SLIDER_RANGE = 2;
constexpr int PHOTOT_RANGE = 10;
typedef struct SmoothControl {
    int pin;
    int range;
    double analogEma;
    int binnedReading;
} SmoothControl;
void update_control(SmoothControl &ctl);

// MARK: Convenience

Button new_button(int pin);
Switch new_switch(int pin);
SmoothControl new_dial(int pin);
SmoothControl new_slider(int pin);
SmoothControl new_photot(int pin);

#endif
