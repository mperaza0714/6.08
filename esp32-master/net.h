#ifndef NET_H
#define NET_H
#include <string>

constexpr int RESPONSE_TIMEOUT = 1000;
static const char network[] = "FIXME";
static const char password[] = "FIXME";

void wifi_setup();
void http_req(const char *host, char *request, char *response,
              int response_size);
#endif
