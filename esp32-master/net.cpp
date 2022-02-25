#include "net.h"
#include <TFT_eSPI.h>
#include <WiFi.h>
#include <mpu6050_esp32.h>
#include <string>

void wifi_setup()
{
    WiFi.begin(network, password);
    Serial.printf("Connecting to %s...\n", network);
    while (WiFi.status() != WL_CONNECTED)
        ;
    Serial.println("Connected.");
}

uint8_t char_append(char *buff, char c, uint16_t buff_size)
{
    int len = strlen(buff);
    if (len > buff_size)
        return false;
    buff[len] = c;
    buff[len + 1] = '\0';
    return true;
}

void http_req(const char *host, char *request, char *response,
              int response_size)
{
    WiFiClient client;
    if (client.connect(host, 80)) {
        client.print(request);
        memset(response, 0, response_size);
        uint32_t count = millis();
        while (true) {
            client.readBytesUntil('\n', response, response_size);
            if (strcmp(response, "\r") == 0)
                break;
            memset(response, 0, response_size);
            if (millis() - count > RESPONSE_TIMEOUT)
                break;
        }
        strcpy(response, "");
        count = millis();
        while (client.available()) {
            char_append(response, client.read(), response_size);
        }
        client.stop();
    }
    else
        client.stop();
}
