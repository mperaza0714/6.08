#include "map_range.h"
#include <math.h>

int map_range(double value, int in_bits, int out_range)
{
    double pct = value / (pow(2, in_bits) - 1.0);
    return lround(pct * out_range);
}
