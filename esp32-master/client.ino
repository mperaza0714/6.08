#include "controls.h"
#include "net.h"
#include <SPI.h>
#include <TFT_eSPI.h>
#include <math.h>
#include <mpu6050_esp32.h>
#include <vector>

TFT_eSPI tft = TFT_eSPI();

// MARK: Client state

enum class ClState { Idle, Waiting, Playing };
ClState clState = ClState::Idle;
int game_id = 0;
int game_id_digit = 10;
int game_id_pos = 0;
char username[256];
unsigned long game_start_time;

// MARK: Network

const uint16_t IN_BUFFER_SIZE = 1000;
const uint16_t OUT_BUFFER_SIZE = 1000;
const size_t BODY_BUFFER_SIZE = 512;
char request_buffer[IN_BUFFER_SIZE];
char response_buffer[OUT_BUFFER_SIZE];
char body[BODY_BUFFER_SIZE];
char cur_instruction[BODY_BUFFER_SIZE];

// MARK: Inputs

constexpr int BUTTON_P1[] = {33, 25, 26, 27};
constexpr int BUTTON_P2[] = {14, 12, 13, 0};
constexpr int SWITCH_PINS[] = {32};
constexpr int DIAL_PINS[] = {34};
constexpr int PHOTOT_PINS[] = {39, 35};
constexpr int SLIDER_PINS[] = {36};

std::vector<Button> panel1;
std::vector<Button> panel2;
std::vector<Switch> switches;
std::vector<SmoothControl> dials;
std::vector<SmoothControl> photots;
std::vector<SmoothControl> sliders;
MPU6050 imu;
int IMU_EMA_PERIOD = 10;
double imu_accel_ema = 0;

int get_panel_out(std::vector<Button> panel)
{
    int i = 0;
    for (auto &btn : panel) {
        i++;
        if (btn.state == BTN_PRESSED)
            return i;
    }
    return 0;
}

double norm(double x1, double x2) { return sqrt(powf(x1, 2) + powf(x2, 2)); }

void post_states()
{
    strcpy(body, "");
    snprintf(body, BODY_BUFFER_SIZE, "%sbutton_panel_1=%d&", body,
             get_panel_out(panel1));
    snprintf(body, BODY_BUFFER_SIZE, "%sbutton_panel_2=%d&", body,
             get_panel_out(panel2));
    int i = 1;
    for (auto &swt : switches) {
        snprintf(body, BODY_BUFFER_SIZE, "%sswitch_%d=%d&", body, i, swt.state);
        i++;
    }
    i = 1;
    for (auto &dial : dials) {
        snprintf(body, BODY_BUFFER_SIZE, "%sdial_%d=%d&", body, i,
                 dial.binnedReading + 1);
        i++;
    }
    i = 1;
    for (auto &photot : photots) {
        snprintf(body, BODY_BUFFER_SIZE, "%sphototransistor_%d=%d&", body, i,
                 photot.binnedReading > 7);
        i++;
    }
    i = 1;
    for (auto &slider : sliders) {
        snprintf(body, BODY_BUFFER_SIZE, "%sslider_%d=%d&", body, i,
                 slider.binnedReading + 1);
        i++;
    }
    snprintf(body, BODY_BUFFER_SIZE, "%simu_1=%d", body, imu_accel_ema > 0.5);
    Serial.println(body);
    post_request(body);
}

void setup()
{
    Serial.begin(115200);
    tft.init();
    tft.setRotation(0);
    tft.setTextSize(1);
    tft.fillScreen(TFT_BLACK);
    wifi_setup();
    imu.setupIMU(1);

    for (auto p : BUTTON_P1) {
        pinMode(p, INPUT_PULLUP);
        panel1.push_back(new_button(p));
    }
    for (auto p : BUTTON_P2) {
        pinMode(p, INPUT_PULLUP);
        panel2.push_back(new_button(p));
    }
    for (auto p : DIAL_PINS) {
        pinMode(p, INPUT);
        dials.push_back(new_dial(p));
    }
    for (auto p : PHOTOT_PINS) {
        pinMode(p, INPUT);
        photots.push_back(new_photot(p));
    }
    for (auto p : SWITCH_PINS) {
        pinMode(p, INPUT_PULLUP);
        switches.push_back(new_switch(p));
    }
    for (auto p : SLIDER_PINS) {
        pinMode(p, INPUT);
        sliders.push_back(new_slider(p));
    }
}

