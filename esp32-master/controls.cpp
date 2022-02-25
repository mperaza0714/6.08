#include "controls.h"
#include "map_range.h"
#include <math.h>
#include <mpu6050_esp32.h>

// MARK: Buttons

void update_button(Button &btn)
{
    btn.prev_state = btn.state;
    btn.state = 1 - digitalRead(btn.pin);
    if (btn.prev_state == BTN_UNPRESSED && btn.state == BTN_PRESSED &&
        millis() - btn.debounce > BTN_DEBOUNCE) {
        btn.debounce = millis();
    }
}

bool pullup(const Button &btn)
{
    return btn.state == BTN_UNPRESSED && btn.prev_state == BTN_PRESSED &&
           millis() - btn.debounce > BTN_DEBOUNCE;
}

// MARK: Switches

void update_switch(Switch &swt)
{
    int reading = 1 - digitalRead(swt.pin);
    if (millis() - swt.debounce > SWT_DEBOUNCE && reading != swt.prev_state) {
        swt.debounce = millis();
        swt.prev_state = swt.state;
        swt.state = reading;
    }
}

bool flipped(const Switch &swt)
{
    return swt.state != swt.prev_state &&
           millis() - swt.debounce > SWT_DEBOUNCE;
}

// MARK: Dials, sliders, phototransistors

void update_control(SmoothControl &ctl)
{
    int reading = analogRead(ctl.pin);
    ctl.analogEma *= (EMA_PERIOD - 1) / (double)EMA_PERIOD;
    ctl.analogEma += reading / (double)EMA_PERIOD;
    ctl.binnedReading = map_range(ctl.analogEma, ADC_BITS, ctl.range);
}

// MARK: Convenience

Button new_button(int pin) { return {pin}; };
Switch new_switch(int pin) { return {pin}; };
SmoothControl new_dial(int pin) { return {pin, DIAL_RANGE}; }
SmoothControl new_slider(int pin) { return {pin, SLIDER_RANGE}; }
SmoothControl new_photot(int pin) { return {pin, PHOTOT_RANGE}; }
