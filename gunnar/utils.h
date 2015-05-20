#ifndef UITLS_H
#define UTILS_H
#include <math.h>
#include <Arduino.h>

void interruptibleDelay(float ms)
{
    // Replace delay(ms) with multiple delayMicroseconds(...), so interrupts still work.
    const int maxDelay = 16383; // delayMicroseconds is only accurate up to this long (and down to ~3 uS).
    
    int nreps = floor(ms*1000 / maxDelay);
    
    // First, delay the remainder. For small ms, the function could stop here.
    delayMicroseconds(fmod(ms*1000, maxDelay));

    // Delay the necessary remaining repetitions of maxDelay.
    for(uint8_t i=0; i<nreps; i++)
    {
        delayMicroseconds(maxDelay);
    }    
}

float average(float* values, int N)
{
    float val = 0;
    for(int i=0; i<N; i++)
    {
        val += values[i];
    }
    val /= (float) N;
    return val;
}

double average(double* values, int N)
{
    double val = 0;
    for(int i=0; i<N; i++)
    {
        val += values[i];
    }
    val /= (double) N;
    return val;
}

long millisViaMicros()
{
    //Apparently millis() can be bad with interrupts.
    return ((long) micros() / 1000L);
}

void rotateArray(double *arr, int n)
{
    // Assume n>1
//     Serial.print("rotate arr: [");
    double first = arr[0];
    for(int i=0; i<n-1; i++)
    {
//         Serial.print(arr[i]);
//         Serial.print(",");
        arr[i] = arr[i+1];
    }
//     Serial.print(arr[n-1]);
//     Serial.println("]");
    arr[n-1] = first;
}

#endif