void update_controls()
{
    for (auto &btn : panel1)
        update_button(btn);
    for (auto &btn : panel2)
        update_button(btn);
    for (auto &swt : switches)
        update_switch(swt);
    for (auto &dial : dials)
        update_control(dial);
    for (auto &photot : photots)
        update_control(photot);
    for (auto &slider : sliders)
        update_control(slider);
    imu.readAccelData(imu.accelCount);
    double imu_norm =
        norm(imu.accelCount[0] * imu.aRes, imu.accelCount[1] * imu.aRes);
    imu_accel_ema *= 1 - 1.0 / IMU_EMA_PERIOD;
    imu_accel_ema += imu_norm * 1.0 / IMU_EMA_PERIOD;
}

void fsm()
{
    if (clState == ClState::Idle) {
        if (pullup(panel1[0])) {
            game_id_digit = ++game_id_digit % 11;
        }
        else if (pullup(panel1[1]) &&
                 !(game_id_pos == 0 && game_id_digit == 10)) {
            tft.drawLine((9 + game_id_pos) * 6, 8, (10 + game_id_pos) * 6 - 1,
                         8, TFT_BLACK);
            game_id_pos++;
            if (game_id_digit == 10) {
                post_join(game_id);
                clState = ClState::Waiting;
                tft.fillScreen(TFT_BLACK);
                game_start_time = millis() + 15000;
                return;
            }
            else {
                game_id = game_id * 10 + game_id_digit;
                game_id_digit = 10;
            }
        }

        tft.setCursor(0, 0, 1);

        if (game_id_pos > 0)
            tft.printf("Game ID: %d", game_id);
        else
            tft.print("Game ID: ");
        if (game_id_digit == 10)
            tft.print(" ");
        else
            tft.print(game_id_digit);

        tft.drawLine((9 + game_id_pos) * 6, 8, (10 + game_id_pos) * 6 - 1, 8,
                     TFT_WHITE);
    }
    else if (clState == ClState::Waiting) {
        tft.setCursor(0, 0, 1);
        tft.printf("Username: %s\n", username);
        if (millis() % 1000 < 333)
            tft.println("Waiting for\nplayers.  ");
        else if (millis() % 1000 < 666)
            tft.println("Waiting for\nplayers . ");
        else
            tft.println("Waiting for\nplayers  .");

        if (millis() >= game_start_time)
            clState = ClState::Playing;
    }
    else if (clState == ClState::Playing) {
        if (millis() % 1000 == 0) {
            get_instruction(username, cur_instruction);
            post_states();
        }
    }
}

void loop()
{
    update_controls();
    fsm();
}

void post_request(char *body)
{
    snprintf(body, BODY_BUFFER_SIZE, "%s&user=%s", body, username);
    int body_len = strlen(body);
    sprintf(request_buffer, "POST "
                            "http://608dev-2.net/sandbox/sc/team076/spaceteam/"
                            "update_instructions.py HTTP/1.1\r\n");
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer,
           "Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n",
            body_len);
    strcat(request_buffer, "\r\n");
    strcat(request_buffer, body);
    http_req("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE);
}

void get_instruction(char *username, char *cur_instruction)
{
    sprintf(request_buffer,
            "GET "
            "http://608dev-2.net/sandbox/sc/team076/spaceteam/"
            "instruction_request.py?user=%s HTTP/1.1\r\n",
            username);
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer, "\r\n"); // add blank line!
    http_req("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE);

    if (strcmp(response_buffer, cur_instruction) != 0) {
        tft.fillScreen(TFT_BLACK);
        tft.setCursor(0, 0, 1);
        tft.println("Instruction:");
        tft.println(response_buffer);
    }

    memset(cur_instruction, 0, OUT_BUFFER_SIZE);
    sprintf(cur_instruction, response_buffer);
}

void post_join(int game_id)
{
    sprintf(body, "game_id=%d", game_id);
    int body_len = strlen(body); // calculate body length (for header reporting)
    sprintf(request_buffer,
            "POST http://608dev-2.net/sandbox/sc/team076/spaceteam/new_game.py "
            "HTTP/1.1\r\n");
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer,
           "Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n",
            body_len); // append string formatted to end of request buffer
    strcat(request_buffer, "\r\n"); // new line from header to body
    strcat(request_buffer, body);   // body
    strcat(request_buffer, "\r\n"); // header
    http_req("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE);
    Serial.println(response_buffer);
    strncpy(username, response_buffer, strlen(response_buffer) - 1);
}
